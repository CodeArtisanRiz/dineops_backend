from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test Redis cache connection and display configuration details'

    def handle(self, *args, **options):
        # Display Redis configuration
        cache_settings = getattr(settings, 'CACHES', {})
        default_cache = cache_settings.get('default', {})
        
        self.stdout.write("=== Redis Configuration ===")
        if default_cache:
            self.stdout.write(f"Backend: {default_cache.get('BACKEND', 'Not specified')}")
            self.stdout.write(f"Location: {default_cache.get('LOCATION', 'Not specified')}")
            self.stdout.write(f"Key Prefix: {default_cache.get('KEY_PREFIX', 'Not specified')}")
        else:
            self.stdout.write("No default cache configuration found")
        
        self.stdout.write("\n=== Redis Connection Test ===")
        
        try:
            # Test setting a value
            cache.set('test_key', 'Hello Redis!', 30)  # Expire in 30 seconds
            
            # Test getting the value
            value = cache.get('test_key')
            
            if value == 'Hello Redis!':
                self.stdout.write(
                    self.style.SUCCESS('✓ Successfully connected to Redis and set/get a value!')
                )
                self.stdout.write(f'  Retrieved value: {value}')
                
                # Test additional operations
                # Test increment
                cache.set('counter', 0, 30)
                cache.incr('counter')
                counter_value = cache.get('counter')
                if counter_value == 1:
                    self.stdout.write(
                        self.style.SUCCESS('✓ Increment operation successful!')
                    )
                
                # Test delete
                cache.delete('test_key')
                deleted_value = cache.get('test_key')
                if deleted_value is None:
                    self.stdout.write(
                        self.style.SUCCESS('✓ Delete operation successful!')
                    )
                    
                # Test TTL
                cache.set('ttl_test', 'value', 10)
                # Note: Django's cache abstraction doesn't provide a standard way to check TTL
                
                self.stdout.write(
                    self.style.SUCCESS('\nAll Redis operations completed successfully!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('✗ Failed to retrieve the correct value from Redis')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to connect to Redis: {str(e)}')
            )
            logger.exception("Redis connection error")
            
        self.stdout.write("\n=== Test Completed ===")