from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("mainapp.urls")),
    # No nginx in front on Railway, so Django serves user uploads directly.
    path(
        f"{settings.MEDIA_URL.lstrip('/')}<path:path>",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
