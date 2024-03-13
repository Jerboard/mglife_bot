import logging
import json
import httpx
import base64

from datetime import datetime

import db
from init import account, secret_key, bot, ADMINS


# Отправить курс специалист
async def get_action_gc(user_id: int):
    user_info = await db.get_user_info(user_id)
    params = {
        "user": {
            "email": user_info.email
        },
        "system": {
            "refresh_if_exists": 1
        },
        "deal": {
            "deal_number": user_id,
            "offer_code": "5435475",
            "product_title": "Выбрали специалиста в боте(Золотая карта)",
            "quantity": "1",
            "deal_status": "payed",
            "deal_cost": "0",
            "deal_is_paid": "1"
        }
    }

    params_json = json.dumps (params)
    base64_encoded_data = base64.b64encode (params_json.encode ()).decode ()

    url = 'https://4magiclife.getcourse.ru/pl/api/deals'
    data = {
        'action': 'add',
        'key': secret_key,
        'params': base64_encoded_data
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data)

    answer = response.json ()
    success = False
    result = answer.get ('result')
    if result and result ['success']:
        success = True

    if not success:
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
