import logging

import db

from init import bot
from keyboards import inline_kb as kb
from utils.enum import LinkRow
from utils.api_utils import get_action_gc


async def ban_user_chats(user_id: int):
    chats = await db.get_all_chats()
    for chat in chats:
        try:
            await bot.ban_chat_member(chat_id=chat, user_id=user_id)
        except:
            pass


async def get_silvers_chat(user_id: int, choice: list, card_list: str):
    if card_list != 'gold':
        chats_1 = await db.get_all_flagman(int(choice [0]))
        chats_2 = await db.get_all_flagman(int(choice [1]))

        chats = chats_1 + chats_2

    else:
        chats = choice

    buttons_data = []
    for chat in chats:
        new_link = await bot.create_chat_invite_link(
            chat_id=chat.channel_id,
            name=f'invite_link_for_{user_id}',
            member_limit=1
        )
        # buttons_data.append({'title': f'{chat.channel_button}', 'link': new_link.invite_link})
        # invite_link = 'https://www.google.com/'
        buttons_data.append({'title': f'{chat.channel_button}', 'link': new_link.invite_link})
        await db.add_link(
            user_id=user_id,
            chat_id=chat.channel_id,
            pack_id=chat.pack_id,
            chat_name=chat.channel_name,
            link=new_link.invite_link
        )

        # если "Специалист" отправка данных
        if chat.pack_id == 6:
            pass
            # user_info = await db.get_user_info(user_id)
            # get_action_gc(user_info.email)

    if card_list == 'silver':
        await bot.send_message (
            chat_id=user_id,
            text='Получить доступ к папке с курсами по карте',
            disable_web_page_preview=True,
            protect_content=True,
            reply_markup=kb.get_silver_url_kb())

    elif card_list == 'gold':
        await bot.send_message (
            chat_id=user_id,
            text='Получить доступ к папке с курсами по карте',
            disable_web_page_preview=True,
            protect_content=True,
            reply_markup=kb.get_gold_url_kb ())

    text = 'Ваш доступ к каналам флагманов.'
    await bot.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=kb.get_silver_chanel_add(buttons_data)
    )


# проверяет актуальность чатов
async def get_current_chat_links(user_id: int) -> list[LinkRow]:
    buttons = await db.get_user_links (user_id=user_id)
    current_links = []
    for button in buttons:
        try:
        # проверяет совпадает ли сохранённая ссылка с актуальной ссылкой
            if button.chat_id == button.channel_id or button.pack_id == 6:
                link = button.link

            else:
                new_link = await bot.create_chat_invite_link(
                    chat_id=button.channel_id,
                    name=f'invite_link_for_{user_id}',
                    member_limit=1
                )

                await db.update_link(
                    row_id=button.id,
                    chat_id=button.channel_id,
                    chat_name=button.channel_name,
                    link=new_link.invite_link)

                link = new_link.invite_link

            current_button = LinkRow (
                id=button.id,
                chat_id=button.channel_id,
                link=link,
                channel_id=button.channel_id,
                channel_name=button.channel_name
            )
            current_links.append(current_button)
        except Exception as ex:
            logging.warning(f'Не обновил кнопку\v{ex}')

    return current_links


# присылает доступ
async def send_access(user: db.UserRow):
    if user.list == 'gold':
        keyboard = kb.get_gold_url_kb ()
    elif user.list == 'silver':
        keyboard = kb.get_silver_url_kb ()
    else:
        keyboard = None

    if user.list != 'part-gold':
        await bot.send_message(
            chat_id=user.tg_id,
            text='Получить доступ к папке с курсами по карте',
            reply_markup=keyboard)

    # if user.list != 'gold':
    buttons = await get_current_chat_links (user_id=user.tg_id)

    if buttons:
        text = 'Ваш доступ к каналам флагманов.'
        await bot.send_message (
            chat_id=user.tg_id,
            text=text,
            reply_markup=kb.get_silver_chanel_start (buttons))
    else:
        if user.list == 'silver':
            text = (
                'Дополнительно по тарифу "Серебряная карта" вы можете выбрать ТОЛЬКО два флагмана.\n\n'
                '❗️После  выбора появится дополнительная кнопка "Подтвердить выбор"'
                'После ее нажатия сменить курс будет <b>НЕВОЗМОЖНО</b>.')

        elif user.list == 'gold':
            text = (
                'Дополнительно по тарифу "Золотая карта" вы можете выбрать ТОЛЬКО два флагмана.\n\n'
                '❗️После  выбора появится дополнительная кнопка "Подтвердить выбор"'
                'После ее нажатия сменить курс будет <b>НЕВОЗМОЖНО</b>.')
        else:
            text = ('По условиям рассрочки "Золотой карты" вы сейчас можете выбрать ТОЛЬКО два флагмана.\n\n'
                    '❗️После  выбора появится дополнительная кнопка "Подтвердить выбор"'
                    'После ее нажатия сменить курс будет <b>НЕВОЗМОЖНО</b>.')

        all_flagman = await db.get_all_flagman ()
        await bot.send_message (
            chat_id=user.tg_id,
            text=text,
            reply_markup=kb.get_silver_chanel_choice (
                choice=[],
                list_name=user.list,
                all_flagman=all_flagman
            )
        )


# проверяет является ли бот админом в канале
async def get_channel_info(check_chat_id: int):
    result = None
    try:
        result = await bot.get_chat (chat_id=check_chat_id)
    except Exception as ex:
        print(ex)
        pass
    finally:
        return result
