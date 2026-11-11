import os
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .views import index_spa_view


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "service": "Doc PII Auditor API",
            "version": "1.0.0",
            "status": "healthy",
            "celery_eager": settings.CELERY_TASK_ALWAYS_EAGER
        })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', HealthCheckView.as_view(), name='health_check'),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/documents/', include('apps.documents.urls')),
]

# Assets from frontend dist
frontend_assets_dir = settings.BASE_DIR.parent / 'frontend' / 'dist' / 'assets'
if os.path.exists(frontend_assets_dir):
    urlpatterns += [
        path('assets/<path:path>', serve, {'document_root': frontend_assets_dir}),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# SPA fallback
urlpatterns += [
    re_path(r'^(?!api/|admin/|media/|assets/).*$', index_spa_view, name='spa_root'),
]
