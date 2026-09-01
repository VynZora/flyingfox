from datetime import datetime, date, time, timedelta

from django.db import models
from django.db.models import Sum
from django.utils import timezone

from flyingfox_app.models import BookingRideSlot


# =========================================================
# OPERATING HOURS
# =========================================================

RIDE_OPENING_TIME = time(8, 30)

RIDE_CLOSING_TIME = time(18, 30)


# =========================================================
# GENERATE RIDE SLOTS
# =========================================================

def generate_ride_slots(ride):

    slot_duration = (
        ride.slot_duration_minutes
        or
        60
    )

    dummy_date = date.today()

    current = datetime.combine(
        dummy_date,
        RIDE_OPENING_TIME,
    )

    closing = datetime.combine(
        dummy_date,
        RIDE_CLOSING_TIME,
    )

    slots = []

    while current < closing:

        end = current + timedelta(
            minutes=slot_duration
        )

        if end > closing:
            break

        slots.append(
            {
                "start_time": current.time(),
                "end_time": end.time(),
            }
        )

        current = end

    return slots


# =========================================================
# BOOKED PARTICIPANTS
# =========================================================

def get_booked_quantity(
    *,
    ride,
    booking_date,
    slot_start_time,
):

    now = timezone.now()

    result = (
        BookingRideSlot.objects
        .filter(
            booking_item__ride=ride,
            booking_item__booking__booking_date=booking_date,
            slot_start_time=slot_start_time,
        )
        .filter(
            models.Q(
                status="confirmed"
            )
            |
            models.Q(
                status="held",
                hold_expires_at__gt=now,
            )
        )
        .aggregate(
            total=Sum(
                "participant_count"
            )
        )
    )

    return result["total"] or 0


# =========================================================
# REMAINING CAPACITY
# =========================================================

def get_slot_remaining_capacity(
    *,
    ride,
    booking_date,
    slot_start_time,
):

    booked = get_booked_quantity(
        ride=ride,
        booking_date=booking_date,
        slot_start_time=slot_start_time,
    )

    capacity = ride.capacity_per_slot

    remaining = max(
        capacity - booked,
        0,
    )

    return {
        "capacity": capacity,
        "booked": booked,
        "remaining": remaining,
    }


# =========================================================
# ALL SLOT AVAILABILITY
# =========================================================

def get_available_slots(
    *,
    ride,
    booking_date,
):

    generated_slots = generate_ride_slots(
        ride
    )

    results = []

    for slot in generated_slots:

        capacity_data = (
            get_slot_remaining_capacity(
                ride=ride,
                booking_date=booking_date,
                slot_start_time=slot["start_time"],
            )
        )

        results.append(
            {
                "start_time":
                    slot["start_time"],

                "end_time":
                    slot["end_time"],

                "capacity":
                    capacity_data["capacity"],

                "booked":
                    capacity_data["booked"],

                "remaining":
                    capacity_data["remaining"],

                "available":
                    capacity_data["remaining"] > 0,
            }
        )

    return results


# =========================================================
# SPLIT PARTICIPANTS ACROSS CONSECUTIVE SLOTS
# =========================================================

def allocate_participants_from_start_slot(
    *,
    ride,
    booking_date,
    requested_quantity,
    selected_start_time,
):

    if requested_quantity <= 0:

        return {
            "available": False,
            "allocations": [],
            "message": (
                "Participant quantity must "
                "be greater than zero."
            ),
        }

    available_slots = get_available_slots(
        ride=ride,
        booking_date=booking_date,
    )

    remaining_people = requested_quantity

    allocations = []

    started = False

    for slot in available_slots:

        if (
            slot["start_time"]
            ==
            selected_start_time
        ):
            started = True

        if not started:
            continue

        if remaining_people <= 0:
            break

        if slot["remaining"] <= 0:
            break

        allocated_count = min(
            remaining_people,
            slot["remaining"],
        )

        allocations.append(
            {
                "start_time":
                    slot["start_time"],

                "end_time":
                    slot["end_time"],

                "participant_count":
                    allocated_count,
            }
        )

        remaining_people -= allocated_count

    if remaining_people > 0:

        return {
            "available": False,
            "allocations": [],
            "message": (
                "There is not enough consecutive "
                "slot capacity for all participants."
            ),
        }

    return {
        "available": True,
        "allocations": allocations,
        "message": "",
    }