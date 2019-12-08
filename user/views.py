from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for the user"""
    serializer_class = AuthTokenSerializer
    # The renderer_classes sets the endpoint so that we
    # can view it in the browser - browsable api
    # If you don't do this, you have to make a
    # POST request via postman or some other client
    # to get the auth token.
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    # authetication is the mechanisim by which the auth happens
    # it could be cookie auth, token auth, etc
    authentication_classes = (authentication.TokenAuthentication,)
    # permissions are the level of access user has
    # user must be authenticated to use the api
    permission_classes = (permissions.IsAuthenticated,)

    # overwriting the get_object and return the user that is authenticated
    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user
