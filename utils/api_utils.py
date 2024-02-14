import logging

import httpx

from datetime import datetime

import db
from init import account, secret_key, bot, ADMINS


# Отправить курс специалист
async def get_action_gc(user_id: int):
    user_info = await db.get_user_info(user_id)
    # today = datetime.now().date()
    # url = f'https://{account}.getcourse.ru/pl/api/account/deals?key={secret_key}&created_at[from]={today}'
    #
    # payloads = {
    #     'key': secret_key,
    #     'created_at[from]': '2024-01-30',
    #     "user": {"email": user_info.email},
    #     "deal": {"offer_code": "5446723", "quantity": 1}
    # }
    #
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(url, data=payloads)
    #
    # response_data = response.json ()
    # if not response_data ['success']:
    if user_info.username:
        user = f'Пользователь: {user_info.full_name} (@{user_info.username})'
    else:
        user = f'Пользователь: {user_info.full_name}'

    text = (f'Пользователь {user} выбрал курс "Специалист"\n\n'
            f'gc_id: <code>{user_info.tg_id}</code>\n'
            f'email: <code>{user_info.email}</code>\n')

    for admin in [653117820, 589889158]:
        try:
            await bot.send_message(
                chat_id=admin,
                text=text
            )
        except Exception as ex:
            logging.warning(f'Уведомление по специалисту не отправлено: {admin}\n{ex}')
