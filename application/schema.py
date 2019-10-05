#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

import graphene

from application.services import Interpreter


class Chat(graphene.ObjectType):
    message = graphene.String(chat=graphene.String(default_value=""),
                              text=graphene.String(default_value=""))

    @staticmethod
    def resolve_message(self, info, **kwargs):
        interpreter = Interpreter(kwargs['chat'])
        response = interpreter.get_response(kwargs['text'])

        return response


schema = graphene.Schema(query=Chat)
