from typing import List, Optional, Dict, Any, AsyncGenerator
from datetime import datetime
import uuid
import json
import os
import aiofiles
from fastapi import UploadFile, HTTPException
import mimetypes

from app.models.schemas import (
    GroupChat,
    GroupChatCreate,
    GroupChatMessage,
    GroupChatMember,
    FileAttachment,
)
from app.llm.glm_client import glm_client
from app.services.agent_manager import agent_manager
from app.api.ws import ws_manager


class GroupChatService:
    """群聊服务 - QQ-like group chat system"""

    STORAGE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "group_chats.json")
    UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads", "group_chats")
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {
        "image": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"],
        "document": [".pdf", ".doc", ".docx", ".txt", ".md", ".rtf"],
        "archive": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "code": [".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".json", ".xml"],
    }

    def __init__(self):
        self.chats: Dict[str, GroupChat] = {}
        self._load_chats()
        self._ensure_upload_dir()

    def _ensure_upload_dir(self):
        """Ensure upload directory exists"""
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

    def _load_chats(self):
        """Load persisted group chats from file"""
        if os.path.exists(self.STORAGE_FILE):
            try:
                with open(self.STORAGE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for chat_data in data.get("chats", []):
                        # Convert ISO strings back to datetime
                        chat_data["created_at"] = datetime.fromisoformat(chat_data["created_at"])
                        chat_data["updated_at"] = datetime.fromisoformat(chat_data["updated_at"])

                        # Convert members
                        members = []
                        for member_data in chat_data.get("members", []):
                            member_data["joined_at"] = datetime.fromisoformat(member_data["joined_at"])
                            members.append(GroupChatMember(**member_data))
                        chat_data["members"] = members

                        # Convert messages
                        messages = []
                        for msg_data in chat_data.get("messages", []):
                            msg_data["timestamp"] = datetime.fromisoformat(msg_data["timestamp"])

                            # Convert attachments
                            attachments = []
                            for att_data in msg_data.get("attachments", []):
                                att_data["upload_at"] = datetime.fromisoformat(att_data["upload_at"])
                                attachments.append(FileAttachment(**att_data))
                            msg_data["attachments"] = attachments

                            messages.append(GroupChatMessage(**msg_data))
                        chat_data["messages"] = messages

                        self.chats[chat_data["id"]] = GroupChat(**chat_data)

                print(f"[GroupChatService] Loaded {len(self.chats)} group chats from storage")
            except Exception as e:
                print(f"[GroupChatService] Error loading group chats: {e}")

    def _save_chats(self):
        """Persist group chats to file"""
        try:
            os.makedirs(os.path.dirname(self.STORAGE_FILE), exist_ok=True)

            data = {
                "chats": [
                    {
                        "id": chat.id,
                        "name": chat.name,
                        "description": chat.description,
                        "created_by": chat.created_by,
                        "members": [
                            {
                                "id": m.id,
                                "name": m.name,
                                "type": m.type,
                                "avatar_color": m.avatar_color,
                                "joined_at": m.joined_at.isoformat() if m.joined_at else None,
                            }
                            for m in chat.members
                        ],
                        "messages": [
                            {
                                "id": msg.id,
                                "chat_id": msg.chat_id,
                                "sender_id": msg.sender_id,
                                "sender_name": msg.sender_name,
                                "sender_type": msg.sender_type,
                                "content": msg.content,
                                "message_type": msg.message_type,
                                "reply_to": msg.reply_to,
                                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                                "attachments": [
                                    {
                                        "id": a.id,
                                        "filename": a.filename,
                                        "original_name": a.original_name,
                                        "file_path": a.file_path,
                                        "file_size": a.file_size,
                                        "mime_type": a.mime_type,
                                        "upload_by": a.upload_by,
                                        "upload_at": a.upload_at.isoformat() if a.upload_at else None,
                                    }
                                    for a in msg.attachments
                                ],
                            }
                            for msg in chat.messages
                        ],
                        "created_at": chat.created_at.isoformat() if chat.created_at else None,
                        "updated_at": chat.updated_at.isoformat() if chat.updated_at else None,
                        "is_active": chat.is_active,
                    }
                    for chat in self.chats.values()
                ],
                "saved_at": datetime.utcnow().isoformat(),
            }

            with open(self.STORAGE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[GroupChatService] Error saving group chats: {e}")

    def create_chat(self, chat_create: GroupChatCreate, created_by: str = "user") -> GroupChat:
        """创建新的群聊"""
        chat_id = str(uuid.uuid4())

        # Initialize members list with user
        members = [
            GroupChatMember(
                id="user",
                name="用户",
                type="user",
                avatar_color="#6366f1",
            )
        ]

        # Add selected agents to members
        for agent_id in chat_create.agent_ids:
            agent = agent_manager.get_agent(agent_id)
            if agent:
                # Determine avatar color based on agent type
                color_map = {
                    "coder": "#3b82f6",    # blue
                    "analyst": "#10b981",  # green
                    "assistant": "#8b5cf6", # purple
                    "tester": "#f59e0b",   # orange
                    "custom": "#6b7280",   # gray
                }
                members.append(
                    GroupChatMember(
                        id=agent.id,
                        name=agent.name,
                        type="agent",
                        avatar_color=color_map.get(agent.type.value if hasattr(agent.type, "value") else str(agent.type), "#6b7280"),
                    )
                )

        chat = GroupChat(
            id=chat_id,
            name=chat_create.name,
            description=chat_create.description,
            created_by=created_by,
            members=members,
        )

        # Add system message
        system_message = GroupChatMessage(
            id=str(uuid.uuid4()),
            chat_id=chat_id,
            sender_id="system",
            sender_name="系统",
            sender_type="system",
            content=f"群聊 \"{chat.name}\" 创建成功。欢迎加入！",
            message_type="system",
        )
        chat.messages.append(system_message)

        self.chats[chat_id] = chat
        self._save_chats()

        # Broadcast chat creation
        import asyncio
        asyncio.create_task(ws_manager.broadcast({
            "type": "group_chat_created",
            "data": chat.dict()
        }))

        return chat

    def get_chat(self, chat_id: str) -> Optional[GroupChat]:
        """获取指定群聊"""
        return self.chats.get(chat_id)

    def get_all_chats(self) -> List[GroupChat]:
        """获取所有群聊"""
        return list(self.chats.values())

    def delete_chat(self, chat_id: str) -> bool:
        """删除群聊"""
        if chat_id not in self.chats:
            return False

        del self.chats[chat_id]
        self._save_chats()

        # Broadcast chat deletion
        import asyncio
        asyncio.create_task(ws_manager.broadcast({
            "type": "group_chat_deleted",
            "data": {"chat_id": chat_id}
        }))

        return True

    def add_member(self, chat_id: str, agent_id: str) -> Optional[GroupChat]:
        """添加成员到群聊"""
        chat = self.chats.get(chat_id)
        if not chat:
            return None

        # Check if member already exists
        for member in chat.members:
            if member.id == agent_id:
                return chat

        # Get agent info
        agent = agent_manager.get_agent(agent_id)
        if not agent:
            return None

        # Determine avatar color based on agent type
        color_map = {
            "coder": "#3b82f6",
            "analyst": "#10b981",
            "assistant": "#8b5cf6",
            "tester": "#f59e0b",
            "custom": "#6b7280",
        }

        new_member = GroupChatMember(
            id=agent.id,
            name=agent.name,
            type="agent",
            avatar_color=color_map.get(agent.type.value if hasattr(agent.type, "value") else str(agent.type), "#6b7280"),
        )
        chat.members.append(new_member)
        chat.updated_at = datetime.utcnow()

        # Add system message
        system_message = GroupChatMessage(
            id=str(uuid.uuid4()),
            chat_id=chat_id,
            sender_id="system",
            sender_name="系统",
            sender_type="system",
            content=f"{agent.name} 加入了群聊",
            message_type="system",
        )
        chat.messages.append(system_message)

        self._save_chats()

        # Broadcast member addition
        import asyncio
        asyncio.create_task(ws_manager.broadcast({
            "type": "group_chat_member_added",
            "data": {
                "chat_id": chat_id,
                "member": new_member.dict()
            }
        }))

        return chat

    def remove_member(self, chat_id: str, member_id: str) -> Optional[GroupChat]:
        """从群聊移除成员"""
        chat = self.chats.get(chat_id)
        if not chat:
            return None

        # Cannot remove the user
        if member_id == "user":
            raise ValueError("Cannot remove user from chat")

        member_to_remove = None
        for member in chat.members:
            if member.id == member_id:
                member_to_remove = member
                break

        if not member_to_remove:
            return chat

        chat.members.remove(member_to_remove)
        chat.updated_at = datetime.utcnow()

        # Add system message
        system_message = GroupChatMessage(
            id=str(uuid.uuid4()),
            chat_id=chat_id,
            sender_id="system",
            sender_name="系统",
            sender_type="system",
            content=f"{member_to_remove.name} 离开了群聊",
            message_type="system",
        )
        chat.messages.append(system_message)

        self._save_chats()

        # Broadcast member removal
        import asyncio
        asyncio.create_task(ws_manager.broadcast({
            "type": "group_chat_member_removed",
            "data": {
                "chat_id": chat_id,
                "member_id": member_id
            }
        }))

        return chat

    def send_message(
        self,
        chat_id: str,
        sender_id: str,
        sender_name: str,
        sender_type: str,
        content: str,
        message_type: str = "text",
        reply_to: Optional[str] = None,
        attachments: List[FileAttachment] = None,
    ) -> Optional[GroupChatMessage]:
        """发送消息到群聊"""
        chat = self.chats.get(chat_id)
        if not chat:
            return None

        message = GroupChatMessage(
            id=str(uuid.uuid4()),
            chat_id=chat_id,
            sender_id=sender_id,
            sender_name=sender_name,
            sender_type=sender_type,
            content=content,
            message_type=message_type,
            reply_to=reply_to,
            attachments=attachments or [],
        )

        chat.messages.append(message)
        chat.updated_at = datetime.utcnow()
        self._save_chats()

        # Broadcast message
        import asyncio
        asyncio.create_task(ws_manager.broadcast({
            "type": "group_chat_message",
            "data": message.dict()
        }))

        # Trigger agent responses if sender is user
        if sender_type == "user":
            asyncio.create_task(self._trigger_agent_responses(chat, message))

        return message

    async def _trigger_agent_responses(self, chat: GroupChat, user_message: GroupChatMessage):
        """触发Agent智能响应"""
        try:
            print(f"[GroupChatService] Triggering agent responses for chat {chat.id[:8]}...")
        except:
            pass

        # Extract @mentions from message
        import re
        mentions = re.findall(r"@(\w+)", user_message.content)

        # Build context for agents
        recent_messages = chat.messages[-10:]  # Get last 10 messages
        context = "\n".join([
            f"{msg.sender_name}: {msg.content}"
            for msg in recent_messages
        ])

        # Check each agent member
        for member in chat.members:
            if member.type != "agent":
                continue

            agent = agent_manager.get_agent(member.id)
            if not agent:
                continue

            # Check if agent is mentioned OR respond based on relevance
            should_respond = False
            response_reason = ""

            # Direct mention
            if member.name.lower() in user_message.content.lower():
                should_respond = True
                response_reason = "direct_mention"
            elif any(m.lower() in member.name.lower() for m in mentions):
                should_respond = True
                response_reason = "mention"
            else:
                # For now, agents always respond to user messages in group chat
                should_respond = True
                response_reason = "user_message"

            if should_respond:
                await self._generate_agent_response(chat, agent, user_message, context, response_reason)

    async def _generate_agent_response(
        self,
        chat: GroupChat,
        agent,
        user_message: GroupChatMessage,
        context: str,
        trigger_reason: str,
    ):
        """生成Agent响应"""
        agent_type_str = agent.type.value if hasattr(agent.type, "value") else str(agent.type)

        prompt = f"""你是一个名为 {agent.name} 的 AI 助手。你的角色是 {agent_type_str}。

群聊历史：
{context}

用户刚才说：
{user_message.content}

请以 {agent.name} 的身份回应。保持友好、专业，符合你的角色特点。如果消息是@你的，请直接回应。"""

        try:
            # Stream the response
            response_text = ""
            async for chunk in glm_client.chat_stream(
                prompt,
                agent_type=agent_type_str,
                custom_prompt=agent.custom_prompt,
            ):
                response_text += chunk

            if response_text:
                # Send agent response
                self.send_message(
                    chat_id=chat.id,
                    sender_id=agent.id,
                    sender_name=agent.name,
                    sender_type="agent",
                    content=response_text,
                    reply_to=user_message.id if trigger_reason == "direct_mention" or trigger_reason == "mention" else None,
                )

        except Exception as e:
            # Avoid encoding issues with emoji on Windows console
            error_msg = str(e).encode('ascii', errors='replace').decode('ascii')
            print(f"[GroupChatService] Error generating agent response: {error_msg}")
            self.send_message(
                chat_id=chat.id,
                sender_id=agent.id,
                sender_name=agent.name,
                sender_type="agent",
                content=f"抱歉，我遇到了一些问题：{error_msg}",
            )

    async def save_upload_file(self, chat_id: str, file: UploadFile, upload_by: str) -> FileAttachment:
        """保存上传的文件"""
        # Check file size
        file_size = 0
        file_content = await file.read()
        file_size = len(file_content)

        if file_size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum limit of {self.MAX_FILE_SIZE / (1024*1024)}MB"
            )

        # Check file extension
        filename = file.filename
        if not filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        file_ext = os.path.splitext(filename)[1].lower()
        allowed = False
        for category, extensions in self.ALLOWED_EXTENSIONS.items():
            if file_ext in extensions:
                allowed = True
                break

        if not allowed:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} is not allowed"
            )

        # Save file
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}{file_ext}"
        file_path = os.path.join(self.UPLOAD_DIR, safe_filename)

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_content)

        # Determine mime type
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = "application/octet-stream"

        attachment = FileAttachment(
            id=file_id,
            filename=safe_filename,
            original_name=filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            upload_by=upload_by,
            upload_at=datetime.utcnow(),
        )

        return attachment

    def get_file_attachment(self, chat_id: str, file_id: str) -> Optional[FileAttachment]:
        """获取文件附件信息"""
        chat = self.chats.get(chat_id)
        if not chat:
            return None

        for message in chat.messages:
            for attachment in message.attachments:
                if attachment.id == file_id:
                    return attachment

        return None

    def get_file_path(self, chat_id: str, file_id: str) -> Optional[str]:
        """获取文件物理路径"""
        attachment = self.get_file_attachment(chat_id, file_id)
        if attachment:
            return attachment.file_path
        return None


# Global instance
group_chat_service = GroupChatService()
