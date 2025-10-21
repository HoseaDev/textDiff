"""
WebSocket 连接管理器
用于实时协作功能
"""
from typing import Dict, List
from fastapi import WebSocket
import json
import asyncio


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # 存储活动连接: {document_id: [websocket1, websocket2, ...]}
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # 存储用户信息: {websocket: {"user": "username", "doc_id": "doc_id"}}
        self.connection_info: Dict[WebSocket, Dict] = {}

    async def connect(self, websocket: WebSocket, document_id: str, user: str = "anonymous"):
        """
        接受新的WebSocket连接

        Args:
            websocket: WebSocket连接
            document_id: 文档ID
            user: 用户名
        """
        await websocket.accept()

        # 添加到连接列表
        if document_id not in self.active_connections:
            self.active_connections[document_id] = []

        self.active_connections[document_id].append(websocket)
        self.connection_info[websocket] = {"user": user, "doc_id": document_id}

        # 广播用户加入消息
        await self.broadcast_to_document(
            document_id,
            {
                "type": "user_joined",
                "user": user,
                "active_users": self.get_active_users(document_id),
            },
            exclude=websocket,
        )

    def disconnect(self, websocket: WebSocket):
        """
        断开WebSocket连接

        Args:
            websocket: 要断开的WebSocket连接
        """
        if websocket not in self.connection_info:
            return

        info = self.connection_info[websocket]
        document_id = info["doc_id"]
        user = info["user"]

        # 从连接列表移除
        if document_id in self.active_connections:
            self.active_connections[document_id].remove(websocket)

            # 如果没有活动连接了，删除文档的连接列表
            if not self.active_connections[document_id]:
                del self.active_connections[document_id]

        # 删除连接信息
        del self.connection_info[websocket]

        # 广播用户离开消息（非阻塞）
        asyncio.create_task(
            self.broadcast_to_document(
                document_id,
                {
                    "type": "user_left",
                    "user": user,
                    "active_users": self.get_active_users(document_id),
                },
            )
        )

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        发送个人消息

        Args:
            message: 消息内容
            websocket: 目标WebSocket连接
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")

    async def broadcast_to_document(
        self, document_id: str, message: dict, exclude: WebSocket = None
    ):
        """
        向文档的所有连接广播消息

        Args:
            document_id: 文档ID
            message: 消息内容
            exclude: 要排除的连接（可选）
        """
        if document_id not in self.active_connections:
            return

        # 收集断开的连接
        disconnected = []

        for connection in self.active_connections[document_id]:
            if connection == exclude:
                continue

            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)

        # 清理断开的连接
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_save_event(
        self, document_id: str, version_data: dict, user: str = "anonymous"
    ):
        """
        广播保存事件

        Args:
            document_id: 文档ID
            version_data: 版本数据
            user: 执行保存的用户
        """
        await self.broadcast_to_document(
            document_id,
            {
                "type": "version_saved",
                "user": user,
                "version": version_data,
            },
        )

    async def broadcast_cursor_position(
        self, document_id: str, user: str, position: dict, websocket: WebSocket
    ):
        """
        广播光标位置

        Args:
            document_id: 文档ID
            user: 用户名
            position: 光标位置 {line, column}
            websocket: 发送者的WebSocket（排除）
        """
        await self.broadcast_to_document(
            document_id,
            {"type": "cursor_position", "user": user, "position": position},
            exclude=websocket,
        )

    def get_active_users(self, document_id: str) -> List[str]:
        """
        获取文档的活跃用户列表

        Args:
            document_id: 文档ID

        Returns:
            用户名列表
        """
        if document_id not in self.active_connections:
            return []

        users = []
        for connection in self.active_connections[document_id]:
            if connection in self.connection_info:
                users.append(self.connection_info[connection]["user"])

        return users

    def get_connection_count(self, document_id: str) -> int:
        """
        获取文档的连接数

        Args:
            document_id: 文档ID

        Returns:
            连接数
        """
        if document_id not in self.active_connections:
            return 0

        return len(self.active_connections[document_id])


# 全局连接管理器实例
manager = ConnectionManager()
