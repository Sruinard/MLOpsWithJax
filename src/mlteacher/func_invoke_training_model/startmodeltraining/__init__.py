import logging

import os
import requests
import azure.functions as func

from threading import Thread

def main(msg: func.QueueMessage) -> None:
    logging.info('Python queue trigger function processed a queue item: %s',
                 msg.get_body().decode('utf-8'))

    base_url = os.environ.get()
    url = f"{base_url}/models"
    Thread(target=requests.post, args=(url,)).start()
