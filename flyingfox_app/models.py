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

    short_description = models.TextField(
        blank=True
    )

    description = models.TextField()

    is_published = models.BooleanField(
        default=True
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
        related_name="media"
    )

    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        default="image"
    )

    image = models.ImageField(
        upload_to="rides/images/",
        blank=True,
        null=True
    )

    video = models.FileField(
        upload_to="rides/videos/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.ride.name} - {self.get_media_type_display()}"

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
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("checked_in", "Checked In"),
        ("refunded", "Refunded"),
    ]

    booking_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    user = models.ForeignKey(
        UserProfile,
        on_delete=models.PROTECT,
        related_name="bookings"
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

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.booking_id} - {self.user.full_name}"    


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
        return f"{self.full_name} - {self.booking.booking_id}"    



class Payment(models.Model):

    STATUS_CHOICES = [
        ("created", "Created"),
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

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="created"
    )

    paid_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.booking.booking_id} - {self.status}"


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