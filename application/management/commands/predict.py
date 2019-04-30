from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

import logging

from application.services import Predictor


class Command(BaseCommand):
    help = 'Predict based on load trained classifier'

    def add_arguments(self, parser):
        parser.add_argument('elocution', type=str)

    def handle(self, *args, **options):
        logger = logging.getLogger('default')
        logger.info('Starting predict program')

        try:
            predictor = Predictor()
            return str(predictor.get_prediction(options['elocution']))
        except OSError as e:
            logger.error('The prediction cannot be done.')
            logger.error(str(e))
            return None
        finally:
            logger.info('Finishing predict program')
