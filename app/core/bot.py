import os
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import BadRequest

from ..config import TELEGRAM_BOT_TOKEN, DOCUMENT_UPLOAD_PATH
from ..handlers.message import message_handler
from ..handlers.document import document_handler
from ..utils.language import detect_language
from ..utils.logging import log_user_interaction, get_logger
from ..database.mongodb import db
from ..models.message import Message

# Get logger for bot operations
bot_logger = get_logger('telegram_bot')

class TelegramBot:
    def __init__(self):
        self.app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()
        self.processing_users = set()
        self.user_contexts = {}  # Store user contexts for replies
        os.makedirs(DOCUMENT_UPLOAD_PATH, exist_ok=True)

    def setup_handlers(self):
        """Setup message and command handlers"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("docs", self.list_documents))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.app.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "Hello! I'm a multilingual AI assistant. "
            "You can chat with me in any language."
        )

    async def list_documents(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /docs command"""
        user_id = str(update.effective_user.id)
        docs = db.get_user_documents(user_id)
        
        if not docs:
            await update.message.reply_text("You haven't uploaded any documents yet.")
            return
        
        response = "Your uploaded documents:\n\n"
        for doc in docs:
            status = "✅" if doc.get("status") == "processed" else "❌"
            file_path = doc.get('file_path', '')
            if file_path:
                file_name = os.path.basename(file_path)
            else:
                file_name = doc.get('metadata', {}).get('file_name', 'Unknown')
            upload_time = doc.get('upload_time', datetime.utcnow()).strftime('%Y-%m-%d %H:%M')
            response += f"{status} {file_name} - {upload_time}\n"
        
        await update.message.reply_text(response)

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle document uploads"""
        user_id = str(update.effective_user.id)
        document = update.message.document
        
        # Store chat context for this user
        self.user_contexts[user_id] = {
            'chat_id': update.effective_chat.id,
            'message_id': update.message.message_id,
            'update': update
        }
        
        # Download file
        file = await context.bot.get_file(document.file_id)
        file_path = os.path.join(DOCUMENT_UPLOAD_PATH, f"{user_id}_{document.file_name}")
        await file.download_to_drive(file_path)
        
        try:
            # Process document
            result = await document_handler.process_document(file_path, user_id)
            
            if result["status"] == "exists":
                await update.message.reply_text("This document has already been uploaded and processed.")
            else:
                await update.message.reply_text(
                    "Document uploaded and processed successfully! I will analyze it and provide a summary."
                )
                
                # Schedule message processing if not already processing for this user
                if user_id not in self.processing_users:
                    self.processing_users.add(user_id)
                    asyncio.create_task(self._process_messages(user_id))
                
        except Exception as e:
            await update.message.reply_text(f"Error processing document: {str(e)}")
        finally:
            # Clean up downloaded file
            if os.path.exists(file_path):
                os.remove(file_path)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        # Check if message exists and has text
        if not update.message or not update.message.text or not update.effective_user:
            return
            
        user = update.effective_user
        user_id = str(user.id)
        message_text = update.message.text
        
        # Log user interaction
        log_user_interaction(
            user_id=user.id,
            username=user.username or "unknown",
            action="message_sent",
            details={
                'message_type': 'text',
                'chat_id': update.effective_chat.id if update.effective_chat else None,
                'message_length': len(message_text),
                'message_preview': message_text[:100] + "..." if len(message_text) > 100 else message_text
            }
        )
        
        bot_logger.info(f"📝 Processing message from user {user.username or user.id} in chat {update.effective_chat.id if update.effective_chat else 'unknown'}")
        
        # Store chat context for this user
        self.user_contexts[user_id] = {
            'chat_id': update.effective_chat.id if update.effective_chat else None,
            'message_id': update.message.message_id,
            'update': update
        }
        
        # Create message object and insert it
        message_obj = Message(
            user_id=user_id,
            message=message_text,
            timestamp=datetime.now()
        )
        await db.insert_message(message_obj)
        
        # Schedule message processing if not already processing for this user
        if user_id not in self.processing_users:
            self.processing_users.add(user_id)
            asyncio.create_task(self._process_messages(user_id))

    async def _process_messages(self, user_id: str):
        """Process messages for a user"""
        try:
            response = await message_handler.process_message_queue(user_id)
            if response:
                # Get user context for proper reply
                user_context = self.user_contexts.get(user_id)
                if user_context:
                    # Split long messages and reply in the same chat
                    await self._send_long_message(user_context, response)
                else:
                    print(f"Warning: No context found for user {user_id}")
        except Exception as e:
            print(f"Error processing messages for user {user_id}: {e}")
        finally:
            self.processing_users.discard(user_id)
            
            # Check for more pending messages
            try:
                pending_messages = message_handler.db.message_queue.count_documents({
                    "user_id": user_id,
                    "is_processed": False
                })
                
                if pending_messages > 0:
                    self.processing_users.add(user_id)
                    # Use asyncio.create_task properly
                    try:
                        asyncio.create_task(self._process_messages(user_id))
                    except RuntimeError:
                        # If event loop is closed, don't create new tasks
                        pass
            except Exception as e:
                print(f"Error checking pending messages: {e}")
                # Don't try to create new tasks if there's an error

    async def _send_long_message(self, user_context: dict, text: str, max_length: int = 4000):
        """Split and send long messages as replies in the same chat"""
        if not user_context:
            print("Error: No user context available for sending message")
            return
            
        chat_id = user_context['chat_id']
        
        try:
            # If message is short enough, send it directly
            if len(text) <= max_length:
                await self.app.bot.send_message(chat_id=chat_id, text=text)
                return

            # Split message into parts
            parts = []
            current_part = ""
            
            # Split by paragraphs first
            paragraphs = text.split("\n\n")
            
            for paragraph in paragraphs:
                # If adding this paragraph would exceed max_length
                if len(current_part) + len(paragraph) + 2 > max_length:
                    # If current_part is not empty, add it to parts
                    if current_part:
                        parts.append(current_part.strip())
                    current_part = paragraph
                else:
                    # Add paragraph to current_part
                    if current_part:
                        current_part += "\n\n"
                    current_part += paragraph
            
            # Add the last part if not empty
            if current_part:
                parts.append(current_part.strip())
            
            # Send each part with a part number
            total_parts = len(parts)
            for i, part in enumerate(parts, 1):
                if total_parts > 1:
                    header = f"Part {i}/{total_parts}:\n\n"
                    message = header + part
                else:
                    message = part
                
                try:
                    await self.app.bot.send_message(chat_id=chat_id, text=message)
                    # Add a small delay between messages to maintain order
                    if i < total_parts:
                        await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"Error sending message part {i}: {str(e)}")
                    # If a part is still too long, split it further
                    if isinstance(e, BadRequest) and "Message is too long" in str(e):
                        # Split into smaller parts
                        subparts = [message[j:j + max_length] for j in range(0, len(message), max_length)]
                        for subpart in subparts:
                            try:
                                await self.app.bot.send_message(chat_id=chat_id, text=subpart)
                                await asyncio.sleep(0.5)
                            except Exception as sub_e:
                                print(f"Error sending message subpart: {sub_e}")
                                
        except Exception as e:
            print(f"Error in _send_long_message: {e}")
            # Fallback: try to send a simple error message
            try:
                await self.app.bot.send_message(
                    chat_id=chat_id, 
                    text="Sorry, I encountered an error while sending the response. Please try again."
                )
            except Exception as fallback_e:
                print(f"Error sending fallback message: {fallback_e}")

    async def start(self):
        """Start the bot"""
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()

    async def stop(self):
        """Stop the bot"""
        try:
            if self.app.updater.running:
                await self.app.updater.stop()
            if self.app.running:
                await self.app.stop()
            await self.app.shutdown()
        except Exception as e:
            print(f"Error during bot shutdown: {e}")

# Create a singleton instance
bot = TelegramBot()