#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

import sys
import logging
import contextlib
import time

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from .models import Intent
from .ml_services import Predictor
from . import features


@contextlib.contextmanager
def watch_time(message, logger):
    """
    Context manager to print how long a block of code took.
    :param message:
    :param logger:
    :return:
    """
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        logger.info(f'Total elapsed time for {message}: {(t1 - t0):.2f}')


class CacheManager:
    """
    Cache Manager of bot.
    """
    @staticmethod
    def set_cache(key, data, force=False):
        """
        Set bot cache.
        :param key:
        :param data:
        :param force:
        :return:
        """
        cache_data = CacheManager.get_cache(key)

        if not cache_data or force:
            cache.set(key, data, timeout=86400)

            return data

        return None

    @staticmethod
    def get_cache(key):
        """
        Get bot cache.
        :param key:
        :return:
        """
        return cache.get(key)

    @staticmethod
    def update_cache(key, data_key, new_data, append=False):
        """
        Update bot cache.
        :param key:
        :param data_key:
        :param new_data:
        :param append:
        :return:
        """
        cache_data = CacheManager.get_cache(key)

        if cache_data:

            if append:
                cache_data[data_key] = cache_data[data_key] + new_data

            else:
                cache_data[data_key] = new_data

            return CacheManager.set_cache(key, cache_data, True)

        return None


class Interpreter:
    """
    Message interpreter of bot.
    """
    _logger = logging.getLogger('default')
    _last_intent = None
    _entities = None
    _chat_id = None

    def __init__(self, chat_id):
        self._chat_id = str(chat_id)
        self._logger.info('Chat ID: ' + self._chat_id)
        CacheManager.set_cache(self._chat_id, {
            'person': {
                'name': None
            },
            'messages': [],
            'process': {
                'feature': None,
                'step': None
            }
        })

    def translate(self, elocution_text):
        """
        Handle interaction of chat.
        :param elocution_text:
        :return:
        """
        if len(elocution_text) > 0:
            CacheManager.update_cache(self._chat_id, 'messages',
                                      [elocution_text], True)

            active_process = self.get_active_process()
            active_feature_class = active_process.get('feature')

            if active_feature_class is not None:
                feature = active_feature_class()
                return feature.handle(elocution_text)

            else:
                return self.get_ml_response(elocution_text)

    def get_ml_response(self, elocution_text):
        """
        Get response by Machine Learning process.
        :param elocution_text:
        :return:
        """
        predictor = Predictor()
        result = predictor.get_prediction(elocution_text)

        try:
            intent = Intent.objects.get(tag=result)

        except ObjectDoesNotExist:
            self._logger.error('The intent object cannot be find with '
                               'predicted tag')
            sys.exit('Bad girl!')

        feature = self.get_feature_instance(intent)

        if feature is not None:

            try:
                return feature.handle()

            except AttributeError:
                self._logger.error(
                    'The feature class can not '
                    'be found in the features module')
                sys.exit('Bad girl!')

        else:

            try:
                return intent.response.get_response_elocution()

            except ObjectDoesNotExist:
                self._logger.error(
                    'The intent object cannot find a '
                    'response object')
                sys.exit('Bad girl!')

    def get_feature_instance(self, intent):
        """
        Get instance of a intent if exists.
        :param intent:
        :return:
        """
        if intent.feature is not None:

            try:
                feature_class = getattr(features,
                                        intent.feature.call)
                return feature_class(intent)

            except AttributeError:
                self._logger.error(
                    'The feature class can not '
                    'be found in the features module')
                sys.exit('Bad girl!')

        return None

    def get_active_process(self):
        """
        Get active process in cache.
        :return:
        """
        cache_data = CacheManager.get_cache(self._chat_id)

        return cache_data['process']

    def pre_process_entry(self, entry):
        self.get_entities(entry)

    def get_entities(self, elocution_text):
        from .er import EntityRecon

        entity_recon = EntityRecon()
        self._entities = entity_recon.recognize(elocution_text)
        print(self._entities)
