import datetime
import re
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models


def phone_number_is_valid(val):
    if not re.search(r'^\+?[78][-\(]?\d{3}\)?-?\d{3}-?\d{2}-?\d{2}$', val):
        raise ValidationError('Disallowed Tags')


class Client(models.Model):
    JUNIOR = 'JR'
    MIDDLE = 'MD'
    SENIOR = 'SR'

    MOSСOW = 'MSK'
    ATLANTIC = 'AST'
    EUROPE = 'CET'

    POSITION = [
        (JUNIOR, 'Junior'),
        (MIDDLE, 'Middle'),
        (SENIOR, 'Senior'),
    ]

    TIMEZONE = [
        (MOSСOW, 'UTC+3'),
        (ATLANTIC, 'UTC−4'),
        (EUROPE, 'UTC+1'),
    ]

    phoneNumber = models.CharField(
        "Номер телефона", validators=[phone_number_is_valid], max_length=12, unique=True)
    operator = models.PositiveIntegerField("Код оператора")
    tag = models.CharField(max_length=2, choices=POSITION, default=JUNIOR)
    timezone = models.CharField(max_length=3, choices=TIMEZONE, default=MOSСOW)

    def save(self, *args, **kwargs):
        if len(str(self.phoneNumber)) == 12:
            if int(str(self.phoneNumber)[2:5]) == self.operator:
                super(Client, self).save(*args, **kwargs)
            else:
                raise serializers.ValidationError(f'{self.operator}: Код оператора не соответствует номеру телефона.')
        else:
            if int(str(self.phoneNumber)[1:4]) == self.operator:
                super(Client, self).save(*args, **kwargs)
            else:
                raise serializers.ValidationError(f'{self.operator}: Код оператора не соответствует номеру телефона.')


class Sending(models.Model):

    text = models.TextField()
    start = models.DateTimeField("Начало отправки", blank=True)
    finish = models.DateTimeField("Завершение отправки")
    filter_client = models.CharField(max_length=250)


class Message(models.Model):
    create = models.DateTimeField()
    status_sending = models.BooleanField(default=False)
    sending = models.ForeignKey(Sending, on_delete=models.SET_NULL, null=True, related_name='send')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, related_name='client')








