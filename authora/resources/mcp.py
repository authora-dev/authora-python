from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from .._http import AsyncHttpClient, SyncHttpClient
from ..types import McpProxyResponse, McpServer, McpTool, PaginatedList


class McpResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def register(
        self,
        *,
        workspace_id: str,
        name: str,
        url: str,
        description: Optional[str] = None,
        transport: Optional[str] = None,
        version: Optional[str] = None,
        auth_config: Optional[Dict[str, Any]] = None,
        connection_timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ) -> McpServer:
        body: Dict[str, Any] = {
            "workspace_id": workspace_id,
            "name": name,
            "url": url,
        }
        if description is not None:
            body["description"] = description
        if transport is not None:
            body["transport"] = transport
        if version is not None:
            body["version"] = version
        if auth_config is not None:
            body["auth_config"] = auth_config
        if connection_timeout is not None:
            body["connection_timeout"] = connection_timeout
        if max_retries is not None:
            body["max_retries"] = max_retries

        data = self._http.post("/mcp/servers", body=body)
        return McpServer.from_dict(data)

    def list_servers(self, *, workspace_id: str) -> PaginatedList[McpServer]:
        data = self._http.get("/mcp/servers", query={"workspace_id": workspace_id})
        return PaginatedList.from_dict(data, McpServer)

    def get_server(self, server_id: str) -> McpServer:
        data = self._http.get(f"/mcp/servers/{server_id}")
        return McpServer.from_dict(data)

    def update_server(
        self,
        server_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        url: Optional[str] = None,
        transport: Optional[str] = None,
        version: Optional[str] = None,
        auth_config: Optional[Dict[str, Any]] = None,
        connection_timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ) -> McpServer:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if url is not None:
            body["url"] = url
        if transport is not None:
            body["transport"] = transport
        if version is not None:
            body["version"] = version
        if auth_config is not None:
            body["auth_config"] = auth_config
        if connection_timeout is not None:
            body["connection_timeout"] = connection_timeout
        if max_retries is not None:
            body["max_retries"] = max_retries

        data = self._http.patch(f"/mcp/servers/{server_id}", body=body)
        return McpServer.from_dict(data)

    def delete_server(self, server_id: str) -> None:
        self._http.delete(f"/mcp/servers/{server_id}")

    def list_tools(self, server_id: str) -> List[McpTool]:
        data = self._http.get(f"/mcp/servers/{server_id}/tools")
        items = data.get("items", data) if isinstance(data, dict) else data
        return [McpTool.from_dict(item) for item in items]

    def delete_tool(self, server_id: str, tool_id: str) -> None:
        self._http.delete(f"/mcp/servers/{server_id}/tools/{tool_id}")

    def register_tool(
        self,
        server_id: str,
        *,
        name: str,
        description: Optional[str] = None,
        input_schema: Optional[Dict[str, Any]] = None,
    ) -> McpTool:
        body: Dict[str, Any] = {"name": name}
        if description is not None:
            body["description"] = description
        if input_schema is not None:
            body["input_schema"] = input_schema

        data = self._http.post(f"/mcp/servers/{server_id}/tools", body=body)
        return McpTool.from_dict(data)

    def discover_tools(self, server_id: str) -> Dict[str, Any]:
        data = self._http.post(f"/mcp/servers/{server_id}/discover")
        return data

    def proxy(
        self,
        *,
        method: str,
        params: Any = None,
        request_id: Optional[Union[str, int]] = None,
    ) -> McpProxyResponse:
        body: Dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            body["params"] = params
        if request_id is not None:
            body["id"] = request_id

        headers = {
            "Authorization": f"Bearer {self._http._api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self._http._base_url}/mcp/proxy"
        response = self._http._client.request(
            "POST",
            url,
            json=body,
            headers=headers,
        )
        if not response.is_success:
            from authora._http import _keys_to_snake, _raise_for_status

            resp_body = (
                _keys_to_snake(response.json())
                if "application/json" in response.headers.get("content-type", "")
                else response.text
            )
            _raise_for_status(response.status_code, resp_body, "POST", "/mcp/proxy")

        resp_json = response.json()
        from authora._http import _keys_to_snake

        data = _keys_to_snake(resp_json)
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        return McpProxyResponse.from_dict(data)


class AsyncMcpResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def register(
        self,
        *,
        workspace_id: str,
        name: str,
        url: str,
        description: Optional[str] = None,
        transport: Optional[str] = None,
        version: Optional[str] = None,
        auth_config: Optional[Dict[str, Any]] = None,
        connection_timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ) -> McpServer:
        body: Dict[str, Any] = {
            "workspace_id": workspace_id,
            "name": name,
            "url": url,
        }
        if description is not None:
            body["description"] = description
        if transport is not None:
            body["transport"] = transport
        if version is not None:
            body["version"] = version
        if auth_config is not None:
            body["auth_config"] = auth_config
        if connection_timeout is not None:
            body["connection_timeout"] = connection_timeout
        if max_retries is not None:
            body["max_retries"] = max_retries

        data = await self._http.post("/mcp/servers", body=body)
        return McpServer.from_dict(data)

    async def list_servers(self, *, workspace_id: str) -> PaginatedList[McpServer]:
        data = await self._http.get("/mcp/servers", query={"workspace_id": workspace_id})
        return PaginatedList.from_dict(data, McpServer)

    async def get_server(self, server_id: str) -> McpServer:
        data = await self._http.get(f"/mcp/servers/{server_id}")
        return McpServer.from_dict(data)

    async def update_server(
        self,
        server_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        url: Optional[str] = None,
        transport: Optional[str] = None,
        version: Optional[str] = None,
        auth_config: Optional[Dict[str, Any]] = None,
        connection_timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ) -> McpServer:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if url is not None:
            body["url"] = url
        if transport is not None:
            body["transport"] = transport
        if version is not None:
            body["version"] = version
        if auth_config is not None:
            body["auth_config"] = auth_config
        if connection_timeout is not None:
            body["connection_timeout"] = connection_timeout
        if max_retries is not None:
            body["max_retries"] = max_retries

        data = await self._http.patch(f"/mcp/servers/{server_id}", body=body)
        return McpServer.from_dict(data)

    async def delete_server(self, server_id: str) -> None:
        await self._http.delete(f"/mcp/servers/{server_id}")

    async def list_tools(self, server_id: str) -> List[McpTool]:
        data = await self._http.get(f"/mcp/servers/{server_id}/tools")
        items = data.get("items", data) if isinstance(data, dict) else data
        return [McpTool.from_dict(item) for item in items]

    async def delete_tool(self, server_id: str, tool_id: str) -> None:
        await self._http.delete(f"/mcp/servers/{server_id}/tools/{tool_id}")

    async def register_tool(
        self,
        server_id: str,
        *,
        name: str,
        description: Optional[str] = None,
        input_schema: Optional[Dict[str, Any]] = None,
    ) -> McpTool:
        body: Dict[str, Any] = {"name": name}
        if description is not None:
            body["description"] = description
        if input_schema is not None:
            body["input_schema"] = input_schema

        data = await self._http.post(f"/mcp/servers/{server_id}/tools", body=body)
        return McpTool.from_dict(data)

    async def discover_tools(self, server_id: str) -> Dict[str, Any]:
        data = await self._http.post(f"/mcp/servers/{server_id}/discover")
        return data

    async def proxy(
        self,
        *,
        method: str,
        params: Any = None,
        request_id: Optional[Union[str, int]] = None,
    ) -> McpProxyResponse:
        body: Dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            body["params"] = params
        if request_id is not None:
            body["id"] = request_id

        headers = {
            "Authorization": f"Bearer {self._http._api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self._http._base_url}/mcp/proxy"
        response = await self._http._client.request(
            "POST",
            url,
            json=body,
            headers=headers,
        )
        if not response.is_success:
            from authora._http import _keys_to_snake, _raise_for_status

            resp_body = (
                _keys_to_snake(response.json())
                if "application/json" in response.headers.get("content-type", "")
                else response.text
            )
            _raise_for_status(response.status_code, resp_body, "POST", "/mcp/proxy")

        resp_json = response.json()
        from authora._http import _keys_to_snake

        data = _keys_to_snake(resp_json)
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        return McpProxyResponse.from_dict(data)
