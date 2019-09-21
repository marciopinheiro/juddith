#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

from application.services import CacheManager

from .jfbaseresponsefeature import JFBaseResponseFeature


class JFPharmaSale(JFBaseResponseFeature):
    """
    Feature to make pharma purchases.
    """
    def handle(self, elocution_text):
        """
        Handle the feature process.
        :return:
        """
        active_process_feature = self.get_active_process()

        if active_process_feature != self.__class__.__name__:
            CacheManager.update_cache(self.chat_id, 'process', {
                'feature': self.__class__.__name__,
                'step': 0
            })
            return self.response_elocution

        return self.handle_step(self.get_active_step(), elocution_text)

    def handle_step(self, step, elocution_text):
        """
        Handle the feature step.
        :param step:
        :param elocution_text:
        :return:
        """
        step += 1

        if step is 1: # Get ID of Buyer
            CacheManager.update_cache(self.chat_id, 'process', {
                'feature': self.__class__.__name__,
                'step': step
            })

            return 'Esse é o seu CNPJ: ' + elocution_text

        if step is 2:  # Get Products
            CacheManager.update_cache(self.chat_id, 'process', {
                'feature': self.__class__.__name__,
                'step': step
            })

            return 'Esse é o seu produto: ' + elocution_text

        if step is 3:  # End process
            CacheManager.reset_process(self.chat_id)
            return 'Seu pedido está feito.'

        return str(step) + ': ' + elocution_text

    def get_active_process(self):
        """
        Get active process in cache.
        :return:
        """
        cache_data = CacheManager.get_cache(self.chat_id)

        return cache_data['process'].get('feature')

    def get_active_step(self):
        """
        Get active process step in cache.
        :return:
        """
        cache_data = CacheManager.get_cache(self.chat_id)

        return cache_data['process'].get('step')
