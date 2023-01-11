from rest_framework.authentication import TokenAuthentication, get_authorization_header
from .models import User
from rest_framework import status, exceptions
import jwt
from django.conf import settings
import logging
logger = logging.getLogger(__name__)

class MyLoginTokenAuthentications(TokenAuthentication):
    model = None

    def get_model(self):
        return User

    def authenticate(self, request):
        auth = get_authorization_header(request).split()                                                                        

        if not auth or auth[0].lower() != b'token':
            return None
        if len(auth) == 1:
            logger.error("Invalid token header. no creadential provided")
            msg = "Invalid token header. no creadential provided"
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            logger.error('Invalid token header')
            msg = 'Invalid token header'
            raise exceptions.AuthenticationFailed(msg) 
        try:
            token = auth[1]
            if token == "null":
                logger.error("Null token not allowed")
                msg = "Null token not allowed"
                raise exceptions.AuthenticationFailed(msg)
        except UnicodeError:
            logger.error("Invalid token header. token string should not contain Invalid characters")
            msg = "Invalid token header. token string should not contain Invalid characters"
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        model = self.get_model()
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
            username = payload['username']
            # password = payload['password']
            try:
                user = User.objects.get(username=username,is_delete__in=[False])
            except:
                logger.error('User not found')
                msg = {'Error':'User not found','status':'400'}
                raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            logger.error("Error code signature")
            msg = {'Error':"Error code signature", 'status':'403'}
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            logger.error("Token is Invalid")
            msg = {'Error': "Token is Invalid", 'status':'403'}
            raise exceptions.AuthenticationFailed(msg)
        return (user, token)

    def authenticate_header(self, request):
        return 'Token'