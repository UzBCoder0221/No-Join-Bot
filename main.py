import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ChatMemberUpdated
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER

# delete this line if you don't want logging (data about execution)
logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv('BOT_API')  
admin_ids = os.getenv("ADMIN_ID")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

monitored_chats = set()

@dp.message(Command('add_chat'))
async def cmd_add_chat(message: types.Message):
    if not message.from_user:
        return

    user_id = message.from_user.id
    if user_id not in admin_ids:
        await message.reply("You don't have permission to add chats.")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Please provide a chat link. Usage: /add_chat <link>")
        return

    link = args[1].strip()
    try:
        chat = await bot.get_chat(link)
        monitored_chats.add(chat.id)
        await message.reply(f"Added chat '{chat.title}' to the monitored list.")
    except Exception as e:
        await message.reply(f"Failed to add chat: {e}")
@dp.message()
async def handle_system_messages(message: types.Message):
    if message.new_chat_members:
        await message.delete()
        # for new_member in message.new_chat_members:
        #     print(f"User {new_member.full_name} joined the chat.")
    elif message.left_chat_member:
        await message.delete()
        # print(f"User {message.left_chat_member.full_name} left the chat.")
    elif message.new_chat_title:
        print(f"Chat title changed to: {message.new_chat_title}")
    elif message.new_chat_photo:
        print("Chat photo changed.")
    elif message.delete_chat_photo:
        print("Chat photo deleted.")
    elif message.video_chat_started:
        print("Live stream started.")
    elif message.video_chat_ended:
        print("Live stream ended.")
    elif message.pinned_message:
        print("A message was pinned.")
@dp.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_join(event: ChatMemberUpdated): 
    if event.chat.id not in monitored_chats:
        return
    if event.new_chat_member.status == 'administrator' or event.new_chat_member.status == 'creator':
        return
    user_id = event.from_user.id
    chat_id = event.chat.id
    try:
        await bot.ban_chat_member(chat_id, user_id, revoke_messages=False)
        await bot.unban_chat_member(chat_id, user_id)
        await bot.send_message(admin_ids[0], f"{event.from_user.full_name} was removed upon joining.",disable_notification=True)
    except Exception as e:
        logging.error(f"Failed to remove user {user_id} from chat {chat_id}: {e}")
    
  
        

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())