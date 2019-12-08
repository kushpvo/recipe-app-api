from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    # instance is the model instance, that is linked to our model serializer
    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return user"""
        password = validated_data.pop('password', None)
        # the super() will call the default i.e. the model serliazer's
        # update function so we can update everything else apart from password
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    # Any variable/field that is made up in the serializer is passed into
    # the function below as a dictionary called attrs
    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _("Unable to authenticate with provided crendetials.")
            raise serializers.ValidationError(msg, code='authentication')

        # Whenever you are overwriting the 'validate' function, you must return
        # the values i.e. attrs at the end of the function
        attrs['user'] = user
        return attrs