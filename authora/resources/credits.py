from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import AsyncHttpClient, SyncHttpClient


class CreditsResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def balance(self) -> Dict[str, Any]:
        return self._http.get("/credits")

    def transactions(
        self,
        *,
        type: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if type is not None:
            params["type"] = type
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return self._http.get("/credits/transactions", params=params)

    def checkout(self, pack: str) -> Dict[str, Any]:
        return self._http.post("/credits/checkout", json={"pack": pack})


class AsyncCreditsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def balance(self) -> Dict[str, Any]:
        return await self._http.get("/credits")

    async def transactions(
        self,
        *,
        type: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if type is not None:
            params["type"] = type
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return await self._http.get("/credits/transactions", params=params)

    async def checkout(self, pack: str) -> Dict[str, Any]:
        return await self._http.post("/credits/checkout", json={"pack": pack})
