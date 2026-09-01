from django.db import models

# Create your models here.
from django.db import models
from django.utils.text import slugify
from django.utils import timezone


from django.contrib.auth.models import User
import uuid
import secrets


from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal



WEIGHT_RANGES = {
    "30-50": {
        "label": "30–50 KG",
        "min_weight": 30,
        "max_weight": 50,
    },

    "50-70": {
        "label": "50–70 KG",
        "min_weight": 50,
        "max_weight": 70,
    },

    "70-90": {
        "label": "70–90 KG",
        "min_weight": 70,
        "max_weight": 90,
    },

    "90-110": {
        "label": "90–110 KG",
        "min_weight": 90,
        "max_weight": 110,
    },
}

WEIGHT_RANGE_CHOICES = [
    (
        key,
        data["label"],
    )
    for key, data
    in WEIGHT_RANGES.items()
]








from django.db import models
from django.utils.text import slugify


class OptimizedImageModel(models.Model):
    image_fields = []

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for field in self.image_fields:
            image_field = getattr(self, field, None)
            if image_field and hasattr(image_field, "path"):
                try:
                    from .utils.image_optimizer import optimize_image
                    optimize_image(image_field.path)
                except Exception:
                    pass





class GalleryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Gallery Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while GalleryCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class GalleryItem(OptimizedImageModel):

    image_fields = ["image"]

    category = models.ForeignKey(
        GalleryCategory,
        on_delete=models.CASCADE,
        related_name="items"
    )

    image = models.ImageField(
        upload_to="gallery/images/",
        blank=True,
        null=True
    )

    video = models.FileField(
        upload_to="gallery/videos/",
        blank=True,
        null=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):

        if self.image:
            return f"{self.category.name} - Image"

        if self.video:
            return f"{self.category.name} - Video"

        return self.category.name

    
class Blog(OptimizedImageModel):
    image_fields = ["image"]

    image = models.ImageField(
        upload_to="blogs/"
    )

    slug = models.SlugField(
        unique=True,
        blank=True, max_length=220,
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Blog.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)    




class ContactMessage(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.phone}"



class UserProfile(models.Model):

    # =====================================================
    # GENDER
    # =====================================================

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]


    # =====================================================
    # BASIC INFORMATION
    # =====================================================

    full_name = models.CharField(
        max_length=150,
        blank=True,
        default=""
    )


    # Mobile OTP is currently your login identity
    phone = models.CharField(
        max_length=20,
        unique=True,
        db_index=True
    )


    # User can add email after login
    email = models.EmailField(
        unique=True,
        blank=True,
        null=True
    )


    # =====================================================
    # PROFILE INFORMATION
    # =====================================================

    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True,
        default=""
    )


    date_of_birth = models.DateField(
        blank=True,
        null=True
    )


    address = models.TextField(
        blank=True,
        default=""
    )


    pincode = models.CharField(
        max_length=10,
        blank=True,
        default=""
    )


    region = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )


    # =====================================================
    # COMMUNICATION PREFERENCES
    # =====================================================

    whatsapp_updates = models.BooleanField(
        default=True
    )


    email_updates = models.BooleanField(
        default=False
    )


    # =====================================================
    # VERIFICATION
    # =====================================================

    phone_verified = models.BooleanField(
        default=False
    )


    # =====================================================
    # TIMESTAMPS
    # =====================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    updated_at = models.DateTimeField(
        auto_now=True
    )


    class Meta:
        ordering = ["-created_at"]


    def __str__(self):

        if self.full_name:
            return f"{self.full_name} - {self.phone}"

        return self.phone



