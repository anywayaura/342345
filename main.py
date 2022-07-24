import requests
from datetime import datetime
import os
from aiogram import Bot, Dispatcher, executor, types
import asyncio

TOKEN = os.getenv('DVMNTKN')
DVMN_NTF_BOT = os.getenv('dvmn_ntf_bot')

bot = Bot(token=DVMN_NTF_BOT)
dp = Dispatcher(bot)
admin = 106901721


@dp.message_handler(commands=['works'])
async def get_work_list(message: types.message):
    headers = {'Authorization': TOKEN}
    response = requests.get('https://dvmn.org/api/user_reviews/', headers=headers)
    response.raise_for_status()

    for work in response.json()['results']:
        submit_date = datetime.fromisoformat(work["submitted_at"]).strftime("%d.%m.%y %H:%M")
        lesson_title = work["lesson_title"]
        if work['is_negative']:
            result = 'Доработки'
        else:
            result = 'Принято'
        await bot.send_message(admin, f'{submit_date} {lesson_title} | {result}')
        # print(f'{submit_date} {lesson_title} | {result}')


async def long_polling():
    params = {'': ''}
    headers = {'Authorization': TOKEN}
    while True:
        try:
            response = requests.get('https://dvmn.org/api/long_polling/', headers=headers, params=params)
            response.raise_for_status()
            if response.json()["status"] == "timeout":
                params = {"timestamp": response.json()["timestamp_to_request"]}
            elif response.json()["status"] == "found":
                params = {"timestamp": response.json()["last_attempt_timestamp"]}
                await bot.send_message(admin, response.json())
                print(response.json()['request_query'])
        except requests.exceptions.ReadTimeout as _exto:
            print(f'Timeout error ({_exto})')
        except ConnectionError as _exce:
            print(f'No internet connection ({_exce})')
        await asyncio.sleep(5)


async def on_startup(_):
    asyncio.create_task(long_polling())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)



