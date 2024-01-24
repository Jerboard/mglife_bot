from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
# from utils.maps import silver_chats

import db


# доступ по золотой карте
def get_gold_url_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='Получить доступ', url="https://t.me/addlist/blMG7Iz-gstjOGNi")
    ]])


# доступ поп серебрянной карте
def get_silver_url_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='Получить доступ', url="https://t.me/addlist/8Gz5ibDS5Xs0MTk6")
    ]])


def get_admin_action_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Сделать возврат', callback_data="admin_act:return")],
        [InlineKeyboardButton(text='Сменить пользователя', callback_data="admin_act:refresh")],
        [InlineKeyboardButton(text='Проверить почту', callback_data="admin_act:check")],
        [InlineKeyboardButton(text='Редактировать потоки', callback_data="edit_flagman_start")]
    ])


# выбор чатов флагманов
def get_silver_chanel_choice(choice: list, list_name: str, all_flagman: tuple[db.FlagmanRow]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    end_button = 7 if list_name == 'silver' else 8
    view_pack_id = []

    for flagman in all_flagman:
        if flagman.pack_id < end_button and flagman.pack_id not in view_pack_id:
            if flagman.pack_id in choice:
                text = f'✅ {flagman.pack_name}'
            else:
                text = flagman.pack_name

            kb.button (text=text, callback_data=f'choice_silver:{flagman.pack_id}:{list_name}')
            view_pack_id.append (flagman.pack_id)

    if len(choice) == 2:
        kb.button(text='❗️❗️❗️ Подтвердить выбор ❗️❗️❗️', callback_data='confirm_choice_silver')

    kb.adjust(1)
    return kb.as_markup()


# даёт чаты
def get_silver_chanel_add(buttons_data: list) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for bt in buttons_data:
        kb.button(text=bt['title'], url=bt['link'])
    kb.adjust(1)
    return kb.as_markup()


# даёт чаты
def get_silver_chanel_start(buttons_data: tuple[db.LinkRow]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for bt in buttons_data:
        kb.button(text=bt.chat_name, url=bt.link)
    kb.adjust(1)
    return kb.as_markup()


# отменяет последнее действие
def get_cancel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='❌ Отмена', callback_data='cancel')]
    ])
