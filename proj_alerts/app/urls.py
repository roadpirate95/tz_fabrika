from django.urls import path, include


from rest_framework import routers
from .views import ClientViewSet, SendingViewSet, sending_messages, SendingList, MessageList

app_name = 'app'


router = routers.DefaultRouter()
router.register(r'client', ClientViewSet)

router2 = routers.DefaultRouter()
router2.register(r'sending', SendingViewSet)
urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/', include(router2.urls)),
    path('api/sending/<int:pk>/', sending_messages),
    path('api/all_sending/', SendingList.as_view()),
    path('api/message/<int:pk>/', MessageList.as_view()),
]
