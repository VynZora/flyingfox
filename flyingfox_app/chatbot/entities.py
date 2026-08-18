from difflib import SequenceMatcher

from flyingfox_app.models import Ride

from .normalizer import normalize_text


def find_ride(message):

    normalized_message = normalize_text(
        message
    )

    if not normalized_message:
        return None


    rides = (
        Ride.objects
        .filter(
            is_active=True
        )
        .order_by("name")
    )


    # =====================================================
    # 1. EXACT / CONTAINS MATCH
    # =====================================================

    for ride in rides:

        normalized_ride_name = normalize_text(
            ride.name
        )

        if not normalized_ride_name:
            continue


        if (
            normalized_ride_name
            in
            normalized_message
        ):

            return ride


    # =====================================================
    # 2. FUZZY MATCH
    # =====================================================

    best_ride = None
    best_score = 0.0


    for ride in rides:

        normalized_ride_name = normalize_text(
            ride.name
        )

        if not normalized_ride_name:
            continue


        score = SequenceMatcher(
            None,
            normalized_message,
            normalized_ride_name,
        ).ratio()


        if score > best_score:

            best_score = score
            best_ride = ride


    # =====================================================
    # 3. RETURN ONLY GOOD MATCHES
    # =====================================================

    if (
        best_ride
        and
        best_score >= 0.60
    ):

        return best_ride


    return None