class Ride(models.Model):

    name = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    description = models.TextField()

    duration = models.CharField(
        max_length=100,
        help_text="Example: 30 Minutes / 1 Hour"
    )

    # =====================================================
    # SLOT SETTINGS
    # =====================================================

    capacity_per_slot = models.PositiveIntegerField(
        default=15,
        help_text=(
            "Maximum number of participants allowed "
            "in one time slot for this ride."
        ),
    )

    slot_duration_minutes = models.PositiveIntegerField(
        default=60,
        help_text=(
            "Duration of one booking slot in minutes."
        ),
    )

    safety_notes = models.TextField(
        blank=True
    )

    is_featured = models.BooleanField(
        default=False,
        help_text="Enable this to show the ride in featured sections."
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        if not self.slug:

            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Ride.objects.filter(
                slug=slug
            ).exclude(
                pk=self.pk
            ).exists():

                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class RideMedia(OptimizedImageModel):

    MEDIA_TYPE_CHOICES = [
        ("image", "Image"),
        ("video", "Video"),
    ]

    image_fields = ["image"]

    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name="media",
    )

    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        default="image",
    )

    image = models.ImageField(
        upload_to="rides/images/",
        blank=True,
        null=True,
    )

    video = models.FileField(
        upload_to="rides/videos/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ride.name} - {self.get_media_type_display()}"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.media_type == "image" and not self.image:
            raise ValidationError({
                "image": "Please upload an image."
            })

        if self.media_type == "video" and not self.video:
            raise ValidationError({
                "video": "Please upload a video."
            })

class RidePrice(models.Model):

    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name="prices"
    )

    start_date = models.DateField()

    end_date = models.DateField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("99999999.99")),
        ]
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return (
            f"{self.ride.name} - "
            f"{self.start_date} to {self.end_date} - "
            f"₹{self.price}"
        )


class Booking(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("payment_pending", "Payment Pending"),
        ("confirmed", "Confirmed"),
        ("payment_failed", "Payment Failed"),
        ("cancelled", "Cancelled"),
        ("checked_in", "Checked In"),
        ("refunded", "Refunded"),
    ]

    booking_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    # =====================================================
    # USER
    # =====================================================

    user = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
    )

    # =====================================================
    # CUSTOMER DETAILS
    # =====================================================

    customer_name = models.CharField(
        max_length=150,
    )

    customer_email = models.EmailField(
        blank=True,
        default="",
    )

    customer_phone = models.CharField(
        max_length=20,
    )

    customer_pincode = models.CharField(
        max_length=10,
        blank=True,
        default="",
    )

    # =====================================================
    # RIDE
    # =====================================================

    ride = models.ForeignKey(
        Ride,
        on_delete=models.PROTECT,
        related_name="bookings",
    )

    ride_price = models.ForeignKey(
        RidePrice,
        on_delete=models.PROTECT,
        related_name="bookings",
    )

    booking_date = models.DateField()

    time_slot = models.CharField(
    max_length=50,
    blank=True,
    default="",
    )

    # =====================================================
    # PARTICIPANTS
    # =====================================================

    quantity = models.PositiveIntegerField(
        default=1,
    )

    # =====================================================
    # PRICE
    # =====================================================

    price_per_person = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    # =====================================================
    # OFFER
    # =====================================================

    offer = models.ForeignKey(
        "Offer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
    )

    applied_coupon_code = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    # =====================================================
    # TOTALS
    # =====================================================

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    # =====================================================
    # STATUS
    # =====================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    notifications_sent = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):

        return (
            f"{self.booking_id} - "
            f"{self.customer_name}"
        )
    





