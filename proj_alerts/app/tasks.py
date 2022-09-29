import datetime
import json
from django.core.mail import send_mail
import requests
from celery import shared_task
from django.shortcuts import get_object_or_404
from proj_alerts.celery import app
from proj_alerts.settings import RECIPIENTS_EMAIL, DEFAULT_FROM_EMAIL, TOKEN_API, URL_OUTER_API
import logging
from .models import Message, Client, Sending
logger = logging.getLogger(__name__)

@shared_task(name='send')
def send(idx):
    headers = {'Authorization': f'Bearer {TOKEN_API}'}
    sending_instance = get_object_or_404(Sending, pk=int(idx))
    filters = json.loads(sending_instance.filter_client)
    tag_filters = tuple(set(filters['tag']))
    operator_filters = tuple(set(filters['oper']))
    clients = Client.objects.filter(tag__in=tag_filters, operator__in=operator_filters)

    for client in clients:
        message = Message.objects.create(create=datetime.datetime.now(), sending=sending_instance, client=client)
        logger.info(f'Message create {message.id}')
    message_join_client = Message.objects.select_related('client').filter(sending_id=sending_instance.id)

    data = {
        "id": 0,
        "phone": "string",
        "text": "string",
    }
    for message in message_join_client:
        data['id'] = message.id
        data['phone'] = message.client.phoneNumber
        data['text'] = sending_instance.text

        response = requests.post(f'{URL_OUTER_API}{data["id"]}', headers=headers, json=data)
        if response.status_code == 200:
            Message.objects.filter(pk=message.id).update(status_sending=True)
            logger.info(f'Message ID {message.id} status_sending : True')



@app.task(name="mail")
def mail():
    today = datetime.datetime.now()
    delta = datetime.timedelta(days=1)
    yesterday = today - delta
    sending_for_one_day = Sending.objects.filter(start__gt=yesterday)
    send_mail('of day', f'{sending_for_one_day}', DEFAULT_FROM_EMAIL, RECIPIENTS_EMAIL)
    return 1
