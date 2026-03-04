from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import AsyncHttpClient, SyncHttpClient
from ..types import Notification, UnreadCountResult


class NotificationsResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def list(
        self,
        *,
        organization_id: str,
        user_id: Optional[str] = None,
        unread_only: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Notification]:
        query: Dict[str, Any] = {"organization_id": organization_id}
        if user_id is not None:
            query["user_id"] = user_id
        if unread_only is not None:
            query["unread_only"] = unread_only
        if limit is not None:
            query["limit"] = limit
        if offset is not None:
            query["offset"] = offset

        data = self._http.get("/notifications", query=query)
        return [Notification.from_dict(item) for item in data]

    def unread_count(
        self,
        *,
        organization_id: str,
        user_id: Optional[str] = None,
    ) -> UnreadCountResult:
        query: Dict[str, Any] = {"organization_id": organization_id}
        if user_id is not None:
            query["user_id"] = user_id

        data = self._http.get("/notifications/unread-count", query=query)
        return UnreadCountResult.from_dict(data)

    def mark_read(self, notification_id: str) -> Notification:
        data = self._http.patch(f"/notifications/{notification_id}/read")
        return Notification.from_dict(data)

    def mark_all_read(
        self,
        *,
        organization_id: str,
        user_id: Optional[str] = None,
    ) -> None:
        body: Dict[str, Any] = {"organization_id": organization_id}
        if user_id is not None:
            body["user_id"] = user_id
        self._http.patch("/notifications/read-all", body=body)


class AsyncNotificationsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def list(
        self,
        *,
        organization_id: str,
        user_id: Optional[str] = None,
        unread_only: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Notification]:
        query: Dict[str, Any] = {"organization_id": organization_id}
        if user_id is not None:
            query["user_id"] = user_id
        if unread_only is not None:
            query["unread_only"] = unread_only
        if limit is not None:
            query["limit"] = limit
        if offset is not None:
            query["offset"] = offset

        data = await self._http.get("/notifications", query=query)
        return [Notification.from_dict(item) for item in data]

    async def unread_count(
        self,
        *,
        organization_id: str,
        user_id: Optional[str] = None,
    ) -> UnreadCountResult:
        query: Dict[str, Any] = {"organization_id": organization_id}
        if user_id is not None:
            query["user_id"] = user_id

        data = await self._http.get("/notifications/unread-count", query=query)
        return UnreadCountResult.from_dict(data)

    async def mark_read(self, notification_id: str) -> Notification:
        data = await self._http.patch(f"/notifications/{notification_id}/read")
        return Notification.from_dict(data)

    async def mark_all_read(
        self,
        *,
        organization_id: str,
        user_id: Optional[str] = None,
    ) -> None:
        body: Dict[str, Any] = {"organization_id": organization_id}
        if user_id is not None:
            body["user_id"] = user_id
        await self._http.patch("/notifications/read-all", body=body)
