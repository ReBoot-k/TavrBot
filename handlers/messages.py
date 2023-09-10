import re
import os
import shutil
from pathlib import Path
from utils import check_subscription, download_file
from client import client
from vkbottle.bot import Message
from schedule import schedulelesson
from config import FILENAME_ALL, FILENAME_CORRECTION


client.labeler.vbml_ignore_case = True


COMPILE = re.compile(r".* (\d{1,2}.\d{1,2})(.*)")
@client.on.message( regex=COMPILE)
async def getfile(message: Message) -> None:
    
    if message.attachments:
        files = []    
        folder = "data" 
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
        os.rename(Path(f"data\\{files[0][1]}"), FILENAME_ALL)
        if len(files) > 1:
            os.rename(Path(f"data\\{files[1][1]}"), FILENAME_CORRECTION)
        else:
            shutil.copy(FILENAME_ALL, FILENAME_CORRECTION)
        
        date = COMPILE.match(message.text).group(1)
        type_week = COMPILE.match(message.text).group(2)
        if type_week:
            type_week = type_week.strip().casefold()
            schedulelesson.set_schedule(week_is_even=bool(schedulelesson.get_closest_match("числитель", [type_week.casefold()])))
        else:
            schedulelesson.set_schedule(date)

        

@client.on.private_message()
@check_subscription
async def handler(message: Message) -> None:
    await message.answer(schedulelesson.get_result(message.text))


