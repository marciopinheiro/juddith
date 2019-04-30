import graphene

import application.schema as application_schema


class Query(application_schema.Chat, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
