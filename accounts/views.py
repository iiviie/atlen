from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .serializers import UserInfoSerializer
from authentication.serializers import BaseResponseSerializer

class CheckAuthView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses={
            200: BaseResponseSerializer,
            401: BaseResponseSerializer
        },
        description="Check if JWT authentication is working and return user profile"
    )
    def get(self, request):
        try:
            user_data = UserInfoSerializer(request.user).data
            
            return Response({
                'success': True,
                'message': 'Authentication successful',
                'data': user_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Authentication check failed',
                'errors': {'detail': str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)