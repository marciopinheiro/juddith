#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

import re


class JFBaseResponseFeature(object):
    """
    Parent class of Functional Classes
    """
    chat_id = None
    intent = None
    response_elocution = None

    def __init__(self, chat_id, intent):
        """
        Init class with interaction elocution text and the response object.
        :param intent:
        """
        self.chat_id = chat_id
        self.intent = intent

        if self.intent:
            self.response_elocution = intent.response.get_response_elocution()

    def process(self, data=None, pattern=None):
        """
        Replace the response string pattern with the given data
        :param data:
        :param pattern:
        :return:
        """
        response_message = self.response_elocution

        if data and pattern:

            if type(data) == str:
                data = [data]
                pattern = [pattern]

            for idx, item in enumerate(data):
                response_message = re.sub(rf"{pattern[idx]}",
                                          str(data[idx]).lower(),
                                          str(response_message),
                                          flags=re.IGNORECASE)
        return response_message
