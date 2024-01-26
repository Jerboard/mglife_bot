import logging

from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state


import db
from init import dp, ADMINS, bot, DEBUG
from keyboards import inline_kb as kb
from utils.async_utils import get_silvers_chat, send_access


# @dp.message()
# async def ff(m: Message):
#     print(m.photo[-1].file_id)


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    if message.from_user.id in ADMINS:
        await message.answer(text=hbold('Действия администратора:'),
                             reply_markup=kb.get_admin_action_kb())

    else:
        user = await db.get_user_info(message.from_user.id)
        if user and user.status == 'access':

            await send_access(user)

        else:
            if DEBUG:
                photo_id = 'AgACAgIAAxkBAAImRWWxAAGw-tPwOJBY8cD3pO5hlHCS_gAC49kxGyToiUnuq3B7p7CKKAEAAwIAA3kAAzQE'
            else:
                # photo_id = 'AgACAgIAAxkBAANyZXCNd5RxATSiJISD1oMMOizDfzAAAgXVMRueHYFLX3QWedb7aTUBAAMCAAN5AAMzBA'
                photo_id = 'AgACAgIAAxkBAAIXv2WD3ZNgA3zgkI2fxOjazDyj33gjAAK00DEb7iUhSJa1vRduFvyOAQADAgADeQADMwQ'

            text = ('Урааа 🥳 Поздравляю с покупкой Золотой  или Серебрянной карты.\n\n'
                    'Приготовьтесь к лучшему году в своей жизни 😻 – именно таким вы можете сделать свой 2024-й с '
                    'легендарными курсами и марафонами на ключевые сферы жизни 🔥\n\n'
                    '* Если у вас возникнут вопросы, можете задать их сюда  '
                    '👉  https://4magiclife.getcourse.ru/cms/system/contact\n\n'
                    '‼️ А ТЕПЕРЬ САМОЕ ВАЖНОЕ 👇 \n\n'
                    'Чтобы получить доступ к программам, введите адрес электронной почты, '
                    'который указывали при оплате ❗️\n\n'
                    'Пишите его прямо здесь, в ответ на моё сообщение ⬇️⬇️⬇️')
            await message.answer_photo(photo=photo_id, caption=text)


# сделать фильтр на приват чат
@dp.message(StateFilter(default_state))
async def check_email(message: Message, state: FSMContext) -> None:
    await state.clear ()
    if message.entities and message.entities[0].type == 'email':
        check_user = await db.get_email_info(message.text)
        keyboard = None

        if not check_user:
            await message.answer(
                text='Почта не найдена.\nВозможно вы допустили ошибку или указали другую почту при оплате')
        else:
            print(check_user)

            if check_user.status == 'free':
                text = 'Получить доступ к папке с курсами по карте'
                keyboard = kb.get_gold_url_kb ()

                await db.del_user(check_user.tg_id)
                await db.add_user(tg_id=message.from_user.id,
                                  full_name=message.from_user.full_name,
                                  username=message.from_user.username,
                                  status='access',
                                  gc_id=check_user.gc_id,
                                  email=check_user.email,
                                  list_gc=check_user.list)

                all_chats = await db.get_all_chats()
                for chat in all_chats:
                    try:
                        await bot.unban_chat_member(chat_id=chat,
                                                    user_id=message.from_user.id,
                                                    only_if_banned=True)
                    except:
                        logging.warning(f'Не смог добавить {chat}')

            elif check_user.status == 'access' and check_user.tg_id == message.from_user.id:
                await send_access (check_user)
                return
            else:
                await message.answer('Адрес почты уже использован')
                return

            if check_user.list == 'gold':
                await message.answer (
                    text=text,
                    disable_web_page_preview=True,
                    protect_content=True,
                    reply_markup=keyboard)

            else:
                if check_user.list == 'silver':
                    text = (
                        'Дополнительно по тарифу "Серебряная карта" вы можете выбрать ТОЛЬКО два флагмана.\n\n'
                        '❗️После  выбора появится дополнительная кнопка "Подтвердить выбор"'
                        'После ее нажатия сменить курс будет <b>НЕВОЗМОЖНО</b>.\n\n'
                        '❗Курс "Специалист" допускается к прохождению, только если уже пройден курс "Пользователь". '
                        '❗После выбора курса "Специалист" сменить поток будет невозможно.')
                else:
                    text = ('По условиям рассрочки "Золотой карты" вы сейчас можете выбрать ТОЛЬКО два флагмана.\n\n'
                            '❗️После  выбора появится дополнительная кнопка "Подтвердить выбор"'
                            'После ее нажатия сменить курс будет <b>НЕВОЗМОЖНО</b>.\n\n'
                            '❗Курс "Специалист" допускается к прохождению, только если уже пройден курс "Пользователь". '
                            '❗После выбора курса "Специалист" сменить поток будет невозможно.')

                all_flagman = await db.get_all_flagman ()
                await message.answer(
                    text=text,
                    reply_markup=kb.get_silver_chanel_choice(
                        choice=[],
                        list_name=check_user.list,
                        all_flagman=all_flagman
                    )
                )

    else:
        await message.answer('Некорректный адрес электронной почты')


# выбор чатов
@dp.callback_query(lambda cb: cb.data.startswith('choice_silver'))
async def admin_action(cb: CallbackQuery, state: FSMContext):
    _, chat_key, list_name = cb.data.split(':')
    await state.set_state('choice_silver')
    data = await state.get_data()
    choice = data.get('choice_chats')
    if choice is None:
        choice = []

    if len(choice) == 2:
        choice = choice[1:]

    choice.append(int(chat_key))
    await state.update_data(data={'choice_chats': choice, 'list_name': list_name})
    all_flagman = await db.get_all_flagman ()
    await cb.message.edit_reply_markup(
        reply_markup=kb.get_silver_chanel_choice(
            choice=choice,
            list_name=list_name,
            all_flagman=all_flagman
        ))


# выбор чатов доступ
@dp.callback_query(lambda cb: cb.data.startswith('confirm_choice_silver'))
async def admin_action(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear ()
    is_silver = True if data['list_name'] == 'silver' else False
    await cb.message.delete()
    await get_silvers_chat(
        user_id=cb.from_user.id,
        choice=data['choice_chats'],
        is_silver=is_silver)


# отмена действия
@dp.callback_query(lambda cb: cb.data.startswith('cancel'))
async def cancel(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.delete()


# пишет айди для удаления
@dp.channel_post()
async def chat(message: Message):
    await db.add_chat (message.chat.id)
