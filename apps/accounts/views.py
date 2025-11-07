from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import UserRegistrationSerializer, UserSerializer
from .models import CustomUser
from config.firebase_config import verify_firebase_token


from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    phone_number = request.data.get('phone_number')
    full_name = request.data.get('full_name')
    user_type = request.data.get('user_type')

    if not all([phone_number, full_name, user_type]):
        return Response({
            'success': False,
            'message': 'Missing required fields'
        }, status=status.HTTP_400_BAD_REQUEST)

    user, created = CustomUser.objects.get_or_create(
        phone_number=phone_number,
        defaults={
            'full_name': full_name,
            'user_type': user_type,
            'firebase_uid': f'test_{phone_number}',
            'is_phone_verified': True,
        }
    )

    # ✅ Generate JWT
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    user_serializer = UserSerializer(user)

    return Response({
        'success': True,
        'message': 'User registered successfully' if created else 'User logged in',
        'access_token': access_token,
        'refresh_token': str(refresh),
        'user': user_serializer.data
    }, status=status.HTTP_200_OK)


"""
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    '''
    Register or login user with Firebase authentication
    POST /api/auth/register
    Body: {
        "phone_number": "+919999999999",
        "full_name": "John Doe",
        "user_type": "seller" or "customer",
        "firebase_id_token": "token_from_firebase"
    }
    '''
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Generate or get auth token
        token, created = Token.objects.get_or_create(user=user)

        # Serialize user data
        user_serializer = UserSerializer(user)

        return Response({
            'success': True,
            'message': 'User registered successfully' if created else 'User logged in',
            'token': token.key,
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)

    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

"""
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_token(request):
    """
    Verify Firebase token and return user details
    POST /api/auth/verify-token
    Body: {
        "firebase_id_token": "token_from_firebase"
    }
    """
    firebase_token = request.data.get('firebase_id_token')

    if not firebase_token:
        return Response({
            'success': False,
            'message': 'Firebase token required'
        }, status=status.HTTP_400_BAD_REQUEST)

    decoded_token = verify_firebase_token(firebase_token)

    if not decoded_token:
        return Response({
            'success': False,
            'message': 'Invalid token'
        }, status=status.HTTP_401_UNAUTHORIZED)

    # Find user by firebase_uid
    try:
        user = CustomUser.objects.get(firebase_uid=decoded_token['uid'])
        token, _ = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user)

        return Response({
            'success': True,
            'token': token.key,
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)

    except CustomUser.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)