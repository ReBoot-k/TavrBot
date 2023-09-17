from utils import *
from client import client
from vkbottle.bot import Message, rules
from schedule import schedulelesson
import config
import json

def save_settings(peer_id: str, auto_send: bool = None, manual_send: bool = None, group: str = None) -> None:
    with open(config.FILENAME_SAVE, "r") as file:
        json_data = file.read()
        settings = json.loads(json_data)
    
    if auto_send is None:
        auto_send = settings[peer_id]["auto_send"]
    if manual_send is None:
        manual_send = settings[peer_id]["manual_send"]
    if group is None:
        group = settings[peer_id]["group"]
    
    settings[peer_id] = {
        "auto_send": auto_send,
        "manual_send": manual_send,
        "group": group
    }
    with open(config.FILENAME_SAVE, "w") as file:
        json.dump(settings, file)

def get_settings(peer_id: str):
    with open(config.FILENAME_SAVE, "r") as file:
        json_data = file.read()
        settings = json.loads(json_data)
    if peer_id not in settings:
        return "Настроек для этой беседы нет"
    auto_send = settings[peer_id]["auto_send"]
    manual_send = settings[peer_id]["manual_send"]
    group = settings[peer_id]["group"]

    auto_send = '✅' if auto_send else '❌'
    manual_send = '✅' if manual_send else '❌'
    group = group if group else '[данные удалены]'

    return f"Автоматическое отправление расписания - {auto_send}\nРучной вызов расписания - {manual_send}\nГруппа - {group}"


@client.on.chat_message(text=["/help"])
async def help(message: Message) -> None:
    await message.answer(
        "Команды:\n\nНастройка - устанавливает настройки для этой беседы. Синтаксис:\n"
        "/settings <автоматически отправлять расписание (да или нет)> "
        "<разрешить ручной вызов расписания (да или нет)> <название группы>\n\n или если хотите посмотреть настройки: \n /settings\n"
        "\nклавитура - вызов клавиатуры. Синтаксис: \n /kb\n\n"
        "\nрасписание - ручной вызов расписания. Синтаксис:\n /s <группа или преподаватель>\n\n или /s"
    )


@check_is_admin_chat
@client.on.chat_message(text=["/settings <auto_send> <manual_send> <group>", "/settings"])
async def settings(message: Message, auto_send = "", manual_send = "", group = "") -> None:
    peer = str(message.peer_id)
    auto_send = auto_send.casefold()
    manual_send = manual_send.casefold()
    
    if not any([auto_send, manual_send, group]):
        await message.answer(get_settings(peer))
    else:
        if auto_send not in ["да", "нет"]:
            await message.answer(f"Неверное значение для auto_send. Пожалуйста, введите \"да\" или \"нет\"")
            return
        if manual_send not in ["да", "нет"]:
            await message.answer(f"Неверное значение для manual_send. Пожалуйста, введите  \"да\" или \"нет\"")
            return
        if group not in schedulelesson.schedule:
            await message.answer(f"Данной группы не обнаружено")
            return

        if auto_send and not group:
            await message.answer(f"Вы не указали группу!")
            return
        setting = (peer, True if auto_send == "да" else False, True if manual_send == "да" else False, group)

        save_settings(*setting)
        
        await message.answer(f"Настройки бота успешно изменены:\n{get_settings(peer)}")



@client.on.chat_message(rules.ChatActionRule("chat_invite_user"))
async def bot_joined(message: Message) -> None:
    if message.action.member_id == -config.GROUP_ID:
        await message.answer("Привет! Я бот Таврички.\nДай мне права администратора чтобы я мог использовать свои функции. \nПосле выдачи прав администратора напишите /help")

