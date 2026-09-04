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
                "slug": obj.slug
            },
        )


# =========================================================
# BLOGS
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
                "slug": obj.slug
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
                "slug": obj.slug
            },
        )