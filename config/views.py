from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SiteConfiguration
from .serializers import SiteConfigurationSerializer

class SiteConfigurationView(APIView):
    def get(self, request):
        config = SiteConfiguration.get_solo()
        serializer = SiteConfigurationSerializer(config, context={'request': request})
        return Response(serializer.data)
