"""
WebSocket 实时协作路由
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from ...services.websocket_manager import manager
import json

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/document/{document_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    document_id: str,
    user: str = Query(default="anonymous"),
):
    """
    文档协作 WebSocket 端点

    用于实时协作功能：
    - 用户在线状态同步
    - 版本保存事件广播
    - 光标位置同步（可选）
    - 实时编辑同步（可选）

    消息格式：
    {
        "type": "message_type",
        "data": {...}
    }

    支持的消息类型：
    - cursor_position: 光标位置更新
    - selection: 选中内容更新
    - typing: 正在输入状态
    - save: 保存通知
    """
    await manager.connect(websocket, document_id, user)

    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)

            message_type = message.get("type")

            # 处理不同类型的消息
            if message_type == "cursor_position":
                # 广播光标位置
                position = message.get("position", {})
                await manager.broadcast_cursor_position(
                    document_id, user, position, websocket
                )

            elif message_type == "selection":
                # 广播选中内容
                selection = message.get("selection", {})
                await manager.broadcast_to_document(
                    document_id,
                    {"type": "selection", "user": user, "selection": selection},
                    exclude=websocket,
                )

            elif message_type == "typing":
                # 广播正在输入状态
                is_typing = message.get("is_typing", False)
                await manager.broadcast_to_document(
                    document_id,
                    {"type": "typing", "user": user, "is_typing": is_typing},
                    exclude=websocket,
                )

            elif message_type == "ping":
                # 心跳响应
                await manager.send_personal_message({"type": "pong"}, websocket)

            else:
                # 未知消息类型，广播给其他用户
                await manager.broadcast_to_document(
                    document_id, message, exclude=websocket
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)
