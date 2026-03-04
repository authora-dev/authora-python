from __future__ import annotations

from typing import Any, Callable, Dict, Iterator, Optional

import httpx

from .._http import AsyncHttpClient, SyncHttpClient
from ..types import AuditEvent, AuditMetrics, AuditReport, PaginatedList


class AuditResource:
    def __init__(self, http: SyncHttpClient, base_url: str = "", api_key: str = "") -> None:
        self._http = http
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key

    def list_events(
        self,
        *,
        org_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        type: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        resource: Optional[str] = None,
        result: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> PaginatedList[AuditEvent]:
        query: Dict[str, Any] = {}
        if org_id is not None:
            query["org_id"] = org_id
        if workspace_id is not None:
            query["workspace_id"] = workspace_id
        if agent_id is not None:
            query["agent_id"] = agent_id
        if type is not None:
            query["type"] = type
        if date_from is not None:
            query["date_from"] = date_from
        if date_to is not None:
            query["date_to"] = date_to
        if resource is not None:
            query["resource"] = resource
        if result is not None:
            query["result"] = result
        if page is not None:
            query["page"] = page
        if limit is not None:
            query["limit"] = limit

        data = self._http.get("/audit/events", query=query if query else None)
        return PaginatedList.from_dict(data, AuditEvent)

    def get_event(self, event_id: str) -> AuditEvent:
        data = self._http.get(f"/audit/events/{event_id}")
        return AuditEvent.from_dict(data)

    def generate_report(
        self,
        *,
        org_id: str,
        date_from: str,
        date_to: str,
    ) -> AuditReport:
        body: Dict[str, Any] = {
            "org_id": org_id,
            "date_from": date_from,
            "date_to": date_to,
        }
        data = self._http.post("/audit/reports", body=body)
        return AuditReport.from_dict(data)

    def get_metrics(
        self,
        *,
        org_id: str,
        workspace_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> AuditMetrics:
        query: Dict[str, Any] = {"org_id": org_id}
        if workspace_id is not None:
            query["workspace_id"] = workspace_id
        if agent_id is not None:
            query["agent_id"] = agent_id
        if date_from is not None:
            query["date_from"] = date_from
        if date_to is not None:
            query["date_to"] = date_to

        data = self._http.get("/audit/metrics", query=query)
        return AuditMetrics.from_dict(data)

    def stream_events(self) -> Iterator[AuditEvent]:
        import json

        url = f"{self._base_url}/audit/stream"
        headers = {
            "Accept": "text/event-stream",
            "Authorization": f"Bearer {self._api_key}",
        }
        with httpx.stream("GET", url, headers=headers, timeout=None) as resp:
            resp.raise_for_status()
            event_type = ""
            data = ""
            for line in resp.iter_lines():
                if line.startswith("event: "):
                    event_type = line[7:].strip()
                elif line.startswith("data: "):
                    data = line[6:]
                elif line == "" and data:
                    if event_type == "audit":
                        try:
                            yield AuditEvent.from_dict(json.loads(data))
                        except Exception:
                            pass
                    event_type = ""
                    data = ""


class AsyncAuditResource:
    def __init__(self, http: AsyncHttpClient, base_url: str = "", api_key: str = "") -> None:
        self._http = http
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key

    async def list_events(
        self,
        *,
        org_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        type: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        resource: Optional[str] = None,
        result: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> PaginatedList[AuditEvent]:
        query: Dict[str, Any] = {}
        if org_id is not None:
            query["org_id"] = org_id
        if workspace_id is not None:
            query["workspace_id"] = workspace_id
        if agent_id is not None:
            query["agent_id"] = agent_id
        if type is not None:
            query["type"] = type
        if date_from is not None:
            query["date_from"] = date_from
        if date_to is not None:
            query["date_to"] = date_to
        if resource is not None:
            query["resource"] = resource
        if result is not None:
            query["result"] = result
        if page is not None:
            query["page"] = page
        if limit is not None:
            query["limit"] = limit

        data = await self._http.get("/audit/events", query=query if query else None)
        return PaginatedList.from_dict(data, AuditEvent)

    async def get_event(self, event_id: str) -> AuditEvent:
        data = await self._http.get(f"/audit/events/{event_id}")
        return AuditEvent.from_dict(data)

    async def generate_report(
        self,
        *,
        org_id: str,
        date_from: str,
        date_to: str,
    ) -> AuditReport:
        body: Dict[str, Any] = {
            "org_id": org_id,
            "date_from": date_from,
            "date_to": date_to,
        }
        data = await self._http.post("/audit/reports", body=body)
        return AuditReport.from_dict(data)

    async def get_metrics(
        self,
        *,
        org_id: str,
        workspace_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> AuditMetrics:
        query: Dict[str, Any] = {"org_id": org_id}
        if workspace_id is not None:
            query["workspace_id"] = workspace_id
        if agent_id is not None:
            query["agent_id"] = agent_id
        if date_from is not None:
            query["date_from"] = date_from
        if date_to is not None:
            query["date_to"] = date_to

        data = await self._http.get("/audit/metrics", query=query)
        return AuditMetrics.from_dict(data)

    async def stream_events(self, callback: Callable[[AuditEvent], Any]) -> None:
        import json

        url = f"{self._base_url}/audit/stream"
        headers = {
            "Accept": "text/event-stream",
            "Authorization": f"Bearer {self._api_key}",
        }
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", url, headers=headers, timeout=None) as resp:
                resp.raise_for_status()
                event_type = ""
                data = ""
                async for line in resp.aiter_lines():
                    if line.startswith("event: "):
                        event_type = line[7:].strip()
                    elif line.startswith("data: "):
                        data = line[6:]
                    elif line == "" and data:
                        if event_type == "audit":
                            try:
                                callback(AuditEvent.from_dict(json.loads(data)))
                            except Exception:
                                pass
                        event_type = ""
                        data = ""
