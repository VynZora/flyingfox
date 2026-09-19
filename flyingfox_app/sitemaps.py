import math

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone

from .models import Ride, Blog, Offer


# =========================================================
# STATIC PAGES
# =========================================================

class StaticViewSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return [
            "home",
            "rides",
            "about",
            "blog",
            "offers",
            "gallery",
            "contact",
            "bookings",
            "user_signin",
            "terms_conditions",
            "privacy_policy",
        ]

    def location(self, item):
        return reverse(item)


# =========================================================
# RIDES
# =========================================================

class RideSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Ride.objects.filter(
            is_active=True
        )

    def location(self, obj):
        return reverse(
            "ride_detail",
            kwargs={
                "slug": obj.slug,
            },
        )


# =========================================================
# BLOG DETAILS
# =========================================================

class BlogSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Blog.objects.all()

    def location(self, obj):
        return reverse(
            "blog_detail",
            kwargs={
                "slug": obj.slug,
            },
        )


# =========================================================
# OFFERS
# =========================================================

class OfferSitemap(Sitemap):
    protocol = "https"
    changefreq = "daily"
    priority = 0.7

    def items(self):
        today = timezone.localdate()

        return Offer.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        )

    def location(self, obj):
        return reverse(
            "frontend_offer_detail",
            kwargs={
                "slug": obj.slug,
            },
        )


# =========================================================
# GALLERY CATEGORY PAGES
# =========================================================

class GalleryPageSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return [
            "/gallery/normal-zipline/",
            "/gallery/superman-zipline/",
        ]

    def location(self, item):
        return item


# =========================================================
# BLOG PAGINATION
# =========================================================

class BlogPageSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        blogs_per_page = 6

        total_blogs = Blog.objects.count()

        total_pages = math.ceil(
            total_blogs / blogs_per_page
        )

        # Page 1 is already included as /blog/
        # through StaticViewSitemap.
        return range(
            2,
            total_pages + 1,
        )

    def location(self, page):
        return reverse(
            "blog_page",
            kwargs={
                "page": page,
            },
        )