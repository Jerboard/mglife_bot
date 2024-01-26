import requests
import logging

from init import account, group_id, secret_key


# Отправить курс специалист
def get_action_gc(email: str):
    url = f'https://{account}.getcourse.ru/pl/api/account/deals?key={secret_key}&....'

    payloads = {
        "user": {"email": {email}, "phone": "foo"},
        "system": {"refresh_if_exists": 0},
        "deal": {"offer_code": "5446723", "quantity": 1}
    }

    response = requests.post(url=url, data=payloads)
    logging.warning(f'Запрос специалист: {email}, code: {response.status_code}\n{response.text}')



