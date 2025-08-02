from rest_framework import serializers
from .models import ShortURL, URLStats
from datetime import datetime, timedelta


class ShortURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortURL
        fields = ['original_url', 'short_code', 'expires_at']
        extra_kwargs = {
            'short_code': {'required': False},
            'expires_at': {'read_only': True}
        }

    def validate_original_url(self, value):
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("URL must start with http:// or https://")
        return value

    def validate_short_code(self, value):
        if value and not value.isalnum():
            raise serializers.ValidationError("Short code must be alphanumeric")
        return value

    def create(self, validated_data):
        validity = int(self.context.get('validity', 30))
        expires_at = datetime.now() + timedelta(minutes=validity)

        short_url = ShortURL(
            original_url=validated_data['original_url'],
            short_code=validated_data.get('short_code'),
            expires_at=expires_at
        )
        short_url.save()
        return short_url


class URLStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = URLStats
        fields = ['clicked_at', 'referrer', 'ip_address', 'country']