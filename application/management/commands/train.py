#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

from django.core.management.base import BaseCommand

import logging

from application.services import Trainer


class Command(BaseCommand):
    help = 'Train a classifier'

    def handle(self, *args, **options):
        logger = logging.getLogger('default')
        logger.info('Starting trainning program')
        trainer = Trainer()
        trainer.fit()
        trainer.persist()
        logger.info('Finishing trainning program')
