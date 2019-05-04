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
