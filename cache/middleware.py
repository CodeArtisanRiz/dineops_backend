# common/middleware.py
import logging
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
import json

logger = logging.getLogger(__name__)

class CacheMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method == 'GET':
            cache_key = f"view_cache:{request.get_full_path()}"
            cached_response = cache.get(cache_key)
            if cached_response:
                logger.info(f"Cache hit for {cache_key}")
                # Decode bytes to string and then parse JSON
                cached_data = json.loads(cached_response.decode('utf-8'))
                return JsonResponse(cached_data, safe=False)
            else:
                logger.info(f"Cache miss for {cache_key}")

    def process_response(self, request, response):
        if request.method == 'GET' and response.status_code == 200:
            cache_key = f"view_cache:{request.get_full_path()}"
            try:
                # Ensure the response content is serializable
                cache.set(cache_key, response.content, timeout=60*15)
                logger.info(f"Response cached for {cache_key}")
            except Exception as e:
                logger.error(f"Error caching response for {cache_key}: {e}")
        return response