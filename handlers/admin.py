from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter


import db
from init import dp
import keyboards.inline_kb as kb
from utils.async_utils import ban_user_chats


@dp.callback_query(lambda cb: cb.data.startswith('back_admin'))
async def back_admin(cb: CallbackQuery):
    await cb.message.edit_text (
        text='<b>Действия администратора:</b>',
        reply_markup=kb.get_admin_action_kb ())


@dp.callback_query(lambda cb: cb.data.startswith('admin_act'))
async def admin_action(cb: CallbackQuery, state: FSMContext):
    _, action = cb.data.split(':')
    await state.set_state('admin_action')
    await state.update_data(data={'action': action})
    if action == 'return':
        text = 'Отправь мне почту по которой хочешь сделать возврат.'
    else:
        text = 'Отправьте почту'

    await cb.message.answer(text=text)


@dp.message(StateFilter('admin_action'))
async def check_email(message: Message, state: FSMContext) -> None:
    sent = await message.answer('⏳')
    data = await state.get_data()
    await state.clear()
    email_info = await db.get_email_info(message.text)

    if not email_info:
        await message.answer ('Почта не найдена')
        await sent.delete ()
        return

    if data['action'] == 'return':
        await db.ban_email(message.text)

    elif data['action'] == 'check':

        if email_info.username:
            info_user = f'Пользователь: {email_info.full_name} (@{email_info.username})'
        else:
            info_user = f'Пользователь: {email_info.full_name}'

        if email_info.status == 'access':
            text = f'Почта использована\n\n{info_user}\n{email_info.list}'
        elif email_info.status == 'ban':
            text = f'Почта недоступна. Сделан возврат. \n\n{info_user}\n{email_info.list}'
        else:
            text = f'Почта свободна {email_info.list}'

        await message.answer(text)
        await sent.delete ()
        return

    else:
        await db.del_user(email_info.id)
        await db.add_email(gc_id=email_info.gc_id, email=email_info.email)

    await ban_user_chats(email_info.tg_id)
    await db.del_users_link(email_info.tg_id)
    await sent.delete()
