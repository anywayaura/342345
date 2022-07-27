import asyncio
import logging
import os

import aiohttp
from aiogram import Bot

logging.basicConfig(level=logging.INFO)

DVMN_API = os.getenv('DVMN_API_TOKEN')  # dvmn.org user api-key
TG_NOTIFY_BOT = os.getenv('DVMN_REVIEWS_NOTIFY_TG_BOT')  # telegram bot token
TG_CHAT_ID = os.getenv('TG_CHAT_ID')  # telegram chat id to notify


async def dvmn_long_polling(DVMN_API_TOKEN, TG_NOTIFY_BOT, TG_CHAT_ID):
    bot = Bot(token=TG_NOTIFY_BOT)
    params = dict()
    headers = {'Authorization': DVMN_API_TOKEN}
    print('Polling reviews...')
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://dvmn.org/api/long_polling/', headers=headers,
                                       params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    if data["status"] == "timeout":
                        params = {"timestamp": data["timestamp_to_request"]}
                    elif data["status"] == "found":
                        params = {"timestamp": data["last_attempt_timestamp"]}
                        await bot.send_message(TG_CHAT_ID, data)  # debug
                        for work in data['new_attempts']:
                            lesson_title = work["lesson_title"]
                            if work['is_negative']:
                                result = 'Нужна доработка'
                            else:
                                result = 'Успех!'
                            url = work['lesson_url']
                            await bot.send_message(TG_CHAT_ID, f'Работа "{lesson_title}" проверена: {result}\n{url}')

        except asyncio.exceptions.TimeoutError:
            return None

        except ConnectionError as _exce:
            print(f'No internet connection ({_exce})')
            await asyncio.sleep(10)


if __name__ == '__main__':
    asyncio.run(dvmn_long_polling(DVMN_API, TG_NOTIFY_BOT, TG_CHAT_ID))
