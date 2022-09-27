from rest_framework import serializers
from .models import Client, Sending, Message


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"


class SendingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sending
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class SendingListSerializer(serializers.ModelSerializer):

    count_message_true = serializers.SerializerMethodField()
    count_message_false = serializers.SerializerMethodField()

    class Meta:
        model = Sending
        fields = "__all__"

    def get_count_message_true(self, obj):
        return len(list(message for message in obj.prefetched_sends if message.status_sending))

    def get_count_message_false(self, obj):
        return len(list(message for message in obj.prefetched_sends if not message.status_sending))
