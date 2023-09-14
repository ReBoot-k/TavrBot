import re
import os
import shutil
from pathlib import Path
from utils import check_subscription, download_file
from client import client
from vkbottle.bot import Message
from vkbottle import Keyboard, Text
from schedule import schedulelesson
from config import FILENAME_ALL, FILENAME_CORRECTION

client.labeler.vbml_ignore_case = True


COMPILE = re.compile(r".* (\d{1,2}.\d{1,2})(.*)")
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
        os.rename(Path(f"data/{files[0][1]}"), FILENAME_ALL)
        if len(files) > 1:
            os.rename(Path(f"data/{files[1][1]}"), FILENAME_CORRECTION)
        else:
            shutil.copy(FILENAME_ALL, FILENAME_CORRECTION)
        
        date = COMPILE.match(message.text).group(1)
        type_week = COMPILE.match(message.text).group(2)
        if type_week:
            type_week = type_week.strip().casefold()
            week_is_even = (
                schedulelesson.get_closest_match("числитель", [type_week.casefold()])
                or schedulelesson.get_closest_match("знаменатель", [type_week.casefold()])
            )

            schedulelesson.set_schedule(week_is_even=bool(week_is_even))
        else:
            schedulelesson.set_schedule(date)

        
@client.on.private_message(text=["/start", "начать"])
async def start(message: Message) -> None:
    keyboard = (
        Keyboard(one_time=False, inline=False)
        .add(Text("Расписание", payload={"command": "schedule"}))
    ).get_json()

    await message.answer(
        message="Привет, я бот Таврички. Выберите функцию",
        keyboard=keyboard
    )

@client.on.private_message(payload={"command": "schedule"})
@check_subscription
async def schedule(message: Message) -> None:
    await message.answer("Напишите мне группу или преподавателя")

    @client.on.private_message()
    async def get_word(message: Message) -> None:
        word = message.text
        await message.answer(schedulelesson.get_result(word))
