#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

from django.core.management.base import BaseCommand

from application.services import Interpreter


class Command(BaseCommand):
    help = 'Start a new console interaction'

    def handle(self, *args, **options):
        elocution_text = ''

        while True:

            if len(elocution_text) == 0:
                elocution_text = str(input(self.style.SUCCESS('')))
            else:

                if elocution_text in ('q', 'Q'):
                    break

                interpreter = Interpreter()
                response = interpreter.get_response(elocution_text)

                if len(response) > 0:
                    response += ' '
                    elocution_text = str(input(self.style.SUCCESS(response)))
                else:
                    elocution_text = str(input(self.style.SUCCESS('')))
