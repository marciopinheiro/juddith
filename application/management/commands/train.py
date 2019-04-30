from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

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
