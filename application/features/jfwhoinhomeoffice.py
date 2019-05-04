#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

import json
import re
import datetime
import requests

from django.conf import settings
from .jfbaseresponsefeature import JFBaseResponseFeature


class JFWhoInHomeOffice(JFBaseResponseFeature):
    """
    Get who in home office.
    """
    date = None

    def handle(self, elocution_text):
        """
        Handle the response message
        :return:
        """
        self.set_date()
        return self.get_home_office_schedule()

    def set_date(self):
        """
        Try to find some date pattern on given elocution text
        and set a date time object if someone match
        :return:
        """
        match_date = re.search(r'\d{1,2}\/\d{1,2}\/(\d{4}|\d{2})',
                               self.response_elocution)
        if match_date:
            try:
                self.date = datetime.datetime.strptime(match_date.group(0),
                                                       '%d/%m/%Y')
            except Exception:
                self.date = datetime.datetime.strptime(match_date.group(0),
                                                       '%d/%m/%y')
            return True

        if re.search(r'(amanhã|amanha)', self.response_elocution):
            self.date = datetime.datetime.today() + datetime.timedelta(days=1)
            return True

        if re.search(r'(ontem|onten)', self.response_elocution):
            self.date = datetime.datetime.today() + datetime.timedelta(days=-1)
            return True

        self.date = datetime.datetime.today()
        return True

    def get_home_office_schedule(self):
        """
        Get the home office schedule
        :return:
        """
        url = settings.XABLAUTECH_HO_FUNCIONAL_URL
        data = json.dumps({
            'date': self.date.strftime('%Y-%m-%d'),
            'username': settings.XABLAUTECH_HO_FUNCIONAL_LOGIN,
            'password': settings.XABLAUTECH_HO_FUNCIONAL_PASSWORD
        })
        headers = {'Content-Type': 'application/json'}
        request = requests.post(url, data=data, headers=headers, timeout=60)

        if request.status_code == 200:
            try:
                if len(request.json()) > 0:
                    ho_list = [f"{ticket.get('workerName')} ({ticket.get('status')})"
                               for ticket in request.json()]
                    return super().process(data='\n'.join(ho_list),
                                           pattern=':who_in_home_office:')
                else:
                    return self.intent.feature.empty_message
            except Exception:
                return self.intent.feature.error_message

        return self.intent.feature.error_message
