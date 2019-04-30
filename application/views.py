#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

from django.shortcuts import render
from application.services import Trainer


def chat(request):
    return render(request, 'application/chat.html')


def train(request):
    trainer = Trainer()
    trainer.fit()
    trainer.persist()
    return render(request, 'application/trained.html')
