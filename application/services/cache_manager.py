#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

from django.core.cache import cache


class CacheManager:
    """
    Cache Manager of bot.
    """
    @classmethod
    def set_cache(cls, key, data, force=False):
        """
        Set bot cache.
        :param key:
        :param data:
        :param force:
        :return:
        """
        cache_data = cls.get_cache(key)

        if not cache_data or force:
            cache.set(key, data, timeout=86400)

            return data

        return None

    @classmethod
    def get_cache(cls, key):
        """
        Get bot cache.
        :param key:
        :return:
        """
        return cache.get(key)

    @classmethod
    def update_cache(cls, key, data_key, new_data, append=False):
        """
        Update bot cache.
        :param key:
        :param data_key:
        :param new_data:
        :param append:
        :return:
        """
        cache_data = cls.get_cache(key)

        if cache_data:

            if append:
                cache_data[data_key] = cache_data[data_key] + new_data

            else:
                cache_data[data_key] = new_data

            return cls.set_cache(key, cache_data, True)

        return None

    @classmethod
    def reset_process(cls, key):
        """
        Reset active feature chat cache.
        :param key:
        :return:
        """
        cls.update_cache(key, 'process', {
            'feature': None,
            'step': None
        })

    @classmethod
    def reset(cls, key):
        """
        Reset chat cache.
        :param key:
        :return:
        """
        cls.set_cache(key, {
            'person': {
                'name': None
            },
            'messages': [],
            'process': {
                'feature': None,
                'step': None
            }
        })
