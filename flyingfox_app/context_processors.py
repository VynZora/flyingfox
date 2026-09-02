from .models import Ride


def footer_popular_rides(request):
    """
    Makes active rides available
    in every template.
    """

    popular_rides = (
        Ride.objects
        .filter(is_active=True)
        .order_by("-created_at")[:4]
    )

    return {
        "footer_popular_rides": popular_rides,
    }