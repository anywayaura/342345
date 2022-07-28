import asyncio
import logging
import os

import aiohttp
from aiogram import Bot

logging.basicConfig(level=logging.INFO)

DVMN_API = os.getenv('DVMN_API_TOKEN')  # dvmn.org user api-key
TG_NOTIFY_BOT = os.getenv('DVMN_REVIEWS_NOTIFY_TG_BOT')  # telegram bot token
TG_CHAT_ID = os.getenv('TG_CHAT_ID')  # telegram chat id to notify


async def dvmn_long_polling(dvmn_api_token, tg_notify_bot, tg_chat_id):
    bot = Bot(token=tg_notify_bot)
    params = dict()
    headers = {'Authorization': dvmn_api_token}
    async with aiohttp.ClientSession() as session:
        logging.info('Polling Reviews...')
        while True:
            try:
                async with session.get(
                        'https://dvmn.org/api/long_polling/', headers=headers, params=params) as response:
                    response.raise_for_status()
                    reviews_json = await response.json()
                    if reviews_json["status"] == "timeout":
                        params = {"timestamp": reviews_json["timestamp_to_request"]}
                    elif reviews_json["status"] == "found":
                        params = {"timestamp": reviews_json["last_attempt_timestamp"]}
                        for work in reviews_json['new_attempts']:
                            lesson_title = work["lesson_title"]
                            if work['is_negative']:
                                result = 'Нужна доработка'
                            else:
                                result = 'Успех!'
                            url = work['lesson_url']
                            await bot.send_message(tg_chat_id, f'Работа "{lesson_title}" проверена: {result}\n{url}')

            except asyncio.exceptions.TimeoutError:
                pass

            except ConnectionError as _exce:
                logging.error(f'No internet connection ({_exce})')
                await asyncio.sleep(10)


if __name__ == '__main__':
    asyncio.run(dvmn_long_polling(DVMN_API, TG_NOTIFY_BOT, TG_CHAT_ID))

