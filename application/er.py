#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

import nltk
import requests
import logging
import datetime

from django.conf import settings


class Person:
    first_name = None
    last_name = None

    def __repr__(self):
        return self.__class__.__name__ + ':' + self.first_name + \
               (' ' + self.last_name if self.last_name else '')


class PersonRecon:
    _logger = logging.getLogger('default')

    def recognize(self, text):
        people = list()
        names = self.verify_names(text)

        for i, name in enumerate(names):
            person = Person()

            if i > 0 and names[i-1][0]+1 == name[0]:
                people[-1].last_name = name[1].title()
            else:
                person.first_name = name[1].title()
                people.append(person)

        return people

    def verify_names(self, text):
        import string
        from unidecode import unidecode

        names = list()
        words = [(i, w, unidecode(w))
                 for i, w in enumerate([w for w in nltk.word_tokenize(text)
                                        if w not in string.punctuation])]

        url = settings.IBGE_NOMES_API_BASEURL + '|'.join([w[2] for w in words])

        try:
            request = requests.get(url, timeout=10)

            if request.status_code == 200:
                response = request.json()
                names = [w for w in words
                         if w[2].upper() in [node.get('nome')
                                             for node in response]]
        except Exception:
            self._logger.info(f'Something goes wrong when trying to '
                              f'validate names')

        return names


class TimeRecon:
    _logger = logging.getLogger('default')
    now_time = None

    def __init__(self):
        self.now_time = datetime.datetime.now()

    def recognize(self, text):
        times = list()

        return times

    def search_date(self, text):
        """
        Try to find some date pattern on given elocution text
        and set a date time object if someone match
        :return:
        """
        import re

        match_date = list()

        match_date.append(re.search(r'\d{1,2}\/\d{1,2}\/(\d{4}|\d{2})', text))
        match_date.append(re.search(r'(amanhã|amanha)', text))
        match_date.append(re.search(r'(ontem|onten)', text))

        if match_date:
            try:
                self.date = datetime.datetime.strptime(match_date.group(0),
                                                       '%d/%m/%Y')
            except Exception:
                self.date = datetime.datetime.strptime(match_date.group(0),
                                                       '%d/%m/%y')
            return True

        if re.search(r'(amanhã|amanha)', self.elocution_text):
            self.date = datetime.datetime.today() + datetime.timedelta(days=1)
            return True

        if re.search(r'(ontem|onten)', self.elocution_text):
            self.date = datetime.datetime.today() + datetime.timedelta(days=-1)
            return True

        self.date = datetime.datetime.today()
        return True


class EntityRecon:
    _logger = logging.getLogger('default')

    def __init__(self):
        pass

    def recognize(self, words):
        entities = dict()

        person_recon = PersonRecon()
        time_recon = TimeRecon()

        entities['people'] = person_recon.recognize(words)
        entities['time'] = time_recon.recognize(words)

        return entities
