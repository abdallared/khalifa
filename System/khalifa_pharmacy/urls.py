"""
URL Configuration for Khalifa Pharmacy System
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.http import HttpResponse
from django.views.generic import View
import requests

class UploadsProxyView(View):
    """
    Proxy للملفات المرفوعة من WPPConnect
    """
    def get(self, request, filename):
        try:
            # طلب الملف من WPPConnect server
            wppconnect_url = f"http://localhost:3000/uploads/{filename}"
            response = requests.get(wppconnect_url, stream=True)

            if response.status_code == 200:
                # إرجاع الملف مع الـ content type الصحيح
                django_response = HttpResponse(
                    response.content,
                    content_type=response.headers.get('content-type', 'application/octet-stream')
                )
                return django_response
            else:
                return HttpResponse("File not found", status=404)

        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)


urlpatterns = [
    # Language switcher
    path('i18n/', include('django.conf.urls.i18n')),
    
    # Frontend Pages (HTML) - يجب أن تكون قبل Django Admin
    path('', include('khalifa_pharmacy.urls_frontend')),

    # API Endpoints
    path('api/', include('conversations.urls')),

    # Proxy للملفات المرفوعة
    path('uploads/<str:filename>', UploadsProxyView.as_view(), name='uploads_proxy'),

    # Django Admin - يجب أن يكون في النهاية
    path('django-admin/', admin.site.urls),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

