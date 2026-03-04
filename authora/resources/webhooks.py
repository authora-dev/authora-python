from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import AsyncHttpClient, SyncHttpClient
from ..types import PaginatedList, Webhook


class WebhooksResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        organization_id: str,
        url: str,
        event_types: List[str],
        secret: str,
    ) -> Webhook:
        body: Dict[str, Any] = {
            "organization_id": organization_id,
            "url": url,
            "event_types": event_types,
            "secret": secret,
        }
        data = self._http.post("/webhooks", body=body)
        return Webhook.from_dict(data)

    def list(self, *, organization_id: str) -> PaginatedList[Webhook]:
        query: Dict[str, Any] = {"organization_id": organization_id}
        data = self._http.get("/webhooks", query=query)
        return PaginatedList.from_dict(data, Webhook)

    def update(
        self,
        webhook_id: str,
        *,
        url: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        secret: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> Webhook:
        body: Dict[str, Any] = {}
        if url is not None:
            body["url"] = url
        if event_types is not None:
            body["event_types"] = event_types
        if secret is not None:
            body["secret"] = secret
        if enabled is not None:
            body["enabled"] = enabled
        data = self._http.patch(f"/webhooks/{webhook_id}", body=body)
        return Webhook.from_dict(data)

    def delete(self, webhook_id: str) -> None:
        self._http.delete(f"/webhooks/{webhook_id}")


class AsyncWebhooksResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        organization_id: str,
        url: str,
        event_types: List[str],
        secret: str,
    ) -> Webhook:
        body: Dict[str, Any] = {
            "organization_id": organization_id,
            "url": url,
            "event_types": event_types,
            "secret": secret,
        }
        data = await self._http.post("/webhooks", body=body)
        return Webhook.from_dict(data)

    async def list(self, *, organization_id: str) -> PaginatedList[Webhook]:
        query: Dict[str, Any] = {"organization_id": organization_id}
        data = await self._http.get("/webhooks", query=query)
        return PaginatedList.from_dict(data, Webhook)

    async def update(
        self,
        webhook_id: str,
        *,
        url: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        secret: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> Webhook:
        body: Dict[str, Any] = {}
        if url is not None:
            body["url"] = url
        if event_types is not None:
            body["event_types"] = event_types
        if secret is not None:
            body["secret"] = secret
        if enabled is not None:
            body["enabled"] = enabled
        data = await self._http.patch(f"/webhooks/{webhook_id}", body=body)
        return Webhook.from_dict(data)

    async def delete(self, webhook_id: str) -> None:
        await self._http.delete(f"/webhooks/{webhook_id}")
