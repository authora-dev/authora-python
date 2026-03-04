from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import AsyncHttpClient, SyncHttpClient
from ..types import Alert, PaginatedList


class AlertsResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        organization_id: str,
        name: str,
        event_types: List[str],
        conditions: Dict[str, Any],
        channels: List[Dict[str, Any]],
    ) -> Alert:
        body: Dict[str, Any] = {
            "organization_id": organization_id,
            "name": name,
            "event_types": event_types,
            "conditions": conditions,
            "channels": channels,
        }
        data = self._http.post("/alerts", body=body)
        return Alert.from_dict(data)

    def list(self, *, organization_id: str) -> PaginatedList[Alert]:
        query: Dict[str, Any] = {"organization_id": organization_id}
        data = self._http.get("/alerts", query=query)
        return PaginatedList.from_dict(data, Alert)

    def update(
        self,
        alert_id: str,
        *,
        name: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        conditions: Optional[Dict[str, Any]] = None,
        channels: Optional[List[Dict[str, Any]]] = None,
        enabled: Optional[bool] = None,
    ) -> Alert:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if event_types is not None:
            body["event_types"] = event_types
        if conditions is not None:
            body["conditions"] = conditions
        if channels is not None:
            body["channels"] = channels
        if enabled is not None:
            body["enabled"] = enabled
        data = self._http.patch(f"/alerts/{alert_id}", body=body)
        return Alert.from_dict(data)

    def delete(self, alert_id: str) -> None:
        self._http.delete(f"/alerts/{alert_id}")


class AsyncAlertsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        organization_id: str,
        name: str,
        event_types: List[str],
        conditions: Dict[str, Any],
        channels: List[Dict[str, Any]],
    ) -> Alert:
        body: Dict[str, Any] = {
            "organization_id": organization_id,
            "name": name,
            "event_types": event_types,
            "conditions": conditions,
            "channels": channels,
        }
        data = await self._http.post("/alerts", body=body)
        return Alert.from_dict(data)

    async def list(self, *, organization_id: str) -> PaginatedList[Alert]:
        query: Dict[str, Any] = {"organization_id": organization_id}
        data = await self._http.get("/alerts", query=query)
        return PaginatedList.from_dict(data, Alert)

    async def update(
        self,
        alert_id: str,
        *,
        name: Optional[str] = None,
        event_types: Optional[List[str]] = None,
        conditions: Optional[Dict[str, Any]] = None,
        channels: Optional[List[Dict[str, Any]]] = None,
        enabled: Optional[bool] = None,
    ) -> Alert:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if event_types is not None:
            body["event_types"] = event_types
        if conditions is not None:
            body["conditions"] = conditions
        if channels is not None:
            body["channels"] = channels
        if enabled is not None:
            body["enabled"] = enabled
        data = await self._http.patch(f"/alerts/{alert_id}", body=body)
        return Alert.from_dict(data)

    async def delete(self, alert_id: str) -> None:
        await self._http.delete(f"/alerts/{alert_id}")
