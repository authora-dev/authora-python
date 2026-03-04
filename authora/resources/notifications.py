"""Notifications resource -- list, count unread, mark read."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import AsyncHttpClient, SyncHttpClient
from ..types import Notification, UnreadCountResult


class NotificationsResource:
    """Manage user notifications (synchronous)."""

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
        """List notifications with optional filters.

        Args:
            organization_id: The organization to list notifications for.
            user_id: Optional user filter.
            unread_only: If True, return only unread notifications.
            limit: Maximum number of notifications to return.
            offset: Number of notifications to skip.

        Returns:
            List of Notification objects.
        """
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
        """Get the count of unread notifications.

        Args:
            organization_id: The organization to count for.
            user_id: Optional user filter.

        Returns:
            An UnreadCountResult with the count.
        """
        query: Dict[str, Any] = {"organization_id": organization_id}
        if user_id is not None:
            query["user_id"] = user_id

        data = self._http.get("/notifications/unread-count", query=query)
        return UnreadCountResult.from_dict(data)

    def mark_read(self, notification_id: str) -> Notification:
        """Mark a single notification as read.

        Args:
            notification_id: The unique identifier of the notification.

        Returns:
            The updated Notification.
        """
        data = self._http.patch(f"/notifications/{notification_id}/read")
        return Notification.from_dict(data)

    def mark_all_read(
        self,
        *,
        organization_id: str,
        user_id: Optional[str] = None,
    ) -> None:
        """Mark all notifications as read for an organization.

        Args:
            organization_id: The organization to mark notifications for.
            user_id: Optional user filter.
        """
        body: Dict[str, Any] = {"organization_id": organization_id}
        if user_id is not None:
            body["user_id"] = user_id
        self._http.patch("/notifications/read-all", body=body)


class AsyncNotificationsResource:
    """Manage user notifications (asynchronous)."""

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
        """List notifications with optional filters.

        Args:
            organization_id: The organization to list notifications for.
            user_id: Optional user filter.
            unread_only: If True, return only unread notifications.
            limit: Maximum number of notifications to return.
            offset: Number of notifications to skip.

        Returns:
            List of Notification objects.
        """
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
        """Get the count of unread notifications.

        Args:
            organization_id: The organization to count for.
            user_id: Optional user filter.

        Returns:
            An UnreadCountResult with the count.
        """
        query: Dict[str, Any] = {"organization_id": organization_id}
        if user_id is not None:
            query["user_id"] = user_id

        data = await self._http.get("/notifications/unread-count", query=query)
        return UnreadCountResult.from_dict(data)

    async def mark_read(self, notification_id: str) -> Notification:
        """Mark a single notification as read.

        Args:
            notification_id: The unique identifier of the notification.

        Returns:
            The updated Notification.
        """
        data = await self._http.patch(f"/notifications/{notification_id}/read")
        return Notification.from_dict(data)

    async def mark_all_read(
        self,
        *,
        organization_id: str,
        user_id: Optional[str] = None,
    ) -> None:
        """Mark all notifications as read for an organization.

        Args:
            organization_id: The organization to mark notifications for.
            user_id: Optional user filter.
        """
        body: Dict[str, Any] = {"organization_id": organization_id}
        if user_id is not None:
            body["user_id"] = user_id
        await self._http.patch("/notifications/read-all", body=body)
