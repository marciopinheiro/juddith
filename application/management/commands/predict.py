#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

from django.core.management.base import BaseCommand

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
