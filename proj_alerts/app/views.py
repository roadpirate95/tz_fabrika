from django.db.models import Prefetch
from rest_framework import status, mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from .models import Client, Sending
from .serializers import ClientSerializer, SendingSerializer, SendingListSerializer, MessageSerializer
from rest_framework.viewsets import GenericViewSet
from app.tasks import send
import datetime
import json


@api_view(['POST'])
def sending_messages(request, *args, **kwargs):
    sending_instance = get_object_or_404(Sending, pk=kwargs.get('pk'))
    start = sending_instance.start
    start_new_obj = datetime.datetime(start.year, start.month, start.day, hour=start.hour, minute=start.minute, microsecond=start.microsecond)
    if start_new_obj <= datetime.datetime.now():
        send.delay(str(kwargs.get('pk')))
    else:
        countdown = (start_new_obj - datetime.datetime.now()).seconds
        print(countdown)
        send.apply_async(args=[str(kwargs.get('pk'))], countdown=countdown)
    return Response(status='200', data='Success')


class ClientViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.ListModelMixin,
                    GenericViewSet):

    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class SendingViewSet(mixins.DestroyModelMixin,
                     GenericViewSet):

    queryset = Sending.objects.all()
    serializer_class = SendingSerializer

    def create(self, request, *args, **kwargs):
        json_obj = json.dumps(request.data['filter_client'])
        filter_client = str(json_obj)
        request.data['filter_client'] = filter_client
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        update_sending = get_object_or_404(Sending, pk=kwargs.get('pk'))
        json_obj = json.dumps(request.data['filter_client'])
        filter_client = str(json_obj)
        request.data['filter_client'] = filter_client
        serializer = self.get_serializer(update_sending, data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendingList(APIView):

    def get(self, request):
        sending_all = Sending.objects.prefetch_related(Prefetch('send', to_attr='prefetched_sends'))
        serializer = SendingListSerializer(sending_all, many=True)
        return Response(serializer.data)


class MessageList(APIView):

    def get(self, request, pk):
        get_sending = get_object_or_404(Sending, pk=pk)
        message_for_send = get_sending.send.all()
        serializer = MessageSerializer(message_for_send, many=True)
        return Response(serializer.data)
