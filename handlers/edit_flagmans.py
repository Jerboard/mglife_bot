from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from asyncio import sleep

import db
from init import dp, bot
import keyboards as kb
from utils.async_utils import get_channel_info


async def get_main_flagman_menu(chat_id: int, message_id: int = None):
    all_flagman = await db.get_all_flagman ()
    text = f'<b>Изменить флагманы:</b>'
    if message_id:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=kb.get_main_edit_flagman_kb (all_flagman)
        )
    else:
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=kb.get_main_edit_flagman_kb (all_flagman))


async def view_channel_pack(pack_id: int, chat_id: int, message_id: int = 0):
    channel_pack = await db.get_all_flagman (pack_id=pack_id)

    text = (f'<b>Название:</b> {channel_pack [0].pack_name}\n\n'
            f'<b>Каналы в пакете:</b>\n')

    for channel in channel_pack:
        text = f'{text}{channel.channel_name}\n'

    if message_id:
        await bot.edit_message_text (
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=kb.get_edit_flagman_kb (channel_pack)
        )
    else:
        await bot.send_message (
            chat_id=chat_id,
            text=text,
            reply_markup=kb.get_edit_flagman_kb (channel_pack)
        )


# изменение флагманов
@dp.callback_query(lambda cb: cb.data.startswith('edit_flagman_start'))
async def edit_flagman_start(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await get_main_flagman_menu(chat_id=cb.message.chat.id, message_id=cb.message.message_id)


# начала введения изменений
@dp.callback_query(lambda cb: cb.data.startswith('edit_flagman_update'))
async def edit_flagman_start(cb: CallbackQuery, state: FSMContext) -> None:
    _, option, pack_id = cb.data.split (':')
    pack_id = int(pack_id)

    if option == 'date':
        text = 'Отправьте дату начала нового потока в формате <code>дд.мм.гггг</code>'

        await state.set_state('update_date')

    elif option == 'name':
        pack_info = await db.get_pack_info(pack_id=pack_id)
        text = (f'Отправьте новое название для пакета <i>{pack_info.pack_name}</i>\n\n'
                f'❗️ Название не должно быть длиннее 128 символов')

        await state.set_state ('update_name')

    else:
        text = 'Отправьте ID канала'
        await state.set_state ('add_channel')

    sent = await cb.message.answer (text, reply_markup=kb.get_cancel_kb ())
    await state.update_data (data={
        'sent_message_id': sent.message_id,
        'main_message_id': cb.message.message_id,
        'pack_id': pack_id})


# принимает новую дату
@dp.message(StateFilter('update_date'))
async def update_date(msg: Message, state: FSMContext) -> None:
    await msg.delete()
    if len(msg.text.split('.')) != 3 and not msg.text.replace('.', '').isdigit():
        sent = await msg.answer('Некорректный формат даты')
        await sleep(3)
        await sent.delete()

    else:
        data = await state.get_data()

        all_flagman = await db.get_all_flagman (pack_id=data['pack_id'])
        await db.inactive_all_flagman(pack_id=data['pack_id'])
        for flagman in all_flagman:
            await db.add_flagman(
                start_date=msg.text,
                status='active',
                pack_id=flagman.pack_id,
                pack_name=flagman.pack_name,
                channel_name=flagman.channel_name,
                channel_id=flagman.channel_id
            )

        if data['pack_id']:
            text = f'В пакете {all_flagman[0].pack_name} начала всех потоков изменена на {msg.text}'
        else:
            text = f'Дата начала всех потоков изменена на {msg.text}'

        await state.clear()
        await bot.edit_message_text (
            chat_id=msg.chat.id,
            message_id=data ['message_id'],
            text=text
        )


# принимает новое имя канала
@dp.message(StateFilter('update_name'))
async def update_name(msg: Message, state: FSMContext) -> None:
    await msg.delete ()
    if len(msg.text) > 128:
        sent = await msg.answer(f'Слишком длинное название {len(msg.text)} символов')
        await sleep(3)
        await sent.delete()
    else:
        data = await state.get_data ()
        await state.clear()

        await db.update_flagman_pack(pack_id=data ['pack_id'], pack_name=msg.text)
        await bot.delete_message(chat_id=msg.chat.id, message_id=data['sent_message_id'])
        await view_channel_pack (
            pack_id=data['pack_id'],
            chat_id=msg.chat.id,
            message_id=data['main_message_id']
        )


# добавляет канал в пакет
@dp.message (StateFilter ('add_channel'))
async def add_channel(msg: Message, state: FSMContext) -> None:
    await msg.delete ()
    check_chat_id = msg.forward_from_chat.id if msg.forward_from_chat else msg.text

    channel_info = await get_channel_info(check_chat_id=check_chat_id)
    if not channel_info:
        sent = await msg.answer (f'Бот не является администратором в канале\n\n'
                                 f'Дайте боту статус администратора и попробуйте ещё раз')
        await sleep (3)
        await sent.delete ()

    else:
        data = await state.get_data()
        await state.clear()
        channel_info = await bot.get_chat(chat_id=msg.text)
        pack_info = await db.get_pack_info (pack_id=data['pack_id'])
        await db.add_flagman (
            start_date=pack_info.start_date,
            status='active',
            pack_id=pack_info.pack_id,
            pack_name=pack_info.pack_name,
            channel_name=channel_info.title,
            channel_id=channel_info.id
        )

        await bot.delete_message(chat_id=msg.chat.id, message_id=data['sent_message_id'])
        await view_channel_pack (
            pack_id=data ['pack_id'],
            chat_id=msg.chat.id,
            message_id=data ['main_message_id']
        )


# показывает пак флагманов
@dp.callback_query(lambda cb: cb.data.startswith('edit_flagman_pack'))
async def edit_flagman_pack(cb: CallbackQuery, state: FSMContext) -> None:
    _, pack_id = cb.data.split(':')

    await view_channel_pack (
        pack_id=pack_id,
        chat_id=cb.message.chat.id,
        message_id=cb.message.message_id
    )


# показывает канал флагман
@dp.callback_query(lambda cb: cb.data.startswith('edit_flagman_channel'))
async def edit_flagman_pack(cb: CallbackQuery, state: FSMContext) -> None:
    _, row_id_str = cb.data.split(':')
    row_id = int (row_id_str)

    channel_info = await db.get_flagman(row_id)
    text = f'<b>Название канала:</b> {channel_info.channel_name}'

    await cb.message.edit_text(text, reply_markup=kb.get_edit_channel_kb(channel_info))


# показывает канал флагман
@dp.callback_query (lambda cb: cb.data.startswith ('edit_flagman_del_channel'))
async def edit_flagman_pack(cb: CallbackQuery, state: FSMContext) -> None:
    _, pack_id_str, row_id_str = cb.data.split (':')
    pack_id = int (pack_id_str)
    row_id = int (row_id_str)
    await db.del_pack_row (row_id)
    await view_channel_pack(
        pack_id=pack_id,
        chat_id=cb.message.chat.id,
        message_id=cb.message.message_id
    )