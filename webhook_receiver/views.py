from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import NotificationSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
import logging
from slack_sdk import WebClient
import os
logger = logging.getLogger(__name__)

slack = WebClient(os.getenv('SLACK_TOKEN'))


@method_decorator(csrf_exempt, name='dispatch')
#@api_view(['GET'])
#@authentication_classes([BasicAuthentication])
class NotificationAPIView(APIView):
    """
    Handle incoming webhook
    """
    authentication_classes = [BasicAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = NotificationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                digits = serializer.validated_data.get("digits")

                if digits in ["1", "2", "3"]:
                    response_data = {
                        "say": "thank you",
                        "language": "english",
                        "voice": "female"
                    }
                else:
                    response_data = {
                        "say": "Incorrect response, our customer service team will connect with you shortly.",
                        "language": "english",
                        "voice": "female"
                    }

                logging.info('Notification captured successfully.')
                slack.chat_postMessage(channel='unifonic_webhook_tracker', text='Response captured from phone: `' + serializer.validated_data.get("recipient") + '` with digit: `' + digits  + '`' )
                return Response(response_data, status=status.HTTP_200_OK)

            # serializer is not valid
            logging.warning('Notification payload is not valid.')
            slack.chat_postMessage(channel='unifonic_webhook_tracker', text='Notification payload is not valid at robocalls response webhook, error: `' + str(serializer.errors) + '`')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            slack.chat_postMessage(channel='unifonic_webhook_tracker', text='Error at robocalls response webhook: `' + str(e) + '`')
            logging.error('Notification API View Error: '+str(e))
