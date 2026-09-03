"""
URL configuration for flyingfox project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

from flyingfox_app.sitemaps import (
    StaticViewSitemap,
    RideSitemap,
    BlogSitemap,
    OfferSitemap,
)


sitemaps = {
    "static": StaticViewSitemap,
    "rides": RideSitemap,
    "blogs": BlogSitemap,
    "offers": OfferSitemap,
}


urlpatterns = [
    path("admin/", admin.site.urls),

    # Sitemap
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),

    # Robots.txt
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="robots.txt",
            content_type="text/plain",
        ),
        name="robots_txt",
    ),

    # Main application
    path("", include("flyingfox_app.urls")),
]


handler404 = "flyingfox_app.views.page_404"


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )