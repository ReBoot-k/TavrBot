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
            group_id=abs(config.GROUP_ID), user_id=message.from_id
        )
        if not is_subscribed:
            await message.answer(
                "Подпишитесь на сообщество, чтобы использовать этого бота"
            )
        else:
            await function(*args, **kwargs)
    return wrapper



