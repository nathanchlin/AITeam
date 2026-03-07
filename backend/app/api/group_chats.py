from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import List, Optional
from pydantic import BaseModel, Field
import os
import asyncio

from app.models.schemas import GroupChat, GroupChatCreate, GroupChatMessage, FileAttachment
from app.services.group_chat_service import group_chat_service

router = APIRouter(prefix="/group-chats", tags=["group-chats"])


class MessageCreate(BaseModel):
    """创建消息请求"""
    content: str = Field(..., min_length=1, max_length=5000)
    message_type: str = "text"
    reply_to: Optional[str] = None
    sender_id: str = "user"
    sender_name: str = "用户"
    sender_type: str = "user"


class AddMemberRequest(BaseModel):
    """添加成员请求"""
    agent_id: str


@router.get("", response_model=List[dict])
async def list_chats():
    """获取所有群聊"""
    chats = group_chat_service.get_all_chats()
    return [chat.model_dump() for chat in chats]


@router.post("", response_model=dict)
async def create_chat(chat_data: GroupChatCreate):
    """创建新群聊"""
    chat = group_chat_service.create_chat(chat_data)
    return chat.model_dump()


@router.get("/{chat_id}", response_model=dict)
async def get_chat(chat_id: str):
    """获取指定群聊详情"""
    chat = group_chat_service.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Group chat not found")
    return chat.model_dump()


@router.delete("/{chat_id}")
async def delete_chat(chat_id: str):
    """删除群聊"""
    if not group_chat_service.delete_chat(chat_id):
        raise HTTPException(status_code=404, detail="Group chat not found")
    return {"message": "Group chat deleted successfully"}


@router.post("/{chat_id}/members", response_model=dict)
async def add_member(chat_id: str, request: AddMemberRequest):
    """添加成员到群聊"""
    chat = group_chat_service.add_member(chat_id, request.agent_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Group chat or Agent not found")
    return chat.model_dump()


@router.delete("/{chat_id}/members/{member_id}", response_model=dict)
async def remove_member(chat_id: str, member_id: str):
    """从群聊移除成员"""
    try:
        chat = group_chat_service.remove_member(chat_id, member_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Group chat not found")
        return chat.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{chat_id}/messages", response_model=dict)
async def send_message(chat_id: str, message_data: MessageCreate):
    """发送消息到群聊"""
    message = group_chat_service.send_message(
        chat_id=chat_id,
        sender_id=message_data.sender_id,
        sender_name=message_data.sender_name,
        sender_type=message_data.sender_type,
        content=message_data.content,
        message_type=message_data.message_type,
        reply_to=message_data.reply_to,
        trigger_agent_response=False,  # Don't trigger in sync method
    )
    if not message:
        raise HTTPException(status_code=404, detail="Group chat not found")

    # Trigger agent responses in async context
    if message_data.sender_type == "user":
        chat = group_chat_service.get_chat(chat_id)
        if chat:
            asyncio.create_task(group_chat_service._trigger_agent_responses(chat, message))

    return message.model_dump()


@router.post("/{chat_id}/upload", response_model=dict)
async def upload_file(
    chat_id: str,
    file: UploadFile = File(...),
    sender_id: str = Form("user"),
    sender_name: str = Form("用户"),
    sender_type: str = Form("user"),
    content: str = Form(""),
    reply_to: Optional[str] = Form(None),
):
    """上传文件并发送消息"""
    # Check if chat exists
    chat = group_chat_service.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Group chat not found")

    # Save file
    attachment = await group_chat_service.save_upload_file(chat_id, file, sender_id)

    # Send message with attachment
    message = group_chat_service.send_message(
        chat_id=chat_id,
        sender_id=sender_id,
        sender_name=sender_name,
        sender_type=sender_type,
        content=content or f"上传了文件: {attachment.original_name}",
        message_type="file",
        reply_to=reply_to,
        attachments=[attachment],
    )

    return message.model_dump()


@router.get("/{chat_id}/files/{file_id}")
async def download_file(chat_id: str, file_id: str):
    """下载文件"""
    file_path = group_chat_service.get_file_path(chat_id, file_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    # Get attachment info for filename
    attachment = group_chat_service.get_file_attachment(chat_id, file_id)
    filename = attachment.original_name if attachment else file_id

    return FileResponse(
        file_path,
        filename=filename,
        media_type=attachment.mime_type if attachment else "application/octet-stream",
    )
