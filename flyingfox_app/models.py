from django.db import models

# Create your models here.
from django.db import models
from django.utils.text import slugify
from django.utils import timezone


from django.contrib.auth.models import User
import uuid


# class Coupon(models.Model):
#     DISCOUNT_TYPES = (
#         ("percentage", "Percentage"),
#         ("fixed", "Fixed Amount"),
#     )

#     code = models.CharField(
#         max_length=50,
#         unique=True
#     )

#     discount_type = models.CharField(
#         max_length=20,
#         choices=DISCOUNT_TYPES
#     )

#     discount_value = models.DecimalField(
#         max_digits=10,
#         decimal_places=2
#     )

#     valid_from = models.DateTimeField()
#     valid_until = models.DateTimeField()

#     usage_limit = models.PositiveIntegerField(
#         blank=True,
#         null=True
#     )

#     times_used = models.PositiveIntegerField(default=0)

#     active = models.BooleanField(default=True)

#     def __str__(self):
#         return self.code


# class Booking(models.Model):
#     STATUS_CHOICES = (
#         ("pending", "Pending"),
#         ("confirmed", "Confirmed"),
#         ("cancelled", "Cancelled"),
#         ("checked_in", "Checked In"),
#         ("refunded", "Refunded"),
#     )

#     booking_id = models.UUIDField(
#         default=uuid.uuid4,
#         editable=False,
#         unique=True
#     )

#     user = models.ForeignKey(
#         User,
#         on_delete=models.SET_NULL,
#         blank=True,
#         null=True,
#         related_name="bookings"
#     )

#     timeslot = models.ForeignKey(
#         RideTimeSlot,
#         on_delete=models.PROTECT,
#         related_name="bookings"
#     )

#     customer_name = models.CharField(max_length=150)
#     email = models.EmailField()
#     phone = models.CharField(max_length=20)

#     quantity = models.PositiveIntegerField()

#     price_per_person = models.DecimalField(
#         max_digits=10,
#         decimal_places=2
#     )

#     subtotal = models.DecimalField(
#         max_digits=10,
#         decimal_places=2
#     )

#     coupon = models.ForeignKey(
#         Coupon,
#         on_delete=models.SET_NULL,
#         blank=True,
#         null=True
#     )

#     discount = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         default=0
#     )

#     total_amount = models.DecimalField(
#         max_digits=10,
#         decimal_places=2
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default="pending"
#     )

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return str(self.booking_id)


# class Payment(models.Model):
#     PAYMENT_STATUS = (
#         ("created", "Created"),
#         ("paid", "Paid"),
#         ("failed", "Failed"),
#         ("refunded", "Refunded"),
#     )

#     booking = models.OneToOneField(
#         Booking,
#         on_delete=models.CASCADE,
#         related_name="payment"
#     )

#     gateway = models.CharField(
#         max_length=30,
#         default="razorpay"
#     )

#     gateway_order_id = models.CharField(
#         max_length=255,
#         blank=True
#     )

#     gateway_payment_id = models.CharField(
#         max_length=255,
#         blank=True
#     )

#     amount = models.DecimalField(
#         max_digits=10,
#         decimal_places=2
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=PAYMENT_STATUS,
#         default="created"
#     )

#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.booking.booking_id} - {self.status}"












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
        blank=True
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
    full_name = models.CharField(
        max_length=150
    )

    email = models.EmailField(
        unique=True
    )

    phone = models.CharField(
        max_length=20,
        unique=True
    )

    password = models.CharField(
        max_length=128
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.email}"



