from __future__ import annotations

import json
from typing import Any
from urllib import error, request

from nba.domain.models import CandidateAction, CustomerContext
from nba.ml.features import build_feature_row


class AzureMLPropensityModel:
    """Propensity model backed by an Azure ML managed online endpoint.

    The endpoint is expected to use Microsoft Entra ``aad_token`` authentication.
    The caller therefore needs the Azure ML ``score/action`` permission on the
    endpoint. No static API key is stored by this adapter.
    """

    def __init__(
        self,
        scoring_uri: str,
        version: str = "azureml-managed-endpoint",
        credential: Any | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        if not scoring_uri.startswith("https://"):
            raise ValueError("Azure ML scoring URI must use HTTPS")
        self.scoring_uri = scoring_uri
        self.version = version
        self.timeout_seconds = timeout_seconds
        self._credential = credential

    def _get_credential(self) -> Any:
        if self._credential is not None:
            return self._credential
        try:
            from azure.identity import DefaultAzureCredential
        except ImportError as exc:  # pragma: no cover - depends on optional cloud extra
            raise RuntimeError("Install the 'azure' extra to use Azure ML inference") from exc
        self._credential = DefaultAzureCredential()
        return self._credential

    def predict(self, customer: CustomerContext, action: CandidateAction) -> float:
        feature_row = build_feature_row(customer, action).iloc[0].to_dict()
        payload = json.dumps({"input_data": [feature_row]}).encode("utf-8")
        token = self._get_credential().get_token("https://ml.azure.com/.default").token
        req = request.Request(
            self.scoring_uri,
            data=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:  # noqa: S310
                body = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Azure ML scoring failed ({exc.code}): {detail}") from exc
        probabilities = body.get("probabilities")
        if not isinstance(probabilities, list) or len(probabilities) != 1:
            raise RuntimeError("Azure ML response did not contain one probability")
        return float(probabilities[0])
