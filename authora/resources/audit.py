"""Audit resource -- list events, get events, generate reports, and get metrics."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .._http import AsyncHttpClient, SyncHttpClient
from ..types import AuditEvent, AuditMetrics, AuditReport, PaginatedList


class AuditResource:
    """Query audit events, generate reports, and retrieve metrics (synchronous)."""

    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

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
        """List audit events with optional filters and pagination.

        Args:
            org_id: Filter by organization.
            workspace_id: Filter by workspace.
            agent_id: Filter by agent.
            type: Filter by event type.
            date_from: Start date (ISO-8601).
            date_to: End date (ISO-8601).
            resource: Filter by resource.
            result: Filter by result.
            page: Page number (1-indexed).
            limit: Maximum number of items per page.

        Returns:
            A paginated list of AuditEvent objects.
        """
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
        """Retrieve a single audit event by its ID.

        Args:
            event_id: The unique identifier of the audit event.

        Returns:
            The AuditEvent object.
        """
        data = self._http.get(f"/audit/events/{event_id}")
        return AuditEvent.from_dict(data)

    def generate_report(
        self,
        *,
        org_id: str,
        date_from: str,
        date_to: str,
    ) -> AuditReport:
        """Generate an audit report for a date range.

        Args:
            org_id: The organization to generate the report for.
            date_from: Start of the reporting period (ISO-8601).
            date_to: End of the reporting period (ISO-8601).

        Returns:
            The generated AuditReport.
        """
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
        """Retrieve aggregated audit metrics.

        Args:
            org_id: The organization to get metrics for.
            workspace_id: Optional workspace filter.
            agent_id: Optional agent filter.
            date_from: Optional start date (ISO-8601).
            date_to: Optional end date (ISO-8601).

        Returns:
            Aggregated AuditMetrics.
        """
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


class AsyncAuditResource:
    """Query audit events, generate reports, and retrieve metrics (asynchronous)."""

    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

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
        """List audit events with optional filters and pagination.

        Args:
            org_id: Filter by organization.
            workspace_id: Filter by workspace.
            agent_id: Filter by agent.
            type: Filter by event type.
            date_from: Start date (ISO-8601).
            date_to: End date (ISO-8601).
            resource: Filter by resource.
            result: Filter by result.
            page: Page number (1-indexed).
            limit: Maximum number of items per page.

        Returns:
            A paginated list of AuditEvent objects.
        """
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
        """Retrieve a single audit event by its ID.

        Args:
            event_id: The unique identifier of the audit event.

        Returns:
            The AuditEvent object.
        """
        data = await self._http.get(f"/audit/events/{event_id}")
        return AuditEvent.from_dict(data)

    async def generate_report(
        self,
        *,
        org_id: str,
        date_from: str,
        date_to: str,
    ) -> AuditReport:
        """Generate an audit report for a date range.

        Args:
            org_id: The organization to generate the report for.
            date_from: Start of the reporting period (ISO-8601).
            date_to: End of the reporting period (ISO-8601).

        Returns:
            The generated AuditReport.
        """
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
        """Retrieve aggregated audit metrics.

        Args:
            org_id: The organization to get metrics for.
            workspace_id: Optional workspace filter.
            agent_id: Optional agent filter.
            date_from: Optional start date (ISO-8601).
            date_to: Optional end date (ISO-8601).

        Returns:
            Aggregated AuditMetrics.
        """
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