class BookingRideItem(models.Model):

    # =====================================================
    # PARENT BOOKING
    # =====================================================

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="ride_items",
    )


    # =====================================================
    # RIDE
    # =====================================================

    ride = models.ForeignKey(
        Ride,
        on_delete=models.PROTECT,
        related_name="booking_items",
    )


    ride_price = models.ForeignKey(
        RidePrice,
        on_delete=models.PROTECT,
        related_name="booking_items",
    )


    # =====================================================
    # PARTICIPANTS
    # =====================================================

    quantity = models.PositiveIntegerField(
        default=1,
    )


    # =====================================================
    # PRICE
    # =====================================================

    price_per_person = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )


    # =====================================================
    # OFFER
    # =====================================================

    offer = models.ForeignKey(
        "Offer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="booking_items",
    )


    applied_coupon_code = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )


    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )


    # =====================================================
    # TOTALS
    # =====================================================

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )


    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )


    # =====================================================
    # CHECK-IN STATUS
    # =====================================================

    STATUS_CHOICES = [
        ("booked", "Booked"),
        ("checked_in", "Checked In"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]


    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="booked",
    )


    checked_in_at = models.DateTimeField(
        blank=True,
        null=True,
    )


    # =====================================================
    # TIMESTAMPS
    # =====================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )


    updated_at = models.DateTimeField(
        auto_now=True,
    )


    class Meta:

        ordering = ["id"]

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "booking",
                    "ride",
                ],
                name="unique_ride_per_booking",
            )

        ]


    def __str__(self):

        return (
            f"{self.booking.booking_id} - "
            f"{self.ride.name}"
        )




class BookingRideSlot(models.Model):

    STATUS_CHOICES = [

        (
            "held",
            "Held",
        ),

        (
            "confirmed",
            "Confirmed",
        ),

        (
            "cancelled",
            "Cancelled",
        ),

        (
            "expired",
            "Expired",
        ),
    ]

    # =====================================================
    # BOOKING RIDE
    # =====================================================

    booking_item = models.ForeignKey(
        BookingRideItem,
        on_delete=models.CASCADE,
        related_name="allocated_slots",
    )

    # =====================================================
    # SLOT TIME
    # =====================================================

    slot_start_time = models.TimeField()

    slot_end_time = models.TimeField()

    # =====================================================
    # PARTICIPANTS
    # =====================================================

    participant_count = models.PositiveIntegerField()

    # =====================================================
    # STATUS
    # =====================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="held",
        db_index=True,
    )

    # =====================================================
    # PAYMENT HOLD EXPIRY
    # =====================================================

    hold_expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # =====================================================
    # TIMESTAMPS
    # =====================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "slot_start_time",
        ]

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "booking_item",
                    "slot_start_time",
                ],
                name="unique_booking_item_start_slot",
            ),

            models.CheckConstraint(
                condition=models.Q(
                    participant_count__gt=0
                ),
                name="booking_ride_slot_participants_gt_0",
            ),
        ]

        indexes = [

            models.Index(
                fields=[
                    "slot_start_time",
                    "status",
                ],
                name="booking_slot_status_idx",
            ),

        ]

    def __str__(self):

        return (
            f"{self.booking_item.booking.booking_id} - "
            f"{self.booking_item.ride.name} - "
            f"{self.slot_start_time} to "
            f"{self.slot_end_time} - "
            f"{self.participant_count} rider(s)"
        )




class Payment(models.Model):

    STATUS_CHOICES = [
        ("created", "Created"),
        ("authorized", "Authorized"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="payment"
    )

    gateway = models.CharField(
        max_length=30,
        default="razorpay"
    )

    gateway_order_id = models.CharField(
        max_length=255,
        blank=True
    )

    gateway_payment_id = models.CharField(
        max_length=255,
        blank=True
    )

    gateway_signature = models.CharField(
        max_length=500,
        blank=True
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="created"
    )

    failure_reason = models.TextField(
        blank=True
    )

    paid_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.booking.booking_id} - "
            f"{self.status}"
        )





