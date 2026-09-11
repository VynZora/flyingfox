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
# CUSTOMER BOOKING START TIMES
#
# These are the actual start times that can be offered
# through the booking system.
#
# IMPORTANT:
# Keep these as Python time objects because the rest of
# the slot system already works with time objects.
# =========================================================

RIDE_START_TIMES = [

    time(8, 30),

    time(9, 30),

    time(10, 30),

    time(11, 30),

    time(13, 0),

    time(14, 0),

    time(15, 0),

    time(16, 0),

]



# =========================================================
# GENERATE RIDE SLOTS
# =========================================================

def generate_ride_slots(ride):

    # =====================================================
    # SLOT DURATION
    #
    # Each ride can still have its own duration.
    #
    # Example:
    # 60 minutes
    # 30 minutes
    # etc.
    # =====================================================

    slot_duration = (
        ride.slot_duration_minutes
        or
        60
    )


    dummy_date = (
        date.today()
    )


    closing_datetime = (
        datetime.combine(
            dummy_date,
            RIDE_CLOSING_TIME,
        )
    )


    slots = []


    # =====================================================
    # BUILD SLOT FROM EACH CONFIGURED START TIME
    # =====================================================

    for start_time in RIDE_START_TIMES:

        start_datetime = (
            datetime.combine(
                dummy_date,
                start_time,
            )
        )


        end_datetime = (
            start_datetime
            +
            timedelta(
                minutes=slot_duration
            )
        )


        # =================================================
        # SAFETY:
        # DO NOT CREATE SLOT PAST CLOSING TIME
        # =================================================

        if (
            end_datetime
            >
            closing_datetime
        ):

            continue


        slots.append(
            {
                "start_time":
                    start_datetime.time(),

                "end_time":
                    end_datetime.time(),
            }
        )


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

    # =====================================================
    # VALIDATE QUANTITY
    # =====================================================

    if requested_quantity <= 0:

        return {
            "available":
                False,

            "allocations":
                [],

            "message":
                (
                    "Participant quantity must "
                    "be greater than zero."
                ),
        }


    # =====================================================
    # GET CURRENT LIVE AVAILABILITY
    # =====================================================

    available_slots = (
        get_available_slots(
            ride=ride,
            booking_date=booking_date,
        )
    )


    remaining_people = (
        requested_quantity
    )


    allocations = []


    started = (
        False
    )


    previous_end_time = (
        None
    )


    # =====================================================
    # WALK FORWARD FROM SELECTED START
    # =====================================================

    for slot in available_slots:

        # -------------------------------------------------
        # FIND SELECTED START
        # -------------------------------------------------

        if (
            slot["start_time"]
            ==
            selected_start_time
        ):

            started = (
                True
            )


        if not started:

            continue


        # -------------------------------------------------
        # EVERYONE ALREADY ALLOCATED
        # -------------------------------------------------

        if (
            remaining_people
            <=
            0
        ):

            break


        # -------------------------------------------------
        # IMPORTANT:
        # AFTER FIRST ALLOCATION, NEXT SLOT MUST START
        # EXACTLY WHEN PREVIOUS SLOT ENDED.
        #
        # This prevents:
        #
        # 11:30 - 12:30
        # then
        # 13:00 - 14:00
        #
        # from being treated as one continuous block.
        # -------------------------------------------------

        if (
            previous_end_time
            is not None
            and
            slot["start_time"]
            !=
            previous_end_time
        ):

            break


        # -------------------------------------------------
        # SLOT FULL
        # -------------------------------------------------

        if (
            slot["remaining"]
            <=
            0
        ):

            break


        # -------------------------------------------------
        # ALLOCATE
        # -------------------------------------------------

        allocated_count = (
            min(
                remaining_people,
                slot["remaining"],
            )
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


        remaining_people -= (
            allocated_count
        )


        previous_end_time = (
            slot["end_time"]
        )


    # =====================================================
    # COULD NOT FIT COMPLETE GROUP
    # =====================================================

    if (
        remaining_people
        >
        0
    ):

        return {
            "available":
                False,

            "allocations":
                [],

            "message":
                (
                    "There is not enough consecutive "
                    "slot capacity for all participants."
                ),
        }


    # =====================================================
    # SUCCESS
    # =====================================================

    return {
        "available":
            True,

        "allocations":
            allocations,

        "message":
            "",
    }