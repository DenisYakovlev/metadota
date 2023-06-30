import os
import io

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.http import Http404

# Create your views here.


def getFileBytes(path, token):
    # open config file and set token value with string modifier
    try:
        with open(path, 'r') as f:
            config_data = f.read() % token
        content_bytes = io.BytesIO(bytes(config_data, 'utf-8'))
        
        return content_bytes
    except IOError:
        raise Http404

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def SendDotaGSIFile(request):
    config_path =  os.path.join(settings.MEDIA_ROOT, 'gsi_dota_template.txt')
    gsi_token = request.user.gsi_token
    filename = 'gamestate_integration_metadota.cfg'
    
    content_bytes = getFileBytes(config_path, gsi_token)
    return FileResponse(content_bytes, as_attachment=True, filename=filename)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def SendCSGOGSIFile(request):
    config_path =  os.path.join(settings.MEDIA_ROOT, 'gsi_csgo_template.txt')
    gsi_token = request.user.gsi_token
    filename = 'gamestate_integration_metadota.cfg'
    
    content_bytes = getFileBytes(config_path, gsi_token)
    return FileResponse(content_bytes, as_attachment=True, filename=filename)

@api_view(['GET'])
def SendImage(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, "weapons", path)
    
    try:
        with open(file_path, "rb") as f:
            return HttpResponse(f.read(), content_type="image/svg+xml")
    except IOError:
        return HttpResponse({"msg": "file not found"}, status=status.HTTP_404_NOT_FOUND)
    