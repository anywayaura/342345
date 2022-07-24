import asyncio
import os

import requests
from aiogram import Bot

TOKEN = os.getenv('DVMNTKN')
DVMN_NTF_BOT = os.getenv('dvmn_ntf_bot')
MY_TG_ID = os.getenv('MY_TG_ID')

bot = Bot(token=DVMN_NTF_BOT)
admin = MY_TG_ID


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
                for work in response.json()['new_attempts']:
                    lesson_title = work["lesson_title"]
                    if work['is_negative']:
                        result = 'Нужна доработка'
                    else:
                        result = 'Успех!'
                    url = work['lesson_url']
                    await bot.send_message(admin, f'Работа "{lesson_title}" проверена: {result}\n{url}')
        except requests.exceptions.ReadTimeout as _exto:
            print(f'Timeout error ({_exto})')
        except ConnectionError as _exce:
            print(f'No internet connection ({_exce})')
        await asyncio.sleep(5)


if __name__ == '__main__':
    asyncio.run(long_polling())
