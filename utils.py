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

def check_subscription(function):
    async def wrapper(*args, **kwargs):
        message = args[0]
        is_subscribed = await client.api.groups.is_member(
            group_id=config.GROUP_ID, user_id=message.from_id
        )
        if not is_subscribed:
            await message.answer(
                "Подпишитесь на сообщество, чтобы использовать этого бота"
            )
        else:
            await function(*args, **kwargs)
    return wrapper

def check_is_admin(function):
    async def wrapper(*args, **kwargs):
        message = args[0]
        admins = await client.api.groups.get_members(group_id=config.GROUP_ID, filter="managers")
        for admin in admins.items:
            if admin.id == message.from_id:
                await function(*args, **kwargs)
                return
        await message.answer("У вас нет полномочий для использования данной команды")
    return wrapper


def check_is_admin_chat(function):
    async def wrapper(*args, **kwargs):
        message = args[0]
        admins = await client.api.messages.get_conversation_members(peer_id=message.peer_id)
        for admin in admins.items:
            if admin.member_id == message.from_id and admin.is_admin:
                await function(*args, **kwargs)
                return
        await message.answer("У вас нет полномочий для использования данной команды")
    return wrapper