class Ticket(models.Model):

    # =====================================================
    # INTERNAL UUID
    # =====================================================

    ticket_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )


    # =====================================================
    # PUBLIC 6-DIGIT TICKET ID
    # =====================================================

    ticket_number = models.CharField(
        max_length=6,
        unique=True,
        blank=True,
        null=True,
        db_index=True,
    )


    # =====================================================
    # BOOKING
    # =====================================================

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="ticket"
    )


    # =====================================================
    # SECURE QR TOKEN
    # =====================================================

    qr_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )


    qr_image = models.ImageField(
        upload_to="tickets/qr/",
        blank=True,
        null=True
    )

    whatsapp_ticket_image = models.ImageField(
        upload_to="tickets/whatsapp/",
        blank=True,
        null=True,
    )


    pdf_ticket = models.FileField(
        upload_to="tickets/pdf/",
        blank=True,
        null=True
    )


    whatsapp_sent = models.BooleanField(
        default=False
    )


    sms_sent = models.BooleanField(
        default=False
    )


    sms_message_id = models.CharField(
        max_length=255,
        blank=True
    )


    sms_status = models.CharField(
        max_length=30,
        blank=True
    )


    email_sent = models.BooleanField(
        default=False
    )


    is_used = models.BooleanField(
        default=False
    )


    checked_in_at = models.DateTimeField(
        blank=True,
        null=True
    )


    created_at = models.DateTimeField(
        auto_now_add=True
    )


    # =====================================================
    # AUTOMATIC 6-DIGIT TICKET NUMBER
    # =====================================================

    def save(
        self,
        *args,
        **kwargs
    ):

        if not self.ticket_number:

            while True:

                number = str(
                    secrets.randbelow(
                        900000
                    )
                    +
                    100000
                )


                if not Ticket.objects.filter(
                    ticket_number=number
                ).exists():

                    self.ticket_number = number

                    break


        super().save(
            *args,
            **kwargs
        )


    def __str__(self):

        if self.ticket_number:

            return self.ticket_number

        return str(
            self.ticket_id
        )


    class Meta:

        permissions = [
            (
                "verify_ticket",
                "Can scan and verify tickets",
            ),
        ]



class Coupon(models.Model):

    DISCOUNT_TYPE_CHOICES = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
    ]

    code = models.CharField(
        max_length=50,
        unique=True
    )

    rides = models.ManyToManyField(
        Ride,
        related_name="coupons",
        blank=True
    )

    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    valid_from = models.DateField()

    valid_until = models.DateField()

    minimum_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    usage_limit = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    times_used = models.PositiveIntegerField(
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.code    


class Testimonial(OptimizedImageModel):
    image_fields = ["image"]

    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name






# chatbot related models

import uuid

from django.db import models


class ChatbotRule(models.Model):
    """
    Admin-managed rule-based chatbot response.

    keywords example:
    ["price", "cost", "rate", "ride price"]
    """

    title = models.CharField(
        max_length=150
    )

    keywords = models.JSONField(
        default=list,
        help_text=(
            'Enter a JSON list, for example: '
            '["price", "cost", "rate"]'
        ),
    )

    response = models.TextField()

    action_text = models.CharField(
        max_length=100,
        blank=True,
    )

    action_url = models.CharField(
        max_length=255,
        blank=True,
    )

    priority = models.PositiveIntegerField(
        default=10
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "-priority",
            "title",
        ]

    def __str__(self):
        return self.title


class ChatSession(models.Model):

    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("ml", "Malayalam"),
        ("hi", "Hindi"),
        ("ta", "Tamil"),
    ]

    ONBOARDING_CHOICES = [
        ("language", "Waiting For Language"),
        ("name", "Waiting For Name"),
        ("phone", "Waiting For Phone"),
        ("email", "Waiting For Email"),
        ("completed", "Completed"),
    ]

    session_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    browser_session_key = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
    )

    # -----------------------------------------
    # LANGUAGE
    # -----------------------------------------

    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default="en",
    )

    customer_name = models.CharField(
        max_length=150,
        blank=True,
    )

    customer_email = models.EmailField(
        blank=True,
    )

    customer_phone = models.CharField(
        max_length=20,
        blank=True,
    )

    onboarding_step = models.CharField(
        max_length=20,
        choices=ONBOARDING_CHOICES,
        default="language",
    )

    is_closed = models.BooleanField(
        default=False,
    )

    started_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )
    context = models.JSONField(
        default=dict,
        blank=True,
      )

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):

        if self.customer_name:
            return (
                f"{self.customer_name} - "
                f"{self.session_id}"
            )

        return str(self.session_id)


    
class ChatMessage(models.Model):

    SENDER_CHOICES = [
        ("user", "User"),
        ("bot", "Bot"),
        ("admin", "Admin"),
    ]


    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
    )


    sender = models.CharField(
        max_length=10,
        choices=SENDER_CHOICES,
    )


    # What user actually typed
    message = models.TextField()


    # English version used internally
    translated_message = models.TextField(
        blank=True,
    )


    # en / ml / hi / ta
    language = models.CharField(
        max_length=10,
        blank=True,
    )


    intent = models.CharField(
        max_length=100,
        blank=True,
    )


    matched_rule = models.ForeignKey(
        ChatbotRule,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="messages",
    )


    created_at = models.DateTimeField(
        auto_now_add=True,
    )


    class Meta:
        ordering = ["created_at"]


    def __str__(self):

        return (
            f"{self.session.session_id} - "
            f"{self.sender}"
        )


class ChatEnquiry(models.Model):

    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("closed", "Closed"),
    ]

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="enquiries",
    )

    name = models.CharField(
        max_length=150
    )

    phone = models.CharField(
        max_length=20
    )

    email = models.EmailField(
        blank=True
    )

    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.phone}"






class ContactEnquiry(models.Model):

    name = models.CharField(
        max_length=150
    )

    email = models.EmailField()

    subject = models.CharField(
        max_length=250
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False
    )

    email_sent = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    class Meta:
        ordering = [
            "-created_at"
        ]

        verbose_name = "Contact Enquiry"
        verbose_name_plural = "Contact Enquiries"


    def __str__(self):
        return f"{self.name} - {self.subject}"





from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Offer(models.Model):

    # =========================================================
    # OFFER TYPES
    # =========================================================

    OFFER_TYPES = [
        ("percentage", "Percentage Discount"),
        ("fixed", "Fixed Amount Discount"),
        ("buy_x_get_y", "Buy X Get Y"),
        ("group", "Group Discount"),
        ("first_booking", "First Booking"),
        ("weekday", "Weekday Offer"),
        ("early_bird", "Early Bird"),
        ("birthday", "Birthday Offer"),
        ("coupon", "Coupon Offer"),
    ]


    # =========================================================
    # BASIC INFORMATION
    # =========================================================

    title = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    banner_image = models.ImageField(
        upload_to="offers/",
        blank=True,
        null=True
    )


    # =========================================================
    # OFFER TYPE
    # =========================================================

    offer_type = models.CharField(
        max_length=30,
        choices=OFFER_TYPES,
        default="percentage"
    )


    # =========================================================
    # APPLICABLE RIDE
    #
    # ONE OFFER -> ONE RIDE
    # ONE RIDE  -> MANY OFFERS
    # =========================================================

    rides = models.ManyToManyField(
    "Ride",
    related_name="offers",
    blank=True
    )


    # =========================================================
    # DISCOUNT SETTINGS
    # =========================================================

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    minimum_booking_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    maximum_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )


    # =========================================================
    # PARTICIPANT SETTINGS
    # =========================================================

    minimum_participants = models.PositiveIntegerField(
        default=1
    )


    # =========================================================
    # BUY X GET Y SETTINGS
    # =========================================================

    buy_quantity = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    free_quantity = models.PositiveIntegerField(
        blank=True,
        null=True
    )


    # =========================================================
    # OFFER VALIDITY
    # =========================================================

    start_date = models.DateField()

    end_date = models.DateField()


    # =========================================================
    # OFFER STATUS
    # =========================================================

    is_active = models.BooleanField(
        default=True
    )


    # =========================================================
    # OFFER APPLICATION
    # =========================================================

    auto_apply = models.BooleanField(
        default=False
    )

    coupon_required = models.BooleanField(
        default=False
    )

    coupon_code = models.CharField(
        max_length=50,
        blank=True
    )


    # =========================================================
    # USER RESTRICTIONS
    # =========================================================

    first_booking_only = models.BooleanField(
        default=False
    )

    max_uses = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    max_uses_per_user = models.PositiveIntegerField(
        default=1
    )


    # =========================================================
    # CREATED DATE
    # =========================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    # =========================================================
    # AUTOMATIC SLUG
    # =========================================================

    def save(self, *args, **kwargs):

        if not self.slug:

            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Offer.objects.filter(
                slug=slug
            ).exclude(
                pk=self.pk
            ).exists():

                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


    # =========================================================
    # COMPUTED STATUS
    # =========================================================

    @property
    def computed_status(self):

        today = timezone.localdate()

        if not self.is_active:
            return "inactive"

        if today < self.start_date:
            return "upcoming"

        if today > self.end_date:
            return "expired"

        return "active"


    # =========================================================
    # DISCOUNT LABEL
    # =========================================================

    @property
    def discount_label(self):

        if self.offer_type == "percentage":

            value = self.discount_value

            if value == value.to_integral():
                value = int(value)

            return f"{value}% OFF"


        if self.offer_type == "fixed":

            value = self.discount_value

            if value == value.to_integral():
                value = int(value)

            return f"₹{value} OFF"


        if self.offer_type == "buy_x_get_y":

            if self.buy_quantity and self.free_quantity:
                return (
                    f"Buy {self.buy_quantity} "
                    f"Get {self.free_quantity} Free"
                )

            return "Buy X Get Y"


        if self.offer_type == "group":

            value = self.discount_value

            if value == value.to_integral():
                value = int(value)

            return f"{value}% Group Discount"


        if self.offer_type == "first_booking":

            value = self.discount_value

            if value == value.to_integral():
                value = int(value)

            return f"{value}% First Booking Discount"


        if self.offer_type == "weekday":

            value = self.discount_value

            if value == value.to_integral():
                value = int(value)

            return f"{value}% Weekday Discount"


        if self.offer_type == "early_bird":

            value = self.discount_value

            if value == value.to_integral():
                value = int(value)

            return f"{value}% Early Bird Discount"


        if self.offer_type == "birthday":

            value = self.discount_value

            if value == value.to_integral():
                value = int(value)

            return f"{value}% Birthday Discount"


        if self.offer_type == "coupon":

            if self.discount_value:

                value = self.discount_value

                if value == value.to_integral():
                    value = int(value)

                return f"{value}% OFF"

            return "Coupon Offer"


        return "Special Offer"


    # =========================================================
    # CHECK IF OFFER IS CURRENTLY VALID
    # =========================================================

    def is_currently_valid(self):

        return self.computed_status == "active"


    # =========================================================
    # STRING REPRESENTATION
    # =========================================================

    def __str__(self):

        if self.rides.exists():
            ride_names = ", ".join(
            self.rides.values_list("name", flat=True)[:3]
           )
            return f"{self.title} - {ride_names}"

        return self.title
    


    def get_user_usage_count(
         self, user_profile):

        if not user_profile:
           return 0

        return (
        Booking.objects
        .filter(
            user=user_profile,
            offer=self,
            status__in=[
                "confirmed",
                "checked_in",
            ],
        )
        .count()
    )


    def can_user_use(
       self,
       user_profile):

        if not user_profile:
          return False

        if not self.max_uses_per_user:
            return True

        usage_count = (
            self.get_user_usage_count(
            user_profile
             )
        )

        return (
        usage_count<self.max_uses_per_user)


    # =========================================================
    # META
    # =========================================================

    class Meta:

        ordering = [
            "-created_at"
        ]

        verbose_name = "Offer"
        verbose_name_plural = "Offers"



class BookingWeightGroup(models.Model):

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="weight_groups",
        null=True,
        blank=True,
    )

    booking_item = models.ForeignKey(
        BookingRideItem,
        on_delete=models.CASCADE,
        related_name="weight_groups",
        null=True,
        blank=True,
    )

    range_key = models.CharField(
        max_length=20,
        choices=WEIGHT_RANGE_CHOICES,
    )

    participant_count = models.PositiveIntegerField(
        default=1,
    )

    min_weight = models.PositiveIntegerField()

    max_weight = models.PositiveIntegerField()

    label = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "booking_item",
                    "range_key",
                ],
                name="unique_booking_item_weight_range",
            )

        ]

    def __str__(self):

        if self.booking_item:

            return (
                f"{self.booking_item.booking.booking_id} - "
                f"{self.booking_item.ride.name} - "
                f"{self.label or self.range_key} - "
                f"{self.participant_count} rider(s)"
            )

        if self.booking:

            return (
                f"{self.booking.booking_id} - "
                f"{self.label or self.range_key} - "
                f"{self.participant_count} rider(s)"
            )

        return (
            f"{self.label or self.range_key} - "
            f"{self.participant_count} rider(s)"
        )


class Refund(models.Model):

    STATUS_CHOICES = [
        ("requested", "Requested"),
        ("approved", "Approved"),
        ("processing", "Processing"),
        ("processed", "Processed"),
        ("rejected", "Rejected"),
        ("failed", "Failed"),
    ]


    refund_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )


    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="refunds",
    )


    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="refunds",
    )


    # =====================================================
    # ORIGINAL AMOUNT
    # =====================================================

    original_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )


    # 10% Flying Fox cancellation charge
    deduction_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("10.00"),
    )


    deduction_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )


    # Actual 90% returned to customer
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )


    # =====================================================
    # CUSTOMER REQUEST
    # =====================================================

    reason = models.TextField(
        blank=True,
        default="",
    )


    admin_note = models.TextField(
        blank=True,
        default="",
    )


    # =====================================================
    # RAZORPAY
    # =====================================================

    razorpay_payment_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )


    razorpay_refund_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
        db_index=True,
    )


    gateway_status = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )


    # Refund reference from bank/acquirer when available
    arn = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )


    # =====================================================
    # STATUS
    # =====================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="requested",
    )


    requested_at = models.DateTimeField(
        auto_now_add=True,
    )


    processed_at = models.DateTimeField(
        blank=True,
        null=True,
    )


    updated_at = models.DateTimeField(
        auto_now=True,
    )


    class Meta:
        ordering = [
            "-requested_at",
        ]


    def __str__(self):

        return (
            f"{self.refund_id} - "
            f"{self.booking.booking_id}"
        )  


class OTPVerification(models.Model):

    # =====================================================
    # PHONE NUMBER
    # =====================================================

    phone_number = models.CharField(
        max_length=20,
        db_index=True,
    )

    # =====================================================
    # OTP
    # =====================================================

    otp = models.CharField(
        max_length=6,
    )

    # =====================================================
    # VERIFICATION
    # =====================================================

    is_verified = models.BooleanField(
        default=False,
    )

    verified_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    # =====================================================
    # ATTEMPTS
    # =====================================================

    attempts = models.PositiveIntegerField(
        default=0,
    )

    # =====================================================
    # EXPIRATION
    # =====================================================

    expires_at = models.DateTimeField()

    # =====================================================
    # CREATED
    # =====================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "phone_number",
                    "is_verified",
                ],
                name="otp_phone_verified_idx",
            ),
        ]

    def is_expired(self):

        return (
            timezone.now()
            >=
            self.expires_at
        )

    def __str__(self):

        return (
            f"{self.phone_number} "
            f"- OTP Verification"
        )