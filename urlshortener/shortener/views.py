from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ShortURL, URLStats
from .serializers import ShortURLSerializer, URLStatsSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from django.db.models import F
import logging

logger = logging.getLogger(__name__)


def index(request):
    """Render the URL shortening web interface"""
    if request.method == 'POST':
        original_url = request.POST.get('original_url')
        validity = request.POST.get('validity', 30)
        shortcode = request.POST.get('shortcode')
        
        logger.info(f"Form data received: original_url={original_url}, validity={validity}, shortcode={shortcode}")
        
        # Create a serializer with the data
        serializer = ShortURLSerializer(
            data={
                'original_url': original_url,
                'validity': validity,
                'shortcode': shortcode
            },
            context={'validity': validity}
        )
        
        if serializer.is_valid():
            logger.info(f"Serializer is valid. Data: {serializer.validated_data}")
            try:
                with transaction.atomic():
                    short_url = serializer.save()
                    logger.info(f"Short URL created successfully: {short_url.short_code}")
                    
                response_data = {
                    'shortlink': request.build_absolute_uri('/') + short_url.short_code,
                    'expiry': short_url.expires_at.isoformat(),
                    'original_url': short_url.original_url
                }
                
                return render(request, 'shortener/index.html', {
                    'result': response_data,
                    'success': True
                })
            except Exception as e:
                logger.error(f"Error creating short URL: {str(e)}", exc_info=True)
                return render(request, 'shortener/index.html', {
                    'error': str(e)
                })
        else:
            logger.error(f"Serializer validation failed: {serializer.errors}")
            return render(request, 'shortener/index.html', {
                'error': serializer.errors
            })
    
    return render(request, 'shortener/index.html')


class CreateShortURL(APIView):
    def get(self, request):
        return Response(
            {
                "message": "Use POST method to create a short URL",
                "example_request": {
                    "url": "https://example.com/very/long/url",
                    "validity": 30,
                    "shortcode": "optional_code"
                }
            },
            status=status.HTTP_200_OK
        )
    def get(self, request):
        return Response(
            {
                "message": "Use POST method to create a short URL",
                "example_request": {
                    "url": "https://example.com/very/long/url",
                    "validity": 30,
                    "shortcode": "optional_code"
                }
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = ShortURLSerializer(
            data=request.data,
            context={'validity': request.data.get('validity', 30)}
        )

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    short_url = serializer.save()

                    response_data = {
                        'shortlink': request.build_absolute_uri('/') + short_url.short_code,
                        'expiry': short_url.expires_at.isoformat(),
                        'original_url': short_url.original_url
                    }

                    logger.info(f"Created short URL: {short_url.short_code}")
                    return Response(response_data, status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.error(f"Error creating short URL: {str(e)}")
                return Response(
                    {'error': 'Could not create short URL'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        logger.error(f"Validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RedirectURL(APIView):
    def get(self, request, short_code):
        try:
            short_url = get_object_or_404(ShortURL, short_code=short_code)

            if timezone.now() > short_url.expires_at:
                logger.error(f"Expired short URL accessed: {short_code}")
                return Response(
                    {
                        'error': 'Short URL has expired',
                        'original_url': short_url.original_url,
                        'expired_at': short_url.expires_at.isoformat()
                    },
                    status=status.HTTP_410_GONE
                )

            with transaction.atomic():
                URLStats.objects.create(
                    short_url=short_url,
                    referrer=request.META.get('HTTP_REFERER'),
                    ip_address=self._get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    country=self._get_country_from_ip(request.META.get('REMOTE_ADDR'))
                )
                short_url.clicks_count = F('clicks_count') + 1
                short_url.save()

            logger.info(f"Redirecting {short_code} to {short_url.original_url}")
            return redirect(short_url.original_url)

        except Exception as e:
            logger.error(f"Error redirecting {short_code}: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

    def _get_country_from_ip(self, ip):
        # Implement with GeoIP2 in production
        return "Unknown"


class URLStatsView(APIView):
    def get(self, request, short_code):
        cache_key = f"url_stats_{short_code}"
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.info(f"Retrieved stats for {short_code} from cache")
            return Response(cached_data)

        try:
            short_url = get_object_or_404(ShortURL, short_code=short_code)
            stats = URLStats.objects.filter(short_url=short_url)[:100]  # Limit to 100 most recent

            response_data = {
                'original_url': short_url.original_url,
                'short_code': short_url.short_code,
                'created_at': short_url.created_at.isoformat(),
                'expires_at': short_url.expires_at.isoformat(),
                'total_clicks': short_url.clicks_count,
                'recent_clicks': URLStatsSerializer(stats, many=True).data
            }

            cache.set(cache_key, response_data, 300)  # Cache for 5 minutes

            logger.info(f"Retrieved stats for short URL: {short_code}")
            return Response(response_data)

        except Exception as e:
            logger.error(f"Error getting stats for {short_code}: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )