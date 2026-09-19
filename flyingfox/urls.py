"""
URL configuration for flyingfox project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from django.http import JsonResponse

from flyingfox_app.sitemaps import (
    StaticViewSitemap,
    RideSitemap,
    BlogSitemap,
    OfferSitemap,
    GalleryPageSitemap,
    BlogPageSitemap,
)


# =====================================================
# HEALTH CHECK
# =====================================================

def health_check(request):
    return JsonResponse({
        "status": "ok"
    })


# =====================================================
# SITEMAPS
# =====================================================

sitemaps = {
    "static": StaticViewSitemap,
    "rides": RideSitemap,
    "blogs": BlogSitemap,
    "offers": OfferSitemap,
    "gallery_pages": GalleryPageSitemap,
    "blog_pages": BlogPageSitemap,
}


# =====================================================
# URL PATTERNS
# =====================================================

urlpatterns = [

    # -------------------------------------------------
    # Health Check
    # -------------------------------------------------
    path(
        "health/",
        health_check,
        name="health_check",
    ),

    # -------------------------------------------------
    # Django Admin
    # -------------------------------------------------
    path(
        "admin/",
        admin.site.urls,
    ),

    # -------------------------------------------------
    # Sitemap
    # -------------------------------------------------
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),

    # -------------------------------------------------
    # Robots.txt
    # -------------------------------------------------
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="robots.txt",
            content_type="text/plain",
        ),
        name="robots_txt",
    ),

    # -------------------------------------------------
    # Main Application
    # Keep this last
    # -------------------------------------------------
    path(
        "",
        include("flyingfox_app.urls"),
    ),
]


# =====================================================
# CUSTOM 404
# =====================================================

handler404 = "flyingfox_app.views.page_404"


# =====================================================
# MEDIA FILES - DEVELOPMENT ONLY
# =====================================================

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )