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
                response = interpreter.translate(elocution_text)

                if len(response) > 0:
                    response += ' '
                    elocution_text = str(input(self.style.SUCCESS(response)))
                else:
                    elocution_text = str(input(self.style.SUCCESS('')))
