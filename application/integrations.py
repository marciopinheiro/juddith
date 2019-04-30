#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

import json
import requests
import logging

from django.conf import settings
from django.http import JsonResponse

from .services import Interpreter


def telegram(request):
    """
    Web hook view of Telegram integration.
    :param request:
    :return:
    """
    send_url = f'{settings.TELEGRAM_BASE_URL}' \
        f'{settings.TELEGRAM_TOKEN}/sendMessage'

    if request.body is not '':
        json_request = json.loads(request.body)

        logger = logging.getLogger('default')
        logger.info('Telegram incoming request: ' + json.dumps(json_request))

        bot = json_request.get('message').get('from').get('is_bot')
        chat_id = json_request.get('message').get('chat').get('id')
        message_text = json_request.get('message').get('text')

        if json_request.get('message'):

            if not bot and message_text is not None:
                interpreter = Interpreter(chat_id)
                response_text = interpreter.translate(message_text)
                requests.post(send_url, data={'chat_id': chat_id,
                                              'text': response_text})

                return JsonResponse({"Received": True})

    return JsonResponse({"Received": False})




