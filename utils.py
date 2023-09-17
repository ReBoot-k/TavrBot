import config
import requests
from vkbottle.bot import Message
from vkbottle import Keyboard
from client import client
from pathlib import Path

def download_file(doc):
    file_url = doc.url
    response = requests.get(file_url)
    if response.status_code == 200:
        file_name = doc.title
        with open(Path("data/" + file_name), "wb") as file:
            file.write(response.content)
        return file_name
    else:
        return None

async def check_subscription(message):
    is_subscribed = await client.api.groups.is_member(
        group_id=config.GROUP_ID, user_id=message.from_id
    )
    if is_subscribed:
        return True
    else:
        await message.answer(
            "Подпишитесь на сообщество, чтобы использовать этого бота"
        )
        return False
        


async def check_is_admin(message):
    admins = await client.api.groups.get_members(group_id=config.GROUP_ID, filter="managers")
    for admin in admins.items:
        if admin.id == message.from_id:
            return True
    await message.answer("У вас нет полномочий для использования данной команды")
    return False


async def check_is_admin_chat(message):
    users = await client.api.messages.get_conversation_members(peer_id=message.peer_id)
    for user in users.items:
        if user.member_id == message.from_id and user.is_admin:
            return True
    await message.answer("У вас нет полномочий для использования данной команды")
    return False
