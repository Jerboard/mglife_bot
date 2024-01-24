# import requests
# import asyncio
#
# from db.users import update_user
# from init import account, group_id, secret_key
#
#
# async def update_db():
#     request_url = f'https://{account}.getcourse.ru/pl/api/account/groups/{group_id}/users?key={secret_key}'
#     response = requests.get(request_url)
#     data = response.json ()
#     if response.status_code == 200 and data['success']:
#         export_id = data['info']['export_id']
#         await asyncio.sleep(30)
#         export_url = f'https://{account}.getcourse.ru/pl/api/account/exports/{export_id}?key={secret_key}'
#         response = requests.get (export_url)
#         if response.status_code == 200:
#             data = response.json ()
#             for row in data['info']['items']:
#                 await update_user(gc_id=int(row[0]), email=row[1])


# asyncio.run(update_db())
