import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khalifa_pharmacy.settings')
django.setup()

from django.urls import get_resolver, URLPattern, URLResolver

def print_urls(urlpatterns, prefix=''):
    """Recursively print all URL patterns"""
    for pattern in urlpatterns:
        if isinstance(pattern, URLResolver):
            # It's a nested URLconf
            print_urls(pattern.url_patterns, prefix + str(pattern.pattern))
        elif isinstance(pattern, URLPattern):
            # It's an actual URL pattern
            route = prefix + str(pattern.pattern)
            name = pattern.name or 'unnamed'
            print(f'{route:60} -> {name}')

print("Testing URL Configuration...")
print("=" * 80)
print()

try:
    from django.conf import settings
    resolver = get_resolver()
    
    print(f"ROOT_URLCONF: {settings.ROOT_URLCONF}")
    print()
    print("All registered URLs:")
    print("-" * 80)
    print_urls(resolver.url_patterns)
    print()
    print('[OK] URL configuration loaded successfully!')
    
except Exception as e:
    print(f'[ERROR] Failed to load URL configuration: {str(e)}')
    import traceback
    traceback.print_exc()
