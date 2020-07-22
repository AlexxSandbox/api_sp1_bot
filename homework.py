import logging
import os
import requests
import telegram
import time
from dotenv import load_dotenv


load_dotenv()
PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
PRAKTIKUM_URL = 'https://praktikum.yandex.ru/api/user_api/{}/'

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_URL = 'https://api.telegram.org/bot{}/{}'

logging.basicConfig(filename='log.txt', level=logging.ERROR, format='%(name)s - %(asctime)s - %(message)s')


def parse_homework_status(homework):
    if 'homework_name' in homework and 'status' in homework:
        homework_name = homework['homework_name']
        homework_status = homework['status']

        if homework_status == 'rejected':
            verdict = 'К сожалению в работе нашлись ошибки.'
        elif homework_status == 'approved':
            verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
        else:
            verdict = 'Но статус получить не удалось. Свяжитесь с ревьювером.'

        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    log = logging.getLogger('Praktikum')
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    request_url = PRAKTIKUM_URL.format('homework_statuses')
    try:
        homework_statuses = requests.get(request_url, headers=headers, params=params).json()

        if 'homeworks' in homework_statuses:
            return homework_statuses
        elif 'message' in homework_statuses:
            error_msg = homework_statuses['message']
            raise KeyError(f'{error_msg}')

    except KeyError as e:
        log.error(str(e))


def send_message(message):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')

            if current_timestamp is None:
                current_timestamp = int(time.time())

            time.sleep(900)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
