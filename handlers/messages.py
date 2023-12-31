import re
import os
import shutil
from pathlib import Path
from utils import *
from client import client
from vkbottle.bot import Message, Bot, rules
from vkbottle import Keyboard, Text, GroupEventType, GroupTypes
from schedule import schedulelesson
import config
import json

client.labeler.vbml_ignore_case = True

@client.on.message(text="/even <arg>")
async def even(message: Message, arg) -> None:
    if not await check_is_admin(message):
        return
    arg = arg.casefold()
    if arg in ["1", "true", "t"]:
        week = True
    elif arg in ["0", "false", "f"]:
        week = False
    else:
        await message.answer("Указан неверный аргумент или не указан вовсе")
        return
    schedulelesson.set_schedule(week_is_even=week)
    await message.answer(f"Четность недели изменена на \"{'числитель' if week else 'знаменатель'}\"")


@client.on.message(text="/s <arg>")
async def schedule(message: Message, arg) -> None:
    if not await check_subscription(message):
        return
    with open(config.FILENAME_SAVE, "r") as file:
        json_data = file.read()
        settings = json.loads(json_data)
        
    if str(message.peer_id) not in settings or settings[str(message.peer_id)]["manual_send"]:
            await message.answer(schedulelesson.get_result(arg))


COMPILE = re.compile(r"(?i)((?P<date>\d{1,2}.\d{1,2})|(?P<type_week>числитель|знаменатель)|(понедельник|вторник|сред[ауы]|четверг|пятниц[аы]|замен[ыа]|расписани[ея]))+")
@client.on.message( regex=COMPILE)
async def getfile(message: Message) -> None:
    if message.attachments:
        files = []    
        folder = "data/" 
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if os.path.isfile(file_path): 
                os.remove(file_path) 

        for attachment in message.attachments:
            doc = attachment.doc
            file_name = download_file(doc)
            if file_name is not None:
                files.append((doc.size, file_name))

        files.sort(reverse=True)
        os.rename(Path(f"data/{files[0][1]}"), config.FILENAME_ALL)
        if len(files) > 1:
            os.rename(Path(f"data/{files[1][1]}"), config.FILENAME_CORRECTION)
        else:
            shutil.copy(config.FILENAME_ALL, config.FILENAME_CORRECTION)
        
        date = None
        type_week = None
        for match in COMPILE.finditer(message.text):
            date = match.group("date") or date
            type_week = match.group("type_week") or type_week

        if type_week:
            type_week = type_week.strip()
            week_is_even = (
                schedulelesson.get_closest_match("числитель", [type_week])
                or schedulelesson.get_closest_match("знаменатель", [type_week])
            )

            schedulelesson.set_schedule(week_is_even=bool(week_is_even))
        else:
            schedulelesson.set_schedule(date)

        with open(config.FILENAME_SAVE, "r") as file:
            json_data = file.read()
            settings = json.loads(json_data)
        
        for key in settings:
            if settings[key]["auto_send"]:
                try:
                    await client.api.messages.send(peer_id=key, message=schedulelesson.get_result(settings[key]["group"]), random_id=0)
                except Exception:
                    pass