class Ride(OptimizedImageModel):

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
        decimal_places=2
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            "-start_date"
        ]

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
        editable=False
    )

    # Guest customer information
    customer_name = models.CharField(
    max_length=150
)

    customer_email = models.EmailField()

    customer_phone = models.CharField(
    max_length=20
)

    customer_pincode = models.CharField(
    max_length=10
)

    time_slot = models.CharField(
    max_length=50
)

    ride = models.ForeignKey(
        Ride,
        on_delete=models.PROTECT,
        related_name="bookings"
    )

    ride_price = models.ForeignKey(
        RidePrice,
        on_delete=models.PROTECT,
        related_name="bookings"
    )

    booking_date = models.DateField()

    

    quantity = models.PositiveIntegerField(
        default=1
    )

    price_per_person = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    photo_addon = models.BooleanField(
        default=False
    )

    video_addon = models.BooleanField(
        default=False
    )

    addon_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    coupon = models.ForeignKey(
        "Coupon",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="bookings"
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    notifications_sent = models.BooleanField(
        default=False
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
        return (
            f"{self.booking_id} - "
            f"{self.customer_name}"
        )


# class Booking(models.Model):

#     STATUS_CHOICES = [
#         ("pending", "Pending"),
#         ("confirmed", "Confirmed"),
#         ("cancelled", "Cancelled"),
#         ("checked_in", "Checked In"),
#         ("refunded", "Refunded"),
#     ]

#     booking_id = models.UUIDField(
#         default=uuid.uuid4,
#         unique=True,
#         editable=False
#     )

#     user = models.ForeignKey(
#         UserProfile,
#         on_delete=models.PROTECT,
#         related_name="bookings"
#     )

#     ride = models.ForeignKey(
#         Ride,
#         on_delete=models.PROTECT,
#         related_name="bookings"
#     )

#     ride_price = models.ForeignKey(
#         RidePrice,
#         on_delete=models.PROTECT,
#         related_name="bookings"
#     )

#     booking_date = models.DateField()

#     quantity = models.PositiveIntegerField(
#         default=1
#     )

#     price_per_person = models.DecimalField(
#         max_digits=10,
#         decimal_places=2
#     )

#     coupon = models.ForeignKey(
#     "Coupon",
#     on_delete=models.SET_NULL,
#     blank=True,
#     null=True,
#     related_name="bookings"
#     )

#     discount_amount = models.DecimalField(
#     max_digits=10,
#     decimal_places=2,
#     default=0
#     )

#     subtotal = models.DecimalField(
#         max_digits=10,
#         decimal_places=2
#     )

#     total_amount = models.DecimalField(
#         max_digits=10,
#         decimal_places=2
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default="pending"
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True
#     )

#     updated_at = models.DateTimeField(
#         auto_now=True
#     )

#     class Meta:
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"{self.booking_id} - {self.user.full_name}"    


class BookingPerson(models.Model):

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="participants"
    )

    full_name = models.CharField(
        max_length=150
    )

    age = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.full_name} - "
            f"{self.booking.booking_id}"
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

# class Payment(models.Model):

#     STATUS_CHOICES = [
#         ("created", "Created"),
#         ("paid", "Paid"),
#         ("failed", "Failed"),
#         ("refunded", "Refunded"),
#     ]

#     booking = models.OneToOneField(
#         Booking,
#         on_delete=models.CASCADE,
#         related_name="payment"
#     )

#     gateway = models.CharField(
#         max_length=30,
#         default="razorpay"
#     )

#     gateway_order_id = models.CharField(
#         max_length=255,
#         blank=True
#     )

#     gateway_payment_id = models.CharField(
#         max_length=255,
#         blank=True
#     )

#     amount = models.DecimalField(
#         max_digits=10,
#         decimal_places=2
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default="created"
#     )

#     paid_at = models.DateTimeField(
#         blank=True,
#         null=True
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True
#     )

#     def __str__(self):
#         return f"{self.booking.booking_id} - {self.status}"




class Ticket(models.Model):

    ticket_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="ticket"
    )

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

    def __str__(self):
        return str(self.ticket_id)



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

    ONBOARDING_CHOICES = [
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
        default="name",
    )

    is_closed = models.BooleanField(
        default=False
    )

    started_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
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

    message = models.TextField()

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
        auto_now_add=True
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

class Offer(models.Model):

    STATUS_CHOICES = [
    ("upcoming", "Upcoming"),
    ("active", "Active"),
    ("expired", "Expired"),
]
    title = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
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

    rides = models.ManyToManyField(
        Ride,
        related_name="offers",
        blank=True
    )

    coupon = models.OneToOneField(
        Coupon,
        on_delete=models.CASCADE,
        related_name="offer",
        blank=True,
        null=True,
        editable=False
    )

    discount_type = models.CharField(
        max_length=20,
        choices=Coupon.DISCOUNT_TYPE_CHOICES
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    start_date = models.DateField()

    end_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="expired",
        editable=False
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Manually disable an offer regardless of dates."
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
        return f"{self.title} ({self.status})"

    def generate_coupon_code(self):
        import random
        import string

        base = slugify(self.title).upper().replace("-", "")[:6] or "OFFER"

        while True:
            code = f"{base}{''.join(random.choices(string.digits, k=4))}"
            if not Coupon.objects.filter(code=code).exists():
                return code

    def refresh_status(self):
        today = timezone.now().date()

        if self.is_active and self.start_date <= today <= self.end_date:
            self.status = "active"
        else:
            self.status = "expired"

    def save(self, *args, **kwargs):

        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Offer.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        self.refresh_status()

        creating_coupon = self.coupon_id is None

        super().save(*args, **kwargs)

        if creating_coupon:
            self.coupon = Coupon.objects.create(
                code=self.generate_coupon_code(),
                discount_type=self.discount_type,
                discount_value=self.discount_value,
                valid_from=self.start_date,
                valid_until=self.end_date,
                is_active=self.is_active,
            )
            super().save(update_fields=["coupon"])

    def sync_coupon(self):
        """Call after setting self.rides (M2M) — e.g. in admin's save_related,
        or after form.save_m2m() — to push rides/dates onto the linked coupon."""
        if self.coupon:
            self.coupon.rides.set(self.rides.all())
            self.coupon.valid_from = self.start_date
            self.coupon.valid_until = self.end_date
            self.coupon.discount_type = self.discount_type
            self.coupon.discount_value = self.discount_value
            self.coupon.is_active = self.is_active
            self.coupon.save()