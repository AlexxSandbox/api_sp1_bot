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
TELEGRAM_BOT = telegram.Bot(token=TELEGRAM_TOKEN)

logging.basicConfig(filename='log.txt', level=logging.ERROR, format='%(name)s - %(asctime)s - %(message)s')


def parse_homework_status(homework):
    log = logging.getLogger('Praktikum')
    if 'homework_name' not in homework and 'status' not in homework:
        log.error('Ключи не найдены.')
    else:
        homework_name = homework['homework_name']
        homework_status = homework['status']
        if homework_status == 'rejected':
            verdict = 'К сожалению в работе нашлись ошибки.'
        elif homework_status == 'approved':
            verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    log = logging.getLogger('Praktikum')
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    request_url = PRAKTIKUM_URL.format('homework_statuses')
    try:
        homework_statuses = requests.get(request_url, headers=headers, params=params)
        return homework_statuses.json()
    except requests.exceptions.RequestException as e:
            log.error(str(e))


def send_message(message):
    return TELEGRAM_BOT.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date') or int(time.time())
            time.sleep(900)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
