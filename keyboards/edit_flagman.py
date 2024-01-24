from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup


import db


# основная клавиатура изменения флагманов
def get_main_edit_flagman_kb(all_flagman: tuple[db.FlagmanRow]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='📆 Обновить дату всех потоков', callback_data=f'edit_flagman_update:date:0')
    view_pack_id = []
    for flagman in all_flagman:
        if flagman.pack_id not in view_pack_id:
            kb.button(text=flagman.pack_name, callback_data=f'edit_flagman_pack:{flagman.pack_id}')
            view_pack_id.append(flagman.pack_id)

    kb.button(text='🔙 Назад', callback_data='back_admin')
    kb.adjust(1)
    return kb.as_markup()


# клавиатура изменения флагмана
def get_edit_flagman_kb(all_flagman: tuple[db.FlagmanRow]) -> InlineKeyboardMarkup:
    pack_id = all_flagman[0].pack_id
    kb = InlineKeyboardBuilder()
    kb.button(text='📆 Обновить дату потока', callback_data=f'edit_flagman_update:date:{pack_id}')
    kb.button(text='✏️ Изменить название пакета', callback_data=f'edit_flagman_update:name:{pack_id}')
    kb.button(text='➕ Добавить канал', callback_data=f'edit_flagman_update:add_channel:{pack_id}')
    for flagman in all_flagman:
        kb.button(text=f'🖍 {flagman.channel_name}', callback_data=f'edit_flagman_channel:{flagman.id}')

    kb.button(text='🔙 Назад', callback_data='edit_flagman_start')
    kb.adjust(1)
    return kb.as_markup()


# клавиатура изменения флагмана
def get_edit_channel_kb(flagman: db.FlagmanRow) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='🗑 Удалить канал', callback_data=f'edit_flagman_del_channel:{flagman.pack_id}:{flagman.id}')
    kb.button(text='🔙 Назад', callback_data=f'edit_flagman_pack:{flagman.pack_id}')
    kb.adjust(1)
    return kb.as_markup()