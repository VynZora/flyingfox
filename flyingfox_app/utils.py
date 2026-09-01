
import requests
from django.conf import settings

# =========================================================
# GENERATE OTP
# =========================================================

import secrets
from datetime import timedelta

from django.utils import timezone

from .models import (
    OTPVerification,
    Booking,
)

from .services.telinfy import send_otp_sms


# =========================================================
# GENERATE OTP
# =========================================================

def generate_otp():

    return str(
        secrets.randbelow(900000)
        + 100000
    )


# =========================================================
# SEND OTP
# =========================================================

def send_otp(phone_number):

    phone_number = str(
        phone_number
    ).strip()

    # =====================================================
    # GENERATE RANDOM 6-DIGIT OTP
    # =====================================================

    otp = generate_otp()

    # =====================================================
    # EXPIRE ALL PREVIOUS UNUSED OTPs
    # =====================================================

    OTPVerification.objects.filter(
        phone_number=phone_number,
        is_verified=False,
    ).update(
        expires_at=timezone.now()
    )

    # =====================================================
    # CREATE NEW OTP RECORD
    # =====================================================

    otp_verification = (
        OTPVerification.objects.create(
            phone_number=phone_number,
            otp=otp,
            expires_at=(
                timezone.now()
                + timedelta(minutes=5)
            ),
        )
    )

    # =====================================================
    # SEND OTP THROUGH TELINFY
    # =====================================================

    try:

        response = send_otp_sms(
            phone_number,
            otp,
        )

    except Exception:

        # SMS submission failed.
        # Delete OTP because customer did not receive it.

        otp_verification.delete()

        raise

    return (
        otp_verification,
        response,
    )


# =========================================================
# VERIFY OTP
# =========================================================

def verify_otp(
    phone_number,
    entered_otp,
):

    phone_number = str(
        phone_number
    ).strip()

    entered_otp = str(
        entered_otp
    ).strip()

    # =====================================================
    # GET LATEST ACTIVE OTP
    # =====================================================

    otp_record = (
        OTPVerification.objects
        .filter(
            phone_number=phone_number,
            is_verified=False,
        )
        .order_by("-created_at")
        .first()
    )

    # =====================================================
    # OTP DOES NOT EXIST
    # =====================================================

    if not otp_record:

        return (
            False,
            "No OTP found. Please request a new OTP.",
        )

    # =====================================================
    # OTP EXPIRED
    # =====================================================

    if timezone.now() >= otp_record.expires_at:

        return (
            False,
            "OTP has expired. Please request a new OTP.",
        )

    # =====================================================
    # TOO MANY ATTEMPTS
    # =====================================================

    if otp_record.attempts >= 5:

        return (
            False,
            "Too many incorrect attempts. "
            "Please request a new OTP.",
        )

    # =====================================================
    # INCORRECT OTP
    # =====================================================

    if otp_record.otp != entered_otp:

        otp_record.attempts += 1

        otp_record.save(
            update_fields=[
                "attempts",
            ]
        )

        return (
            False,
            "Invalid OTP.",
        )

    # =====================================================
    # CORRECT OTP
    # =====================================================

    otp_record.is_verified = True
    otp_record.verified_at = timezone.now()

    otp_record.save(
        update_fields=[
            "is_verified",
            "verified_at",
        ]
    )

    return (
        True,
        "OTP verified successfully.",
    )




