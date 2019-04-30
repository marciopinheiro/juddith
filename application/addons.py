#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

import re
import datetime
import requests

from django.conf import settings
from django.utils.translation import gettext as _
from .models import Intent, Response


class JFBaseResponseFeature(object):
    """
    Parent class of Functional Classes
    """
    intent = None
    response_elocution = None

    def __init__(self, intent):
        """
        Init class with interaction elocution text and the response object.
        :param intent:
        """
        self.intent = intent
        self.response_elocution = intent.response.get_response_elocution()

    def process(self, data=None, pattern=None):
        """
        Replace the response string pattern with the given data
        :param data:
        :param pattern:
        :return:
        """
        if data and pattern:
            if type(data) == str:
                data = [data]
                pattern = [pattern]
            response_message = self.response_elocution
            for idx, item in enumerate(data):
                response_message = re.sub(rf"{pattern[idx]}",
                                          str(data[idx]).lower(),
                                          str(response_message),
                                          flags=re.IGNORECASE)
        return response_message


class JFWhatChatBotFeatures(JFBaseResponseFeature):
    """
    Get what chat bot response's features.
    """

    def handle(self):
        """
        Handle the response message.
        :return:
        """
        return self.get_what_chat_bot_can_do()

    def get_what_chat_bot_can_do(self):
        """
        Get the features of chat bot.
        :return:
        """
        active_value = self.intent.response.get_active_status_value()
        intent_objs = Intent.objects.filter(status=active_value)\
            .exclude(feature__isnull=True)
        chat_bot_can = [f'{i+1} - {intent.response.name}'
                        for i, intent in enumerate(intent_objs)]
        return super().process(data='\n'.join(chat_bot_can),
                               pattern=':chat_bot_can:')


class JFWhatDateTimeNow(JFBaseResponseFeature):
    """
    Get the date and time values.
    """

    def handle(self):
        """
        Handle the response message.
        :return:
        """
        self.response_elocution = self.get_month_day()
        self.response_elocution = self.get_week_day()
        self.response_elocution = self.get_hour()
        return self.response_elocution

    def get_month_day(self):
        """
        Get the actual month day.
        :return:
        """
        dtime = datetime.datetime.now()
        return super().process(data=dtime.strftime("%d/%m/%Y"),
                               pattern=':date:')

    def get_week_day(self):
        """
        Get the actual week day.
        :return:
        """
        today = datetime.datetime.today()
        w_days = [None, _('monday'), _('tuesday'), _('wednesday'),
                  _('thursday'), _('friday'), _('saturday'),
                  _('sunday')]
        return super().process(data=w_days[today.isoweekday()],
                               pattern=':weekday:')

    def get_hour(self):
        """
        Get the actual time with hour and minutes
        :return:
        """
        dtime = datetime.datetime.now()
        return super().process(data=dtime.strftime("%H:%M"),
                               pattern=':time:')


class JFWhatWeatherNow(JFBaseResponseFeature):
    """
    Get weather condition information
    Reference: http://api.openweathermap.org
    """

    def handle(self):
        """
        Handle the response message
        :return:
        """
        return self.get_weather_condition()

    def get_weather_condition(self):
        """
        Get the weather condition
        :return:
        """
        location_id = self.get_location_id()
        url = f"{re.sub(r':id', location_id, settings.CLIMATEMPO_BASE_URL)}"
        request = requests.get(url, timeout=60)

        if request.status_code == 200:
            try:
                response = request.json()
                w_condition = response.get('data').get('condition')
                w_temperature = response.get('data').get('temperature')
                w_sensation = response.get('data').get('sensation')

                data = [w_condition, w_temperature, w_sensation]
                patterns = [':weather_condition:', ':weather_temperature:',
                            ':weather_sensation:']

                return super().process(data=data, pattern=patterns)
            except Exception:
                return self.intent.feature.error_message

        return self.intent.feature.error_message

    # TODO: Get city from elocution message
    @staticmethod
    def get_location_id():
        """
        Get the location ID in Open Weather Map API
        :return:
        """
        locations = {
            'Rio de Janeiro': '5959'
        }

        return locations.get('Rio de Janeiro')
