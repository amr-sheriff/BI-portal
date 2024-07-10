from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny


class HomePage(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'home.html'


class Login(LoginView):
    template_name = 'login.html'

#@method_decorator(csrf_exempt, name='dispatch')
#@api_view(['GET'])
#@authentication_classes([BasicAuthentication])
#def status_view(request):
#    return HttpResponse("OK", content_type="text/plain", status=200)

#@method_decorator(csrf_exempt, name='dispatch')
#class HealthCheckAPIVIEW(APIView):
#    """
#    Handle incoming health check
#    """
#    authentication_classes = [BasicAuthentication]
#    permission_classes = [AllowAny]

#    def get(self, request, *args, **kwargs):
#        try:
#            return Response(response_data, status=status.HTTP_200_OK)
#        except Exception as e:
#            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