def send_ticket_whatsapp(request, ticket):
    """
    Send booking confirmation with the complete generated
    Flying Fox WhatsApp ticket image through Telinfy.

    Template header:
        IMAGE -> complete WhatsApp ticket image

    Body variables:
        {{1}} Customer name
        {{2}} Ticket number
        {{3}} Booking ID
        {{4}} Visit date
        {{5}} Ride summary + confirmed ride schedule
        {{6}} Total riders
        {{7}} Total amount
    """

    # =====================================================
    # BOOKING
    # =====================================================

    booking = (
        Booking.objects
        .prefetch_related(
            "ride_items__ride",
            "ride_items__weight_groups",
            "ride_items__allocated_slots",
        )
        .get(
            pk=ticket.booking.pk
        )
    )

    # =====================================================
    # CUSTOMER PHONE
    # =====================================================

    if not booking.customer_phone:

        print(
            "WHATSAPP ERROR: "
            "Customer phone is empty."
        )

        return False

    phone = (
        booking.customer_phone
        .strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )

    # =====================================================
    # NORMALIZE PHONE
    # =====================================================

    # 9633390345 -> 919633390345
    if (
        len(phone) == 10
        and phone.isdigit()
    ):

        phone = f"91{phone}"

    # 919633390345
    elif (
        len(phone) == 12
        and phone.startswith("91")
        and phone.isdigit()
    ):

        pass

    # +919633390345 -> 919633390345
    elif (
        len(phone) == 13
        and phone.startswith("+91")
        and phone[1:].isdigit()
    ):

        phone = phone[1:]

    else:

        print(
            "WHATSAPP ERROR: "
            "Invalid phone number:",
            phone,
        )

        return False

    telinfy_phone = (
        f"+{phone}"
    )

    # =====================================================
    # TELINFY SETTINGS
    # =====================================================

    api_key = getattr(
        settings,
        "TELINFY_API_KEY",
        "",
    )

    base_url = getattr(
        settings,
        "TELINFY_BASE_URL",
        "https://hub.telinfy.com/unified/developer",
    )

    template_name = getattr(
        settings,
        "TELINFY_WHATSAPP_TEMPLATE",
        "booking_confirmation_qr",
    )

    language_code = getattr(
        settings,
        "TELINFY_WHATSAPP_LANGUAGE",
        "en",
    )

    if not api_key:

        print(
            "WHATSAPP ERROR: "
            "TELINFY_API_KEY is missing."
        )

        return False

    # =====================================================
    # CHECK COMPLETE WHATSAPP TICKET IMAGE
    # =====================================================

    if not ticket.whatsapp_ticket_image:

        print(
            "WHATSAPP ERROR: "
            "WhatsApp ticket image is missing."
        )

        return False

    if not ticket.whatsapp_ticket_image.name:

        print(
            "WHATSAPP ERROR: "
            "WhatsApp ticket image has no file name."
        )

        return False

    # =====================================================
    # BUILD PUBLIC TICKET IMAGE URL
    # =====================================================

    try:

        ticket_image_relative_url = (
            ticket.whatsapp_ticket_image.url
        )

        public_base_url = getattr(
            settings,
            "PUBLIC_BASE_URL",
            "",
        )

        if not public_base_url:

            print(
                "WHATSAPP ERROR: "
                "PUBLIC_BASE_URL is missing."
            )

            return False

        ticket_image_url = (
            f"{public_base_url.rstrip('/')}"
            f"{ticket_image_relative_url}"
        )

    except Exception as error:

        print(
            "WHATSAPP ERROR: "
            "Unable to build public "
            "ticket image URL."
        )

        print(
            "ERROR:",
            repr(error),
        )

        return False

    # =====================================================
    # VALIDATE PUBLIC URL
    # =====================================================

    if (
        "localhost"
        in ticket_image_url.lower()
        or
        "127.0.0.1"
        in ticket_image_url
    ):

        print(
            "WHATSAPP ERROR: "
            "Ticket image URL is localhost "
            "and cannot be downloaded by "
            "Telinfy/WhatsApp."
        )

        print(
            "TICKET IMAGE URL:",
            ticket_image_url,
        )

        return False

    # =====================================================
    # FORMAT SLOT TIME
    # =====================================================

    def format_slot_time(value):

        if not value:
            return ""

        return (
            value.strftime(
                "%I:%M %p"
            )
            .lstrip("0")
        )

    # =====================================================
    # RIDE SUMMARY + CONFIRMED TIME SCHEDULE
    #
    # This complete value goes into WhatsApp {{5}}.
    # =====================================================

    ride_lines = []

    for item in booking.ride_items.all():

        if not item.ride:
            continue

        quantity = int(
            item.quantity
            or
            0
        )

        participant_word = (
            "participant"
            if quantity == 1
            else "participants"
        )

        # -------------------------------------------------
        # RIDE NAME + TOTAL PARTICIPANTS
        # -------------------------------------------------

        ride_lines.append(
            f"{item.ride.name} - "
            f"{quantity} {participant_word}"
        )

        # -------------------------------------------------
        # CONFIRMED SLOT ALLOCATIONS ONLY
        # -------------------------------------------------

        confirmed_slots = [

            slot

            for slot
            in item.allocated_slots.all()

            if slot.status == "confirmed"
        ]

        confirmed_slots.sort(
            key=lambda slot:
                slot.slot_start_time
        )

        # -------------------------------------------------
        # ADD SLOT SCHEDULE
        # -------------------------------------------------

        if confirmed_slots:

            for slot in confirmed_slots:

                start_time = (
                    format_slot_time(
                        slot.slot_start_time
                    )
                )

                end_time = (
                    format_slot_time(
                        slot.slot_end_time
                    )
                )

                slot_riders = int(
                    slot.participant_count
                    or
                    0
                )

                rider_word = (
                    "rider"
                    if slot_riders == 1
                    else "riders"
                )

                ride_lines.append(
                    f"{start_time} - "
                    f"{end_time}: "
                    f"{slot_riders} {rider_word}"
                )

        else:

            # This should normally not happen for a
            # successfully confirmed booking, but we avoid
            # displaying false schedule information.
            ride_lines.append(
                "Schedule unavailable"
            )

        # Blank line between rides.
        ride_lines.append("")

    # =====================================================
    # FINAL {{5}} VALUE
    # =====================================================
    ride_summary = " | ".join(
        line.strip()
        for line in ride_lines
        if line and line.strip()
    )

    ride_summary = (
          ride_summary
          .replace("\n", " ")
          .replace("\r", " ")
          .replace("\t", " ")
          .strip()
        )

    while "  " in ride_summary:
         ride_summary = ride_summary.replace("  ", " ")

    if not ride_summary:
        ride_summary = (
        "Adventure details are included "
        "in your ticket."
    )

    # =====================================================
    # TEMPLATE VALUES
    # =====================================================

    customer_name = (
        booking.customer_name
        or
        ""
    )

    ticket_number = str(
        ticket.ticket_number
        or
        ""
    )

    booking_id_value = str(
        booking.booking_id
        or
        ""
    )

    visit_date = (
        booking.booking_date.strftime(
            "%d-%m-%Y"
        )
        if booking.booking_date
        else ""
    )

    # =====================================================
    # TOTAL RIDERS
    # =====================================================

    total_riders_value = sum(

        int(
            item.quantity
            or
            0
        )

        for item
        in booking.ride_items.all()

        if item.ride
    )

    total_riders = str(
        total_riders_value
    )

    # =====================================================
    # TOTAL AMOUNT
    # =====================================================

    total_amount = str(
        booking.total_amount
        or
        ""
    )

    # =====================================================
    # TELINFY URL
    # =====================================================

    url = (
        f"{base_url.rstrip('/')}"
        "/api/v1/whatsapp/campaigns/send"
    )

    # =====================================================
    # HEADERS
    # =====================================================

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    # =====================================================
    # BODY PARAMETERS
    #
    # IMPORTANT:
    # Keep exactly 7 parameters because the approved
    # WhatsApp template has {{1}} through {{7}}.
    # =====================================================

    body_parameters = [

        # {{1}} Customer name
        {
            "type": "text",
            "text": str(
                customer_name
            ),
        },

        # {{2}} Ticket number
        {
            "type": "text",
            "text": str(
                ticket_number
            ),
        },

        # {{3}} Booking ID
        {
            "type": "text",
            "text": str(
                booking_id_value
            ),
        },

        # {{4}} Visit date
        {
            "type": "text",
            "text": str(
                visit_date
            ),
        },

        # {{5}} Ride details + confirmed schedule
        {
            "type": "text",
            "text": str(
                ride_summary
            ),
        },

        # {{6}} Total riders
        {
            "type": "text",
            "text": str(
                total_riders
            ),
        },

        # {{7}} Total amount
        {
            "type": "text",
            "text": str(
                total_amount
            ),
        },
    ]

    # =====================================================
    # PAYLOAD
    # =====================================================

    payload = {
        "phoneNumber": telinfy_phone,

        "template": {
            "name": template_name,

            "language": {
                "code": language_code,
            },

            "components": [

                # =========================================
                # IMAGE HEADER
                # =========================================

                {
                    "type": "header",

                    "parameters": [
                        {
                            "type": "image",

                            "image": {
                                "link":
                                    ticket_image_url,
                            },
                        }
                    ],
                },

                # =========================================
                # BODY
                # =========================================

                {
                    "type": "body",

                    "parameters":
                        body_parameters,
                },
            ],
        },
    }

    # =====================================================
    # DEBUG REQUEST
    # =====================================================

    print(
        "\n========================================"
    )

    print(
        "TELINFY WHATSAPP TICKET REQUEST"
    )

    print(
        "========================================"
    )

    print(
        "URL:",
        url,
    )

    print(
        "TO:",
        telinfy_phone,
    )

    print(
        "TEMPLATE:",
        template_name,
    )

    print(
        "LANGUAGE:",
        language_code,
    )

    print(
        "TICKET IMAGE FILE:",
        ticket.whatsapp_ticket_image.name,
    )

    print(
        "TICKET IMAGE URL:",
        ticket_image_url,
    )

    print(
        "BODY PARAMETER COUNT:",
        len(
            body_parameters
        ),
    )

    print(
        "BODY PARAMETERS:"
    )

    for index, parameter in enumerate(
        body_parameters,
        start=1,
    ):

        print(
            f"  {{{{{index}}}}}:",
            parameter["text"],
        )

    # =====================================================
    # EXTRA SCHEDULE DEBUG
    # =====================================================

    print(
        "----------------------------------------"
    )

    print(
        "WHATSAPP RIDE SCHEDULE {{5}}:"
    )

    print(
        ride_summary
    )

    print(
        "========================================"
    )

    # =====================================================
    # SEND REQUEST
    # =====================================================

    try:

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30,
        )

        # =================================================
        # DEBUG RESPONSE
        # =================================================

        print(
            "\n========================================"
        )

        print(
            "TELINFY WHATSAPP TICKET RESULT"
        )

        print(
            "========================================"
        )

        print(
            "HTTP STATUS:",
            response.status_code,
        )

        print(
            "RESPONSE:",
            response.text,
        )

        print(
            "========================================\n"
        )

        # =================================================
        # JSON RESPONSE
        # =================================================

        try:

            response_data = (
                response.json()
            )

        except ValueError:

            response_data = {}

        # =================================================
        # SUCCESS
        # =================================================

        if (
            response.ok
            and
            response_data.get(
                "success"
            ) is True
        ):

            data = (
                response_data.get(
                    "data",
                    {}
                )
                or
                {}
            )

            ticket.whatsapp_sent = True

            ticket.save(
                update_fields=[
                    "whatsapp_sent",
                ]
            )

            print(
                "WHATSAPP TICKET ACCEPTED "
                "BY TELINFY"
            )

            print(
                "RECORD ID:",
                data.get(
                    "recordId"
                ),
            )

            print(
                "QUEUE STATUS:",
                data.get(
                    "queueStatus"
                ),
            )

            print(
                "PHONE:",
                data.get(
                    "phoneNumber"
                ),
            )

            print(
                "TEMPLATE:",
                data.get(
                    "templateName"
                ),
            )

            return True

        # =================================================
        # TELINFY FAILED
        # =================================================

        print(
            "WHATSAPP TICKET SEND FAILED"
        )

        print(
            "STATUS:",
            response.status_code,
        )

        print(
            "RESPONSE:",
            response.text,
        )

        return False

    # =====================================================
    # REQUEST ERROR
    # =====================================================

    except requests.RequestException as error:

        print(
            "\n========================================"
        )

        print(
            "TELINFY WHATSAPP TICKET "
            "REQUEST ERROR"
        )

        print(
            "========================================"
        )

        print(
            "TYPE:",
            type(error).__name__,
        )

        print(
            "ERROR:",
            repr(error),
        )

        print(
            "========================================\n"
        )

        return False