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
                    asyncio.create_task(self._process_messages(user_id))
            except Exception as e:
                print(f"Error checking pending messages: {e}")