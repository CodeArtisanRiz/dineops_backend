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
        cache_key = f"view_cache:{request.get_full_path()}"
        if request.method == 'GET' and response.status_code == 200:
            try:
                # Ensure the response content is serializable
                cache.set(cache_key, response.content, timeout=60*15)
                logger.info(f"Response cached for {cache_key}")
            except Exception as e:
                logger.error(f"Error caching response for {cache_key}: {e}")
        elif request.method in ['POST', 'PATCH'] and response.status_code in [200, 201, 204]:
            # Invalidate cache for list and specific item endpoints
            base_path = request.path.split('/')[1]  # Assuming 'foods' is the base path
            list_cache_key = f"view_cache:/{base_path}/fooditems/"
            item_cache_key = f"view_cache:{request.get_full_path()}"
            
            # Delete both list and item cache
            cache.delete(list_cache_key)
            cache.delete(item_cache_key)
            
            logger.info(f"Cache invalidated for {list_cache_key} and {item_cache_key} due to {request.method} request")
            
            # Additional cache invalidation for linked models
            if base_path == 'orders':
                related_cache_key = "view_cache:/foods/tables/"
                cache.delete(related_cache_key)
                logger.info(f"Cache invalidated for {related_cache_key} due to changes in orders")
                
        return response