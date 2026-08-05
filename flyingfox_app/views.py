import json
import re

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower
from django.db.models import Q, Count
from django.db import transaction
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Prefetch
from datetime import date
from django.utils.dateparse import parse_date
from datetime import date
from decimal import Decimal, InvalidOperation
from io import BytesIO
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

import re

from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from django.db.models import Prefetch
from django.utils.dateparse import parse_date

import qrcode

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.conf import settings
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.db import transaction
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST

from django.views.decorators.http import (
    require_GET,
    require_POST,
)

# sms 
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date


from flyingfox_app.forms import TestimonialForm

from .models import (
    ChatEnquiry,
    ChatbotRule,
    ChatMessage,
    ChatSession,
    GalleryCategory,
    GalleryItem,
    Blog,
    ContactMessage,
    UserProfile,
    RideMedia,
    Ride, RidePrice, Booking,
    BookingPerson,
    Payment,
    Ticket,
    Coupon,Testimonial
)



def _admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect("admin_login")

        return view_func(request, *args, **kwargs)

    return wrapper


def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("admin_dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user and user.is_staff:
            login(request, user)
            return redirect("admin_dashboard")

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "authenticate/login.html"
    )


@login_required(login_url="admin_login")
def admin_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("admin_login")



# @_admin_required
# def admin_dashboard(request):
#     today = timezone.localdate()

#     stats = {
#         "total_rides": Ride.objects.count(),
#         "total_bookings": Booking.objects.count(),
#         "confirmed_bookings": Booking.objects.filter(
#             status="confirmed"
#         ).count(),
#         "cancelled_bookings": Booking.objects.filter(
#             status="cancelled"
#         ).count(),
#         "today_bookings": Booking.objects.filter(
#             created_at__date=today
#         ).count(),
#         "total_coupons": Coupon.objects.count(),
#     }

#     recent_bookings = (
#         Booking.objects
#         .select_related(
#             "timeslot",
#             "timeslot__ride"
#         )
#         .order_by("-created_at")[:5]
#     )

#     return render(
#         request,
#         "admin_pages/dashboard.html",
#         {
#             "stats": stats,
#             "recent_bookings": recent_bookings,
#         }
#     )



@_admin_required
def admin_dashboard(request):

    stats = {
        "total_bookings": 0,
        "confirmed_bookings": 0,
        "cancelled_bookings": 0,
        "today_bookings": 0,
        "total_coupons": 0,
    }

    recent_bookings = []

    return render(
        request,
        "admin_pages/dashboard.html",
        {
            "stats": stats,
            "recent_bookings": recent_bookings,
        }
    )



# ==========================================
# GALLERY CATEGORY CRUD
# ==========================================
# ==========================================
# CATEGORIES
# ==========================================

@login_required(login_url="admin_login")
def category_list(request):

    categories_qs = (
        GalleryCategory.objects
        .all()
        .order_by(Lower("name"))
    )

    paginator = Paginator(
        categories_qs,
        10
    )

    page_number = request.GET.get("page")

    categories = paginator.get_page(
        page_number
    )

    return render(
        request,
        "admin_pages/category_list.html",
        {
            "categories": categories
        }
    )


@login_required(login_url="admin_login")
def add_category(request):

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        if not name:

            messages.error(
                request,
                "Category name is required."
            )

            return render(
                request,
                "admin_pages/add_category.html"
            )

        if GalleryCategory.objects.filter(
            name__iexact=name
        ).exists():

            messages.error(
                request,
                "This category already exists."
            )

            return render(
                request,
                "admin_pages/add_category.html"
            )

        GalleryCategory.objects.create(
            name=name
        )

        messages.success(
            request,
            "Category added successfully!"
        )

        return redirect(
            "category_list"
        )

    return render(
        request,
        "admin_pages/add_category.html"
    )


@login_required(login_url="admin_login")
def update_category(request, pk):

    category = get_object_or_404(
        GalleryCategory,
        pk=pk
    )

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        if not name:

            messages.error(
                request,
                "Category name is required."
            )

            return redirect(
                "category_list"
            )

        if GalleryCategory.objects.filter(
            name__iexact=name
        ).exclude(
            pk=category.pk
        ).exists():

            messages.error(
                request,
                "Another category with this name already exists."
            )

            return redirect(
                "category_list"
            )

        category.name = name

        # regenerate slug after rename
        category.slug = ""

        category.save()

        messages.success(
            request,
            "Category updated successfully!"
        )

    return redirect(
        "category_list"
    )


@login_required(login_url="admin_login")
def delete_category(request, pk):

    category = get_object_or_404(
        GalleryCategory,
        pk=pk
    )

    if request.method == "POST":

        category.delete()

        messages.success(
            request,
            "Category deleted successfully!"
        )

    return redirect(
        "category_list"
    )



# ==========================================
# GALLERY ITEM CRUD
# ==========================================

# ==========================================
# GALLERY
# ==========================================

@login_required(login_url="admin_login")
def gallery_items(request):

    categories = (
        GalleryCategory.objects
        .all()
        .prefetch_related("items")
    )

    category_pages = {}

    for category in categories:

        items_qs = (
            category.items
            .all()
            .order_by("-uploaded_at")
        )

        paginator = Paginator(
            items_qs,
            8
        )

        page_number = request.GET.get(
            f"page_{category.id}",
            1
        )

        try:
            page_obj = paginator.page(
                page_number
            )

        except PageNotAnInteger:
            page_obj = paginator.page(1)

        except EmptyPage:
            page_obj = paginator.page(
                paginator.num_pages
            )

        category_pages[category.id] = page_obj

    return render(
        request,
        "admin_pages/image_list.html",
        {
            "categories": categories,
            "category_pages": category_pages,
        }
    )

# @login_required(login_url="admin_login")
# def add_gallery_item(request):

#     categories = GalleryCategory.objects.all()

#     if request.method == "POST":

#         category_id = request.POST.get(
#             "category"
#         )

#         title = request.POST.get(
#             "title",
#             ""
#         ).strip()

#         media_type = request.POST.get(
#             "media_type",
#             "image"
#         )

#         image = request.FILES.get(
#             "image"
#         )

#         video = request.FILES.get(
#             "video"
#         )

#         video_url = request.POST.get(
#             "video_url",
#             ""
#         ).strip()

#         thumbnail = request.FILES.get(
#             "thumbnail"
#         )

#         is_featured = (
#             request.POST.get("is_featured")
#             == "on"
#         )


#         if not category_id:

#             messages.error(
#                 request,
#                 "Please select a category."
#             )

#             return render(
#                 request,
#                 "admin_pages/add_image.html",
#                 {
#                     "categories": categories
#                 }
#             )


#         category = get_object_or_404(
#             GalleryCategory,
#             pk=category_id
#         )


#         # Image validation
#         if media_type == "image":

#             if not image:

#                 messages.error(
#                     request,
#                     "Please select an image."
#                 )

#                 return render(
#                     request,
#                     "admin_pages/add_image.html",
#                     {
#                         "categories": categories
#                     }
#                 )


#         # Video validation
#         elif media_type == "video":

#             if not video and not video_url:

#                 messages.error(
#                     request,
#                     "Please upload a video or enter a video URL."
#                 )

#                 return render(
#                     request,
#                     "admin_pages/add_image.html",
#                     {
#                         "categories": categories
#                     }
#                 )


#         GalleryItem.objects.create(
#             category=category,
#             title=title,
#             media_type=media_type,
#             image=image,
#             video=video,
#             video_url=video_url or None,
#             thumbnail=thumbnail,
#             is_featured=is_featured,
#         )


#         messages.success(
#             request,
#             "Gallery item added successfully!"
#         )

#         return redirect(
#             "list_image"
#         )


#     return render(
#         request,
#         "admin_pages/add_image.html",
#         {
#             "categories": categories
#         }
#     )


@login_required(login_url="admin_login")
def add_gallery_item(request):

    categories = GalleryCategory.objects.all()

    if request.method == "POST":

        category_id = request.POST.get(
            "category"
        )

        if not category_id:

            messages.error(
                request,
                "Please select a category."
            )

            return render(
                request,
                "admin_pages/add_image.html",
                {
                    "categories": categories
                }
            )

        category = get_object_or_404(
            GalleryCategory,
            pk=category_id
        )

        images = request.FILES.getlist(
            "images"
        )

        videos = request.FILES.getlist(
            "videos"
        )

        if not images and not videos:

            messages.error(
                request,
                "Please select at least one image or video."
            )

            return render(
                request,
                "admin_pages/add_image.html",
                {
                    "categories": categories
                }
            )

        # Save multiple images
        for image in images:

            GalleryItem.objects.create(
                category=category,
                image=image
            )

        # Save multiple videos
        for video in videos:

            GalleryItem.objects.create(
                category=category,
                video=video
            )

        messages.success(
            request,
            "Gallery images and videos uploaded successfully."
        )

        return redirect(
            "list_image"
        )

    return render(
        request,
        "admin_pages/add_image.html",
        {
            "categories": categories
        }
    )


@login_required(login_url="admin_login")
def update_gallery_item(request, item_id):

    item = get_object_or_404(
        GalleryItem,
        id=item_id
    )

    categories = GalleryCategory.objects.all()

    if request.method == "POST":

        category_id = request.POST.get(
            "category"
        )

        if not category_id:

            messages.error(
                request,
                "Please select a category."
            )

            return render(
                request,
                "admin_pages/update_image.html",
                {
                    "categories": categories,
                    "gallery_item": item,
                }
            )

        item.category = get_object_or_404(
            GalleryCategory,
            id=category_id
        )

        new_image = request.FILES.get(
            "image"
        )

        new_video = request.FILES.get(
            "video"
        )

        if new_image:

            item.image = new_image

            # Item becomes image only
            item.video = None

        elif new_video:

            item.video = new_video

            # Item becomes video only
            item.image = None

        item.save()

        messages.success(
            request,
            "Gallery item updated successfully."
        )

        return redirect(
            "list_image"
        )

    return render(
        request,
        "admin_pages/update_image.html",
        {
            "categories": categories,
            "gallery_item": item,
        }
    )

@login_required(login_url="admin_login")
def delete_gallery_item(request, item_id):

    item = get_object_or_404(
        GalleryItem,
        id=item_id
    )

    if request.method == "POST":

        item.delete()

        messages.success(
            request,
            "Gallery item deleted successfully!"
        )

    return redirect(
        "list_image"
    )


# ==========================================
# BLOG CRUD
# ==========================================

@_admin_required
def admin_blog_list(request):

    blogs_qs = Blog.objects.all().order_by("-created_at")

    paginator = Paginator(blogs_qs, 10)

    page_number = request.GET.get("page")

    blogs = paginator.get_page(page_number)

    return render(
        request,
        "admin_pages/blog_list.html",
        {
            "blogs": blogs,
        },
    )


@_admin_required
def blog_create(request):

    if request.method == "POST":

        title = request.POST.get(
            "title",
            "",
        ).strip()

        description = request.POST.get(
            "description",
            "",
        ).strip()

        image = request.FILES.get("image")

        if not title:
            messages.error(
                request,
                "Blog title is required.",
            )

            return render(
                request,
                "admin_pages/create_blog.html",
                {
                    "title": title,
                    "description": description,
                },
            )

        if not description:
            messages.error(
                request,
                "Blog description is required.",
            )

            return render(
                request,
                "admin_pages/create_blog.html",
                {
                    "title": title,
                    "description": description,
                },
            )

        if not image:
            messages.error(
                request,
                "Blog image is required.",
            )

            return render(
                request,
                "admin_pages/create_blog.html",
                {
                    "title": title,
                    "description": description,
                },
            )

        Blog.objects.create(
            title=title,
            description=description,
            image=image,
        )

        messages.success(
            request,
            "Blog created successfully.",
        )

        return redirect("admin_blog_list")

    return render(
        request,
        "admin_pages/create_blog.html",
    )


@_admin_required
def blog_update(request, pk):

    blog = get_object_or_404(
        Blog,
        pk=pk,
    )

    if request.method == "POST":

        title = request.POST.get(
            "title",
            "",
        ).strip()

        description = request.POST.get(
            "description",
            "",
        ).strip()

        if not title:
            messages.error(
                request,
                "Blog title is required.",
            )

            return render(
                request,
                "admin_pages/create_blog.html",
                {
                    "blog": blog,
                },
            )

        if not description:
            messages.error(
                request,
                "Blog description is required.",
            )

            return render(
                request,
                "admin_pages/create_blog.html",
                {
                    "blog": blog,
                },
            )

        blog.title = title
        blog.description = description

        new_image = request.FILES.get("image")

        if new_image:
            blog.image = new_image

        blog.save()

        messages.success(
            request,
            "Blog updated successfully.",
        )

        return redirect("admin_blog_list")

    return render(
        request,
        "admin_pages/create_blog.html",
        {
            "blog": blog,
        },
    )


@_admin_required
def blog_delete(request, pk):

    blog = get_object_or_404(
        Blog,
        pk=pk,
    )

    if request.method == "POST":

        blog.delete()

        messages.success(
            request,
            "Blog deleted successfully.",
        )

    return redirect("admin_blog_list")



# ==========================================
# CONTACTS (ADMIN)
# ==========================================

@login_required(login_url="admin_login")
def view_contacts(request):
    contacts = Paginator(ContactMessage.objects.all().order_by("-created_at"), 10).get_page(request.GET.get("page"))
    return render(request, "admin_pages/view_contacts.html", {"contacts": contacts})


@login_required(login_url="admin_login")
def delete_contact(request, pk):
    contact = get_object_or_404(ContactMessage, pk=pk)
    if request.method == "POST":
        contact.delete()
        messages.success(request, "Contact deleted!")
    return redirect("view_contacts")


# ==========================================
# USER MANAGEMENT
# ==========================================

@login_required(login_url="admin_login")
def user_list(request):

    users_qs = UserProfile.objects.all().order_by("-created_at")

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:
        users_qs = users_qs.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    paginator = Paginator(
        users_qs,
        10
    )

    page_number = request.GET.get(
        "page"
    )

    users = paginator.get_page(
        page_number
    )

    return render(
        request,
        "admin_pages/user_list.html",
        {
            "users": users,
            "search": search,
        }
    )



@login_required(login_url="admin_login")
def user_delete(request, pk):

    user = get_object_or_404(
        UserProfile,
        pk=pk
    )

    if request.method == "POST":

        user_name = user.full_name

        user.delete()

        messages.success(
            request,
            f'User "{user_name}" deleted successfully.'
        )

    return redirect(
        "user_list"
    )




# ==========================================
# RIDE CRUD
# ==========================================

@login_required(login_url="admin_login")
def ride_list(request):

    rides_qs = (
        Ride.objects
        .prefetch_related("media")
        .all()
        .order_by("-created_at")
    )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:
        rides_qs = rides_qs.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    paginator = Paginator(
        rides_qs,
        10
    )

    rides = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "admin_pages/ride_list.html",
        {
            "rides": rides,
            "search": search,
        }
    )

# @login_required(login_url="admin_login")
# def ride_create(request):

#     if request.method == "POST":

#         name = request.POST.get(
#             "name",
#             ""
#         ).strip()

#         description = request.POST.get(
#             "description",
#             ""
#         ).strip()

#         duration = request.POST.get(
#             "duration",
#             ""
#         ).strip()

#         safety_notes = request.POST.get(
#             "safety_notes",
#             ""
#         ).strip()

#         is_active = (
#             request.POST.get("is_active")
#             == "on"
#         )


#         # ==========================
#         # VALIDATION
#         # ==========================

#         if not name:

#             messages.error(
#                 request,
#                 "Ride name is required."
#             )

#             return render(
#                 request,
#                 "admin_pages/ride_form.html"
#             )


#         if not description:

#             messages.error(
#                 request,
#                 "Description is required."
#             )

#             return render(
#                 request,
#                 "admin_pages/ride_form.html"
#             )


#         if not duration:

#             messages.error(
#                 request,
#                 "Duration is required."
#             )

#             return render(
#                 request,
#                 "admin_pages/ride_form.html"
#             )


#         # ==========================
#         # CREATE RIDE
#         # ==========================

#         ride = Ride.objects.create(
#             name=name,
#             description=description,
#             duration=duration,
#             safety_notes=safety_notes,
#             is_active=is_active,
#         )


#         # ==========================
#         # MULTIPLE IMAGES
#         # ==========================

#         images = request.FILES.getlist(
#             "images"
#         )

#         for image in images:

#             RideMedia.objects.create(
#                 ride=ride,
#                 media_type="image",
#                 image=image
#             )


#         # ==========================
#         # SINGLE VIDEO
#         # ==========================

#         video = request.FILES.get(
#             "video"
#         )

#         if video:

#             RideMedia.objects.create(
#                 ride=ride,
#                 media_type="video",
#                 video=video
#             )


#         messages.success(
#             request,
#             "Ride added successfully."
#         )

#         return redirect(
#             "ride_list"
#         )


#     return render(
#         request,
#         "admin_pages/ride_form.html"
#     )


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from .models import Ride, RideMedia


@login_required(login_url="admin_login")
def ride_create(request):

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        duration = request.POST.get(
            "duration",
            ""
        ).strip()

        safety_notes = request.POST.get(
            "safety_notes",
            ""
        ).strip()

        is_featured = (
            request.POST.get("is_featured")
            == "on"
        )

        is_active = (
            request.POST.get("is_active")
            == "on"
        )

        form_data = {
            "name": name,
            "description": description,
            "duration": duration,
            "safety_notes": safety_notes,
            "is_featured": is_featured,
            "is_active": is_active,
        }

        # ==========================
        # VALIDATION
        # ==========================

        if not name:

            messages.error(
                request,
                "Ride name is required."
            )

            return render(
                request,
                "admin_pages/ride_form.html",
                {
                    "form_data": form_data,
                }
            )

        if not description:

            messages.error(
                request,
                "Description is required."
            )

            return render(
                request,
                "admin_pages/ride_form.html",
                {
                    "form_data": form_data,
                }
            )

        if not duration:

            messages.error(
                request,
                "Duration is required."
            )

            return render(
                request,
                "admin_pages/ride_form.html",
                {
                    "form_data": form_data,
                }
            )

        images = request.FILES.getlist(
            "images"
        )

        video = request.FILES.get(
            "video"
        )

        try:

            with transaction.atomic():

                ride = Ride.objects.create(
                    name=name,
                    description=description,
                    duration=duration,
                    safety_notes=safety_notes,
                    is_featured=is_featured,
                    is_active=is_active,
                )

                # ==========================
                # MULTIPLE IMAGES
                # ==========================

                for image in images:

                    RideMedia.objects.create(
                        ride=ride,
                        media_type="image",
                        image=image,
                    )

                # ==========================
                # SINGLE VIDEO
                # ==========================

                if video:

                    RideMedia.objects.create(
                        ride=ride,
                        media_type="video",
                        video=video,
                    )

        except Exception as error:

            print("RIDE CREATION ERROR:", error)

            messages.error(
                request,
                f"Unable to create ride: {error}"
            )

            return render(
                request,
                "admin_pages/ride_form.html",
                {
                    "form_data": form_data,
                }
            )

        messages.success(
            request,
            "Ride added successfully."
        )

        return redirect(
            "ride_list"
        )

    return render(
        request,
        "admin_pages/ride_form.html"
    )



from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .models import Ride, RideMedia


@login_required(login_url="admin_login")
def ride_update(request, pk):

    ride = get_object_or_404(
        Ride,
        pk=pk
    )

    if request.method == "POST":

        name = request.POST.get(
            "name",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        duration = request.POST.get(
            "duration",
            ""
        ).strip()

        safety_notes = request.POST.get(
            "safety_notes",
            ""
        ).strip()

        is_featured = (
            request.POST.get("is_featured")
            == "on"
        )

        is_active = (
            request.POST.get("is_active")
            == "on"
        )

        if not name:

            messages.error(
                request,
                "Ride name is required."
            )

            return render(
                request,
                "admin_pages/ride_form.html",
                {
                    "ride": ride,
                }
            )

        if not description:

            messages.error(
                request,
                "Description is required."
            )

            return render(
                request,
                "admin_pages/ride_form.html",
                {
                    "ride": ride,
                }
            )

        if not duration:

            messages.error(
                request,
                "Duration is required."
            )

            return render(
                request,
                "admin_pages/ride_form.html",
                {
                    "ride": ride,
                }
            )

        images = request.FILES.getlist(
            "images"
        )

        video = request.FILES.get(
            "video"
        )

        try:

            with transaction.atomic():

                ride.name = name
                ride.description = description
                ride.duration = duration
                ride.safety_notes = safety_notes
                ride.is_featured = is_featured
                ride.is_active = is_active

                ride.save()

                # Add new images
                for image in images:

                    RideMedia.objects.create(
                        ride=ride,
                        media_type="image",
                        image=image,
                    )

                # Add new video
                if video:

                    RideMedia.objects.create(
                        ride=ride,
                        media_type="video",
                        video=video,
                    )

        except Exception as error:

            print("RIDE UPDATE ERROR:", error)

            messages.error(
                request,
                f"Unable to update ride: {error}"
            )

            return render(
                request,
                "admin_pages/ride_form.html",
                {
                    "ride": ride,
                }
            )

        messages.success(
            request,
            "Ride updated successfully."
        )

        return redirect(
            "ride_list"
        )

    return render(
        request,
        "admin_pages/ride_form.html",
        {
            "ride": ride,
        }
    )

@login_required(login_url="admin_login")
def ride_delete(request, pk):

    ride = get_object_or_404(
        Ride,
        pk=pk
    )

    if request.method == "POST":

        ride.delete()

        messages.success(
            request,
            "Ride deleted successfully."
        )

    return redirect(
        "ride_list"
    )



@login_required(login_url="admin_login")
def ride_media_delete(request, pk):

    media = get_object_or_404(
        RideMedia,
        pk=pk
    )

    ride_id = media.ride.id

    if request.method == "POST":

        media.delete()

        messages.success(
            request,
            "Ride media deleted successfully."
        )

    return redirect(
        "ride_update",
        pk=ride_id
    )




# ==========================================
# RIDE PRICE CRUD
# ==========================================

@login_required(login_url="admin_login")
def ride_price_list(request):

    prices_qs = (
        RidePrice.objects
        .select_related("ride")
        .all()
        .order_by("-start_date")
    )

    paginator = Paginator(
        prices_qs,
        10
    )

    page_number = request.GET.get(
        "page"
    )

    prices = paginator.get_page(
        page_number
    )

    rides = Ride.objects.all().order_by(
        "name"
    )

    return render(
        request,
        "admin_pages/ride_price_list.html",
        {
            "prices": prices,
            "rides": rides,
        }
    )


@login_required(login_url="admin_login")
def ride_price_create(request):

    rides = Ride.objects.filter(
        is_active=True
    ).order_by("name")

    if request.method == "POST":

        ride_id = request.POST.get(
            "ride"
        )

        start_date = request.POST.get(
            "start_date"
        )

        end_date = request.POST.get(
            "end_date"
        )

        price = request.POST.get(
            "price"
        )

        is_active = (
            request.POST.get("is_active")
            == "on"
        )


        if not ride_id:

            messages.error(
                request,
                "Please select a ride."
            )

            return render(
                request,
                "admin_pages/ride_price_create.html",
                {
                    "rides": rides
                }
            )


        if not start_date or not end_date:

            messages.error(
                request,
                "Start date and end date are required."
            )

            return render(
                request,
                "admin_pages/ride_price_create.html",
                {
                    "rides": rides
                }
            )


        if end_date < start_date:

            messages.error(
                request,
                "End date cannot be before start date."
            )

            return render(
                request,
                "admin_pages/ride_price_create.html",
                {
                    "rides": rides
                }
            )


        if not price:

            messages.error(
                request,
                "Price is required."
            )

            return render(
                request,
                "admin_pages/ride_price_create.html",
                {
                    "rides": rides
                }
            )


        ride = get_object_or_404(
            Ride,
            pk=ride_id
        )


        RidePrice.objects.create(
            ride=ride,
            start_date=start_date,
            end_date=end_date,
            price=price,
            is_active=is_active,
        )


        messages.success(
            request,
            "Ride price added successfully."
        )

        return redirect(
            "ride_price_list"
        )


    return render(
        request,
        "admin_pages/ride_price_create.html",
        {
            "rides": rides
        }
    )


@login_required(login_url="admin_login")
def ride_price_update(request, pk):

    ride_price = get_object_or_404(
        RidePrice,
        pk=pk
    )

    if request.method == "POST":

        ride_id = request.POST.get(
            "ride"
        )

        start_date = request.POST.get(
            "start_date"
        )

        end_date = request.POST.get(
            "end_date"
        )

        price = request.POST.get(
            "price"
        )

        is_active = (
            request.POST.get("is_active")
            == "on"
        )


        if not ride_id:

            messages.error(
                request,
                "Please select a ride."
            )

            return redirect(
                "ride_price_list"
            )


        if not start_date or not end_date:

            messages.error(
                request,
                "Start date and end date are required."
            )

            return redirect(
                "ride_price_list"
            )


        if end_date < start_date:

            messages.error(
                request,
                "End date cannot be before start date."
            )

            return redirect(
                "ride_price_list"
            )


        if not price:

            messages.error(
                request,
                "Price is required."
            )

            return redirect(
                "ride_price_list"
            )


        ride_price.ride = get_object_or_404(
            Ride,
            pk=ride_id
        )

        ride_price.start_date = start_date
        ride_price.end_date = end_date
        ride_price.price = price
        ride_price.is_active = is_active

        ride_price.save()


        messages.success(
            request,
            "Ride price updated successfully."
        )

    return redirect(
        "ride_price_list"
    )



@login_required(login_url="admin_login")
def ride_price_delete(request, pk):

    ride_price = get_object_or_404(
        RidePrice,
        pk=pk
    )

    if request.method == "POST":

        ride_price.delete()

        messages.success(
            request,
            "Ride price deleted successfully."
        )

    return redirect(
        "ride_price_list"
    )




# # ==========================
# # Booking CRUD
# # ==========================


@_admin_required
def booking_list(request):

    bookings_qs = (
        Booking.objects
        .select_related(
            "ride",
            "ride_price",
            "coupon",
            "payment",
            "ticket",
        )
        .prefetch_related(
            "participants"
        )
        .order_by("-created_at")
    )

    search = request.GET.get(
        "search",
        "",
    ).strip()

    status = request.GET.get(
        "status",
        "",
    ).strip()

    if search:
        bookings_qs = bookings_qs.filter(
            Q(customer_name__icontains=search)
            | Q(customer_email__icontains=search)
            | Q(customer_phone__icontains=search)
            | Q(ride__name__icontains=search)
            | Q(booking_id__icontains=search)
        )

    if status:
        bookings_qs = bookings_qs.filter(
            status=status
        )

    paginator = Paginator(
        bookings_qs,
        10,
    )

    bookings = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "admin_pages/booking_list.html",
        {
            "bookings": bookings,
            "search": search,
            "selected_status": status,
            "status_choices": Booking.STATUS_CHOICES,
        },
    )


@_admin_required
@transaction.atomic
def booking_create(request):

    rides = (
        Ride.objects
        .filter(is_active=True)
        .order_by("name")
    )

    prices = (
        RidePrice.objects
        .filter(is_active=True)
        .select_related("ride")
        .order_by(
            "ride__name",
            "-start_date",
        )
    )

    if request.method == "POST":

        # =====================================
        # CUSTOMER DETAILS
        # =====================================

        customer_name = request.POST.get(
            "customer_name",
            "",
        ).strip()

        customer_email = request.POST.get(
            "customer_email",
            "",
        ).strip()

        customer_phone = request.POST.get(
            "customer_phone",
            "",
        ).strip()

        customer_pincode = request.POST.get(
            "customer_pincode",
            "",
        ).strip()

        time_slot = request.POST.get(
            "time_slot",
            "",
        ).strip()

        # =====================================
        # RIDE DETAILS
        # =====================================

        ride_id = request.POST.get(
            "ride"
        )

        ride_price_id = request.POST.get(
            "ride_price"
        )

        booking_date_raw = request.POST.get(
            "booking_date",
            "",
        ).strip()

        quantity_raw = request.POST.get(
            "quantity",
            "1",
        )

        # =====================================
        # CUSTOMER VALIDATION
        # =====================================

        if not customer_name:
            messages.error(
                request,
                "Customer name is required.",
            )
            return redirect("booking_create")

        if not customer_email:
            messages.error(
                request,
                "Customer email is required.",
            )
            return redirect("booking_create")

        if (
            not customer_phone.isdigit()
            or len(customer_phone) != 10
        ):
            messages.error(
                request,
                "Enter a valid 10-digit customer phone number.",
            )
            return redirect("booking_create")

        if (
            not customer_pincode.isdigit()
            or len(customer_pincode) != 6
        ):
            messages.error(
                request,
                "Enter a valid 6-digit PIN code.",
            )
            return redirect("booking_create")

        if not time_slot:
            messages.error(
                request,
                "Time slot is required.",
            )
            return redirect("booking_create")

        # =====================================
        # QUANTITY VALIDATION
        # =====================================

        try:
            quantity = int(quantity_raw)
        except (TypeError, ValueError):
            quantity = 0

        if quantity < 1:
            messages.error(
                request,
                "Quantity must be at least 1.",
            )
            return redirect("booking_create")

        # =====================================
        # DATE VALIDATION
        # =====================================

        selected_date = parse_date(
            booking_date_raw
        )

        if selected_date is None:
            messages.error(
                request,
                "Please select a valid booking date.",
            )
            return redirect("booking_create")

        # =====================================
        # RIDE AND PRICE
        # =====================================

        ride = get_object_or_404(
            Ride,
            pk=ride_id,
            is_active=True,
        )

        ride_price = get_object_or_404(
            RidePrice,
            pk=ride_price_id,
            is_active=True,
        )

        if ride_price.ride_id != ride.id:
            messages.error(
                request,
                "Selected price does not belong to this ride.",
            )
            return redirect("booking_create")

        if not (
            ride_price.start_date
            <= selected_date
            <= ride_price.end_date
        ):
            messages.error(
                request,
                "The selected price is not valid for this booking date.",
            )
            return redirect("booking_create")

        # =====================================
        # PRICE CALCULATION
        # =====================================

        price_per_person = (
            ride_price.price
        )

        subtotal = (
            price_per_person
            * Decimal(quantity)
        )

        # =====================================
        # CREATE BOOKING
        # =====================================

        booking = Booking.objects.create(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            customer_pincode=customer_pincode,
            time_slot=time_slot,

            ride=ride,
            ride_price=ride_price,
            booking_date=selected_date,

            quantity=quantity,
            price_per_person=price_per_person,

            photo_addon=False,
            video_addon=False,
            addon_amount=Decimal("0.00"),

            discount_amount=Decimal("0.00"),
            subtotal=subtotal,
            total_amount=subtotal,

            status="pending",
        )

        # =====================================
        # PARTICIPANTS
        # =====================================

        participant_names = (
            request.POST.getlist(
                "participant_name"
            )
        )

        participant_ages = (
            request.POST.getlist(
                "participant_age"
            )
        )

        participant_weights = (
            request.POST.getlist(
                "participant_weight"
            )
        )

        participant_phones = (
            request.POST.getlist(
                "participant_phone"
            )
        )

        for index in range(quantity):

            name = (
                participant_names[index].strip()
                if index < len(participant_names)
                else ""
            )

            if not name:
                continue

            age = None

            if index < len(participant_ages):
                try:
                    age = int(
                        participant_ages[index]
                    )
                except (TypeError, ValueError):
                    age = None

            weight = None

            if index < len(participant_weights):
                try:
                    weight = Decimal(
                        participant_weights[index]
                    )
                except (
                    TypeError,
                    ValueError,
                    InvalidOperation,
                ):
                    weight = None

            participant_phone = (
                participant_phones[index].strip()
                if index < len(participant_phones)
                else ""
            )

            BookingPerson.objects.create(
                booking=booking,
                full_name=name,
                age=age,
                weight=weight,
                phone=participant_phone,
            )

        messages.success(
            request,
            "Booking created successfully.",
        )

        return redirect(
            "booking_detail",
            pk=booking.pk,
        )

    return render(
        request,
        "admin_pages/booking_form.html",
        {
            "rides": rides,
            "prices": prices,
        },
    )

@_admin_required
@transaction.atomic
def booking_update(request, pk):

    booking = get_object_or_404(
        Booking.objects.select_related(
            "ride",
            "ride_price",
            "coupon",
        ),
        pk=pk,
    )

    rides = (
        Ride.objects
        .filter(is_active=True)
        .order_by("name")
    )

    prices = (
        RidePrice.objects
        .filter(is_active=True)
        .select_related("ride")
        .order_by(
            "ride__name",
            "-start_date",
        )
    )

    if request.method == "POST":

        customer_name = request.POST.get(
            "customer_name",
            "",
        ).strip()

        customer_email = request.POST.get(
            "customer_email",
            "",
        ).strip()

        customer_phone = request.POST.get(
            "customer_phone",
            "",
        ).strip()

        customer_pincode = request.POST.get(
            "customer_pincode",
            "",
        ).strip()

        time_slot = request.POST.get(
            "time_slot",
            "",
        ).strip()

        ride_id = request.POST.get("ride")
        ride_price_id = request.POST.get("ride_price")

        booking_date_raw = request.POST.get(
            "booking_date",
            "",
        ).strip()

        quantity_raw = request.POST.get(
            "quantity",
            "1",
        )

        if not customer_name:
            messages.error(
                request,
                "Customer name is required.",
            )
            return redirect(
                "booking_update",
                pk=booking.pk,
            )

        if not customer_email:
            messages.error(
                request,
                "Customer email is required.",
            )
            return redirect(
                "booking_update",
                pk=booking.pk,
            )

        if (
            not customer_phone.isdigit()
            or len(customer_phone) != 10
        ):
            messages.error(
                request,
                "Enter a valid 10-digit customer phone number.",
            )
            return redirect(
                "booking_update",
                pk=booking.pk,
            )

        if (
            not customer_pincode.isdigit()
            or len(customer_pincode) != 6
        ):
            messages.error(
                request,
                "Enter a valid 6-digit PIN code.",
            )
            return redirect(
                "booking_update",
                pk=booking.pk,
            )

        if not time_slot:
            messages.error(
                request,
                "Time slot is required.",
            )
            return redirect(
                "booking_update",
                pk=booking.pk,
            )

        try:
            quantity = int(quantity_raw)
        except (TypeError, ValueError):
            quantity = 0

        if quantity < 1:
            messages.error(
                request,
                "Quantity must be at least 1.",
            )
            return redirect(
                "booking_update",
                pk=booking.pk,
            )

        selected_date = parse_date(
            booking_date_raw
        )

        if selected_date is None:
            messages.error(
                request,
                "Please select a valid booking date.",
            )
            return redirect(
                "booking_update",
                pk=booking.pk,
            )

        ride = get_object_or_404(
            Ride,
            pk=ride_id,
            is_active=True,
        )

        ride_price = get_object_or_404(
            RidePrice,
            pk=ride_price_id,
            is_active=True,
        )

        if ride_price.ride_id != ride.id:
            messages.error(
                request,
                "Selected price does not belong to this ride.",
            )
            return redirect(
                "booking_update",
                pk=booking.pk,
            )

        if not (
            ride_price.start_date
            <= selected_date
            <= ride_price.end_date
        ):
            messages.error(
                request,
                "The selected price is not valid for this booking date.",
            )
            return redirect(
                "booking_update",
                pk=booking.pk,
            )

        price_per_person = ride_price.price

        subtotal = (
            price_per_person
            * Decimal(quantity)
        )

        booking.customer_name = customer_name
        booking.customer_email = customer_email
        booking.customer_phone = customer_phone
        booking.customer_pincode = customer_pincode
        booking.time_slot = time_slot

        booking.ride = ride
        booking.ride_price = ride_price
        booking.booking_date = selected_date
        booking.quantity = quantity
        booking.price_per_person = price_per_person
        booking.subtotal = subtotal
        booking.total_amount = subtotal

        booking.save()

        messages.success(
            request,
            "Booking updated successfully.",
        )

        return redirect(
            "booking_detail",
            pk=booking.pk,
        )

    return render(
        request,
        "admin_pages/booking_form.html",
        {
            "booking": booking,
            "rides": rides,
            "prices": prices,
        },
    )

@_admin_required
def booking_detail(request, pk):

    booking = get_object_or_404(
        Booking.objects
        .select_related(
            "ride",
            "ride_price",
            "coupon",
            "payment",
            "ticket",
        )
        .prefetch_related(
            "participants"
        ),
        pk=pk,
    )

    payment = getattr(
        booking,
        "payment",
        None,
    )

    ticket = getattr(
        booking,
        "ticket",
        None,
    )

    return render(
        request,
        "admin_pages/booking_detail.html",
        {
            "booking": booking,
            "payment": payment,
            "ticket": ticket,
        },
    )



@_admin_required
def booking_status_update(request, pk):

    booking = get_object_or_404(
        Booking,
        pk=pk
    )


    if request.method == "POST":

        status = request.POST.get(
            "status"
        )


        valid_statuses = [
            choice[0]
            for choice in Booking.STATUS_CHOICES
        ]


        if status in valid_statuses:

            booking.status = status

            booking.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            messages.success(
                request,
                "Booking status updated."
            )


    return redirect(
        "booking_detail",
        pk=booking.pk
    )



@_admin_required
def booking_delete(request, pk):

    booking = get_object_or_404(
        Booking,
        pk=pk
    )


    if request.method == "POST":

        booking.delete()

        messages.success(
            request,
            "Booking deleted successfully."
        )


    return redirect(
        "booking_list"
    )




# # ==========================
# # transaction 
# # ==========================

@_admin_required
def transaction_list(request):

    payments_qs = (
        Payment.objects
        .select_related(
            "booking",
            "booking__user",
            "booking__ride",
        )
        .order_by("-created_at")
    )

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        payments_qs = payments_qs.filter(
            Q(booking__user__full_name__icontains=search) |
            Q(booking__user__email__icontains=search) |
            Q(booking__user__phone__icontains=search) |
            Q(gateway_order_id__icontains=search) |
            Q(gateway_payment_id__icontains=search)
        )

    if status:
        payments_qs = payments_qs.filter(
            status=status
        )

    paginator = Paginator(
        payments_qs,
        10
    )

    payments = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "admin_pages/transaction_list.html",
        {
            "payments": payments,
            "search": search,
            "selected_status": status,
            "status_choices": Payment.STATUS_CHOICES,
        }
    )


@_admin_required
def transaction_detail(request, pk):

    payment = get_object_or_404(
        Payment.objects.select_related(
            "booking",
            "booking__user",
            "booking__ride",
            "booking__ride_price",
        ),
        pk=pk
    )

    return render(
        request,
        "admin_pages/transaction_detail.html",
        {
            "payment": payment
        }
    )




# # ==========================
# # coupens
# # ==========================

@_admin_required
def coupon_list(request):

    coupons_qs = (
        Coupon.objects
        .prefetch_related("rides")
        .all()
    )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    status = request.GET.get(
        "status",
        ""
    ).strip()

    if search:
        coupons_qs = coupons_qs.filter(
            Q(code__icontains=search) |
            Q(rides__name__icontains=search)
        ).distinct()

    if status == "active":
        coupons_qs = coupons_qs.filter(
            is_active=True
        )

    elif status == "inactive":
        coupons_qs = coupons_qs.filter(
            is_active=False
        )

    paginator = Paginator(
        coupons_qs,
        10
    )

    coupons = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "admin_pages/coupon_list.html",
        {
            "coupons": coupons,
            "search": search,
            "selected_status": status,
        }
    )


@_admin_required
def coupon_create(request):

    rides = Ride.objects.filter(
        is_active=True
    ).order_by("name")

    if request.method == "POST":

        code = request.POST.get(
            "code",
            ""
        ).strip().upper()

        ride_ids = request.POST.getlist(
            "rides"
        )

        discount_type = request.POST.get(
            "discount_type"
        )

        discount_value = request.POST.get(
            "discount_value"
        )

        valid_from = request.POST.get(
            "valid_from"
        )

        valid_until = request.POST.get(
            "valid_until"
        )

        minimum_amount = request.POST.get(
            "minimum_amount"
        ) or 0

        usage_limit = request.POST.get(
            "usage_limit"
        ) or None

        is_active = (
            request.POST.get("is_active")
            == "on"
        )

        if not code:
            messages.error(
                request,
                "Coupon code is required."
            )

            return render(
                request,
                "admin_pages/coupon_form.html",
                {
                    "rides": rides,
                    "form_data": request.POST,
                }
            )

        if Coupon.objects.filter(
            code__iexact=code
        ).exists():

            messages.error(
                request,
                "This coupon code already exists."
            )

            return render(
                request,
                "admin_pages/coupon_form.html",
                {
                    "rides": rides,
                    "form_data": request.POST,
                }
            )

        if not ride_ids:
            messages.error(
                request,
                "Please select at least one ride."
            )

            return render(
                request,
                "admin_pages/coupon_form.html",
                {
                    "rides": rides,
                    "form_data": request.POST,
                }
            )

        try:

            coupon = Coupon.objects.create(
                code=code,
                discount_type=discount_type,
                discount_value=discount_value,
                valid_from=valid_from,
                valid_until=valid_until,
                minimum_amount=minimum_amount,
                usage_limit=usage_limit,
                is_active=is_active,
            )

            coupon.rides.set(
                ride_ids
            )

            messages.success(
                request,
                "Coupon created successfully."
            )

            return redirect(
                "coupon_list"
            )

        except Exception as e:

            messages.error(
                request,
                f"Unable to create coupon: {e}"
            )

    return render(
        request,
        "admin_pages/coupon_form.html",
        {
            "rides": rides
        }
    )


@_admin_required
def coupon_update(request, pk):

    coupon = get_object_or_404(
        Coupon,
        pk=pk
    )

    rides = Ride.objects.filter(
        is_active=True
    ).order_by("name")

    if request.method == "POST":

        code = request.POST.get(
            "code",
            ""
        ).strip().upper()

        ride_ids = request.POST.getlist(
            "rides"
        )

        if not code:
            messages.error(
                request,
                "Coupon code is required."
            )

            return render(
                request,
                "admin_pages/coupon_form.html",
                {
                    "coupon": coupon,
                    "rides": rides,
                }
            )

        if Coupon.objects.filter(
            code__iexact=code
        ).exclude(
            pk=coupon.pk
        ).exists():

            messages.error(
                request,
                "This coupon code already exists."
            )

            return render(
                request,
                "admin_pages/coupon_form.html",
                {
                    "coupon": coupon,
                    "rides": rides,
                }
            )

        if not ride_ids:
            messages.error(
                request,
                "Please select at least one ride."
            )

            return render(
                request,
                "admin_pages/coupon_form.html",
                {
                    "coupon": coupon,
                    "rides": rides,
                }
            )

        try:

            coupon.code = code

            coupon.discount_type = (
                request.POST.get(
                    "discount_type"
                )
            )

            coupon.discount_value = (
                request.POST.get(
                    "discount_value"
                )
            )

            coupon.valid_from = (
                request.POST.get(
                    "valid_from"
                )
            )

            coupon.valid_until = (
                request.POST.get(
                    "valid_until"
                )
            )

            coupon.minimum_amount = (
                request.POST.get(
                    "minimum_amount"
                ) or 0
            )

            coupon.usage_limit = (
                request.POST.get(
                    "usage_limit"
                ) or None
            )

            coupon.is_active = (
                request.POST.get(
                    "is_active"
                ) == "on"
            )

            coupon.save()

            coupon.rides.set(
                ride_ids
            )

            messages.success(
                request,
                "Coupon updated successfully."
            )

            return redirect(
                "coupon_list"
            )

        except Exception as e:

            messages.error(
                request,
                f"Unable to update coupon: {e}"
            )

    return render(
        request,
        "admin_pages/coupon_form.html",
        {
            "coupon": coupon,
            "rides": rides,
        }
    )



@_admin_required
def coupon_delete(request, pk):

    coupon = get_object_or_404(
        Coupon,
        pk=pk
    )

    if request.method == "POST":

        code = coupon.code

        coupon.delete()

        messages.success(
            request,
            f"Coupon {code} deleted successfully."
        )

    return redirect(
        "coupon_list"
    )



# ==========================================
# TESTIMONIALS (ADMIN)
# ==========================================

# @login_required(login_url="admin_login")
# def testimonial_list(request):
#     testimonials = Paginator(Testimonial.objects.all().order_by("-created_at"), 10).get_page(request.GET.get("page"))
#     return render(request, "admin_pages/review_list.html", {"testimonials": testimonials})

@login_required(login_url="admin_login")
def testimonial_list(request):
    testimonials_qs = Testimonial.objects.all().order_by("-created_at")

    paginator = Paginator(testimonials_qs, 10)  # 10 testimonials per page

    page_number = request.GET.get("page")
    testimonials = paginator.get_page(page_number)

    return render(
        request,
        "admin_pages/review_list.html",
        {"testimonials": testimonials}
    )


@login_required(login_url="admin_login")
def testimonial_create(request):
    form = TestimonialForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Testimonial added!")
        return redirect("review_list")
    return render(request, "admin_pages/create_review.html", {"form": form})


@login_required(login_url="admin_login")
def testimonial_update(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    form = TestimonialForm(request.POST or None, request.FILES or None, instance=testimonial)
    if form.is_valid():
        form.save()
        messages.success(request, "Testimonial updated!")
        return redirect("review_list")
    return render(request, "admin_pages/create_review.html", {"form": form, "testimonial": testimonial})


@login_required(login_url="admin_login")
def testimonial_delete(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == "POST":
        testimonial.delete()
        messages.success(request, "Testimonial deleted!")
    return redirect("review_list")








   # ---------------------------
        # user sign up
    # ---------------------------

def user_signup(request):

    if request.session.get("user_id"):
        return redirect("home")

    if request.method == "POST":

        full_name = request.POST.get(
            "full_name",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip().lower()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )


        # ---------------------------
        # VALIDATION
        # ---------------------------

        if not full_name:
            messages.error(
                request,
                "Full name is required."
            )

            return render(
                request,
                "authenticate/signup.html",
                {
                    "form_data": request.POST
                }
            )


        if not email:
            messages.error(
                request,
                "Email address is required."
            )

            return render(
                request,
                "authenticate/signup.html",
                {
                    "form_data": request.POST
                }
            )


        if UserProfile.objects.filter(
            email__iexact=email
        ).exists():

            messages.error(
                request,
                "An account with this email already exists."
            )

            return render(
                request,
                "authenticate/signup.html",
                {
                    "form_data": request.POST
                }
            )


        if UserProfile.objects.filter(
            phone=phone
        ).exists():

            messages.error(
                request,
                "An account with this phone number already exists."
            )

            return render(
                request,
                "authenticate/signup.html",
                {
                    "form_data": request.POST
                }
            )


        if len(password) < 8:

            messages.error(
                request,
                "Password must contain at least 8 characters."
            )

            return render(
                request,
                "authenticate/signup.html",
                {
                    "form_data": request.POST
                }
            )


        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return render(
                request,
                "authenticate/signup.html",
                {
                    "form_data": request.POST
                }
            )


        # ---------------------------
        # CREATE USER
        # ---------------------------

        user = UserProfile.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,

            # IMPORTANT
            password=make_password(
                password
            )
        )


        # Automatically login
        request.session["user_id"] = user.id

        request.session[
            "user_name"
        ] = user.full_name


        messages.success(
            request,
            "Your account has been created successfully."
        )


        return redirect("home")


    return render(
        request,
        "authenticate/signup.html"
    )




def user_signin(request):

    if request.session.get("user_id"):
        return redirect("/bookings/")


    if request.method == "POST":

        email = request.POST.get(
            "email",
            ""
        ).strip().lower()

        password = request.POST.get(
            "password",
            ""
        )


        try:

            user = UserProfile.objects.get(
                email__iexact=email
            )

        except UserProfile.DoesNotExist:

            messages.error(
                request,
                "Invalid email or password."
            )

            return render(
                request,
                "authenticate/signin.html",
                {
                    "email": email
                }
            )


        if not check_password(
            password,
            user.password
        ):

            messages.error(
                request,
                "Invalid email or password."
            )

            return render(
                request,
                "authenticate/signin.html",
                {
                    "email": email
                }
            )


        request.session[
            "user_id"
        ] = user.id

        request.session[
            "user_name"
        ] = user.full_name


        messages.success(
            request,
            f"Welcome back, {user.full_name}!"
        )


        return redirect("home")


    return render(
        request,
        "authenticate/signin.html"
    )



def user_logout(request):

    request.session.flush()

    messages.success(
        request,
        "You have been logged out."
    )

    return redirect(
        "user_signin"
    )







 # ---------------------------
        # Home 
 # ---------------------------

def home(request):

    # Get every RideMedia record that actually has a video file.
    # We are not checking media_type here.
    video_media = (
        RideMedia.objects
        .exclude(video="")
        .filter(video__isnull=False)
        .order_by("-created_at")
    )

    gallery_videos = (
       GalleryItem.objects
       .filter(video__isnull=False)
       .exclude(video="")
       .order_by("-uploaded_at")[:10]
    )

    gallery_images = (
        GalleryItem.objects
        .filter(image__isnull=False)
        .exclude(image="")
        .select_related("category")
        .order_by("-uploaded_at")[:8]
    )

    rides = (
        Ride.objects
        .filter(is_active=True)
        .prefetch_related(
            Prefetch(
                "media",
                queryset=video_media,
                to_attr="uploaded_videos",
            )
        )
    )
    testimonials = (
        Testimonial.objects
        .all()
        .order_by("-created_at")
    )

    blogs = Blog.objects.all().order_by("-created_at")[:3]

    return render(
        request,
        "frontend/index.html",
        {
            "rides": rides,
            "gallery_videos": gallery_videos,
            "gallery_images": gallery_images,
            "testimonials": testimonials,
            "blogs": blogs,
        },
    )




def rides(request):

    today = date.today()

    ride_images = (
        RideMedia.objects
        .filter(
            media_type="image",
            image__isnull=False,
        )
        .exclude(image="")
        .order_by("created_at")
    )

    current_prices = (
        RidePrice.objects
        .filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        )
        .order_by(
            "-start_date",
            "-created_at",
        )
    )

    rides_queryset = (
        Ride.objects
        .filter(is_active=True)
        .prefetch_related(
            Prefetch(
                "media",
                queryset=ride_images,
                to_attr="ride_images",
            ),
            Prefetch(
                "prices",
                queryset=current_prices,
                to_attr="current_prices",
            ),
        )
        .order_by(
            "-is_featured",
            "-created_at",
        )
    )

    paginator = Paginator(
        rides_queryset,
        6,
    )

    rides = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "frontend/rides.html",
        {
            "rides": rides,
        },
    )


def ride_detail(request, slug):

    ride = get_object_or_404(
        Ride,
        slug=slug,
        is_active=True
    )

    return render(
        request,
        'frontend/ride_detail.html',
        {
            'ride': ride
        }
    )

def bookings(request):

    ride_images = (
        RideMedia.objects
        .filter(
            media_type="image",
            image__isnull=False,
        )
        .exclude(image="")
        .order_by("-created_at")
    )

    active_prices = (
        RidePrice.objects
        .filter(is_active=True)
        .order_by("-start_date", "-created_at")
    )

    rides = (
        Ride.objects
        .filter(
            is_active=True,
            prices__is_active=True,
        )
        .distinct()
        .prefetch_related(
            Prefetch(
                "media",
                queryset=ride_images,
                to_attr="booking_images",
            ),
            Prefetch(
                "prices",
                queryset=active_prices,
                to_attr="current_prices",
            ),
        )
        .order_by("name")
    )

    return render(
        request,
        "frontend/booking.html",
        {
            "rides": rides,
        },
    )

# def booking_review(request):

#     if request.method != "POST":
#         return redirect("bookings")

#     ride_id = request.POST.get("ride_id")
#     booking_date_raw = request.POST.get("booking_date")
#     time_slot = request.POST.get("time_slot", "").strip()

#     participant_names = request.POST.getlist(
#         "participant_name[]"
#     )

#     participant_ages = request.POST.getlist(
#         "participant_age[]"
#     )

#     participant_weights = request.POST.getlist(
#         "participant_weight[]"
#     )

#     participant_phones = request.POST.getlist(
#         "participant_phone[]"
#     )

#     if not ride_id:
#         messages.error(
#             request,
#             "Please select a ride.",
#         )
#         return redirect("bookings")

#     booking_date = parse_date(
#         booking_date_raw or ""
#     )

#     if not booking_date:
#         messages.error(
#             request,
#             "Please select a valid booking date.",
#         )
#         return redirect("bookings")

#     if booking_date < date.today():
#         messages.error(
#             request,
#             "The booking date cannot be in the past.",
#         )
#         return redirect("bookings")

#     if not time_slot:
#         messages.error(
#             request,
#             "Please select a time slot.",
#         )
#         return redirect("bookings")

#     if not participant_names:
#         messages.error(
#             request,
#             "Please add at least one participant.",
#         )
#         return redirect("bookings")

#     ride = get_object_or_404(
#         Ride,
#         id=ride_id,
#         is_active=True,
#     )

#     # Find the price valid for the selected booking date.
#     ride_price = (
#         RidePrice.objects
#         .filter(
#             ride=ride,
#             is_active=True,
#             start_date__lte=booking_date,
#             end_date__gte=booking_date,
#         )
#         .order_by("-start_date", "-created_at")
#         .first()
#     )

#     if not ride_price:
#         messages.error(
#             request,
#             "No active price is available for this ride "
#             "on the selected date.",
#         )
#         return redirect("bookings")

#     participants = []

#     total_rows = len(participant_names)

#     for index in range(total_rows):

#         full_name = participant_names[index].strip()

#         age_raw = (
#             participant_ages[index]
#             if index < len(participant_ages)
#             else ""
#         )

#         weight_raw = (
#             participant_weights[index]
#             if index < len(participant_weights)
#             else ""
#         )

#         phone = (
#             participant_phones[index].strip()
#             if index < len(participant_phones)
#             else ""
#         )

#         if not full_name:
#             messages.error(
#                 request,
#                 "Every participant must have a name.",
#             )
#             return redirect("bookings")

#         try:
#             age = int(age_raw)
#         except (TypeError, ValueError):
#             messages.error(
#                 request,
#                 f"Enter a valid age for {full_name}.",
#             )
#             return redirect("bookings")

#         try:
#             weight = Decimal(weight_raw)
#         except (InvalidOperation, TypeError, ValueError):
#             messages.error(
#                 request,
#                 f"Enter a valid weight for {full_name}.",
#             )
#             return redirect("bookings")

#         participants.append(
#             {
#                 "full_name": full_name,
#                 "age": age,
#                 "weight": str(weight),
#                 "phone": phone,
#             }
#         )

#     quantity = len(participants)

#     price_per_person = ride_price.price

#     participant_subtotal = (
#         price_per_person * quantity
#     )

#     photo_addon = (
#         request.POST.get("photo_addon") == "1"
#     )

#     video_addon = (
#         request.POST.get("video_addon") == "1"
#     )

#     photo_addon_price = (
#         Decimal("250.00")
#         if photo_addon
#         else Decimal("0.00")
#     )

#     video_addon_price = (
#         Decimal("450.00")
#         if video_addon
#         else Decimal("0.00")
#     )

#     addon_total = (
#         photo_addon_price
#         + video_addon_price
#     )

#     subtotal = (
#         participant_subtotal
#         + addon_total
#     )

#     # Coupon is validated again on the server.
#     coupon_code = request.POST.get(
#         "coupon_code",
#         "",
#     ).strip().upper()

#     coupon = None
#     discount_amount = Decimal("0.00")

#     if coupon_code:

#         coupon = (
#             Coupon.objects
#             .filter(
#                 code__iexact=coupon_code,
#                 is_active=True,
#                 valid_from__lte=booking_date,
#                 valid_until__gte=booking_date,
#             )
#             .first()
#         )

#         if coupon:

#             ride_is_allowed = (
#                 not coupon.rides.exists()
#                 or coupon.rides.filter(
#                     id=ride.id
#                 ).exists()
#             )

#             usage_is_allowed = (
#                 coupon.usage_limit is None
#                 or coupon.times_used
#                 < coupon.usage_limit
#             )

#             minimum_is_met = (
#                 subtotal
#                 >= coupon.minimum_amount
#             )

#             if (
#                 ride_is_allowed
#                 and usage_is_allowed
#                 and minimum_is_met
#             ):

#                 if (
#                     coupon.discount_type
#                     == "percentage"
#                 ):
#                     discount_amount = (
#                         subtotal
#                         * coupon.discount_value
#                         / Decimal("100")
#                     )
#                 else:
#                     discount_amount = (
#                         coupon.discount_value
#                     )

#                 discount_amount = min(
#                     discount_amount,
#                     subtotal,
#                 )

#             else:
#                 coupon = None

#     total_amount = (
#         subtotal - discount_amount
#     )

#     booking_data = {
#         "ride_id": ride.id,
#         "ride_price_id": ride_price.id,
#         "ride_name": ride.name,
#         "booking_date": booking_date.isoformat(),
#         "time_slot": time_slot,
#         "participants": participants,
#         "quantity": quantity,
#         "price_per_person": str(
#             price_per_person
#         ),
#         "participant_subtotal": str(
#             participant_subtotal
#         ),
#         "photo_addon": photo_addon,
#         "video_addon": video_addon,
#         "addon_total": str(addon_total),
#         "coupon_id": (
#             coupon.id if coupon else None
#         ),
#         "coupon_code": (
#             coupon.code if coupon else ""
#         ),
#         "discount_amount": str(
#             discount_amount
#         ),
#         "subtotal": str(subtotal),
#         "total_amount": str(total_amount),
#     }

#     request.session[
#         "pending_booking"
#     ] = booking_data

#     request.session.modified = True

#     return render(
#         request,
#         "frontend/booking_review.html",
#         {
#             "booking_data": booking_data,
#             "ride": ride,
#             "ride_price": ride_price,
#             "participants": participants,
#         },
#     )

def booking_review(request):

    # ==================================================
    # GET REQUEST
    # Reopen the review page using session data
    # ==================================================

    if request.method == "GET":

        booking_data = request.session.get(
            "pending_booking"
        )

        if not booking_data:
            messages.error(
                request,
                "Your booking session has expired. Please start again.",
            )
            return redirect("bookings")

        ride = get_object_or_404(
            Ride,
            id=booking_data.get("ride_id"),
            is_active=True,
        )

        ride_price = get_object_or_404(
            RidePrice,
            id=booking_data.get("ride_price_id"),
            ride=ride,
            is_active=True,
        )

        participants = booking_data.get(
            "participants",
            [],
        )

        return render(
            request,
            "frontend/booking_review.html",
            {
                "booking_data": booking_data,
                "ride": ride,
                "ride_price": ride_price,
                "participants": participants,
            },
        )

    # ==================================================
    # ALLOW ONLY POST AFTER THIS POINT
    # ==================================================

    if request.method != "POST":
        return redirect("bookings")

    # ==================================================
    # READ BOOKING FORM DATA
    # ==================================================

    ride_id = request.POST.get(
        "ride_id",
        "",
    ).strip()

    booking_date_raw = request.POST.get(
        "booking_date",
        "",
    ).strip()

    time_slot = request.POST.get(
        "time_slot",
        "",
    ).strip()

    participant_names = request.POST.getlist(
        "participant_name[]"
    )

    participant_ages = request.POST.getlist(
        "participant_age[]"
    )

    participant_weights = request.POST.getlist(
        "participant_weight[]"
    )

    participant_phones = request.POST.getlist(
        "participant_phone[]"
    )

    # ==================================================
    # VALIDATE BASIC BOOKING DATA
    # ==================================================

    if not ride_id:
        messages.error(
            request,
            "Please select a ride.",
        )
        return redirect("bookings")

    booking_date = parse_date(
        booking_date_raw
    )

    if booking_date is None:
        messages.error(
            request,
            "Please select a valid booking date.",
        )
        return redirect("bookings")

    if booking_date < date.today():
        messages.error(
            request,
            "The booking date cannot be in the past.",
        )
        return redirect("bookings")

    if not time_slot:
        messages.error(
            request,
            "Please select a time slot.",
        )
        return redirect("bookings")

    if not participant_names:
        messages.error(
            request,
            "Please add at least one participant.",
        )
        return redirect("bookings")

    # ==================================================
    # FIND SELECTED RIDE
    # ==================================================

    ride = get_object_or_404(
        Ride,
        id=ride_id,
        is_active=True,
    )

    # Find the price valid for the selected date.
    ride_price = (
        RidePrice.objects
        .filter(
            ride=ride,
            is_active=True,
            start_date__lte=booking_date,
            end_date__gte=booking_date,
        )
        .order_by(
            "-start_date",
            "-created_at",
        )
        .first()
    )

    if ride_price is None:
        messages.error(
            request,
            (
                f"No active price is available for "
                f"{ride.name} on {booking_date}."
            ),
        )
        return redirect("bookings")

    # ==================================================
    # VALIDATE PARTICIPANTS
    # ==================================================

    participants = []

    total_rows = len(participant_names)

    for index in range(total_rows):

        full_name = participant_names[index].strip()

        age_raw = (
            participant_ages[index]
            if index < len(participant_ages)
            else ""
        )

        weight_raw = (
            participant_weights[index]
            if index < len(participant_weights)
            else ""
        )

        phone = (
            participant_phones[index].strip()
            if index < len(participant_phones)
            else ""
        )

        if not full_name:
            messages.error(
                request,
                "Every participant must have a name.",
            )
            return redirect("bookings")

        try:
            age = int(age_raw)
        except (TypeError, ValueError):
            messages.error(
                request,
                f"Enter a valid age for {full_name}.",
            )
            return redirect("bookings")

        try:
            weight = Decimal(weight_raw)
        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ):
            messages.error(
                request,
                f"Enter a valid weight for {full_name}.",
            )
            return redirect("bookings")

        participants.append(
            {
                "full_name": full_name,
                "age": age,
                "weight": str(weight),
                "phone": phone,
            }
        )

    # ==================================================
    # CALCULATE RIDE TOTAL
    # ==================================================

    quantity = len(participants)

    price_per_person = ride_price.price

    participant_subtotal = (
        price_per_person * quantity
    )

    # ==================================================
    # ADD-ONS
    # ==================================================

    photo_addon = (
        request.POST.get("photo_addon") == "1"
    )

    video_addon = (
        request.POST.get("video_addon") == "1"
    )

    photo_addon_price = (
        Decimal("250.00")
        if photo_addon
        else Decimal("0.00")
    )

    video_addon_price = (
        Decimal("450.00")
        if video_addon
        else Decimal("0.00")
    )

    addon_total = (
        photo_addon_price
        + video_addon_price
    )

    subtotal = (
        participant_subtotal
        + addon_total
    )

    # ==================================================
    # COUPON
    # ==================================================

    coupon_code = request.POST.get(
        "coupon_code",
        "",
    ).strip().upper()

    coupon = None
    discount_amount = Decimal("0.00")

    if coupon_code:

        coupon = (
            Coupon.objects
            .filter(
                code__iexact=coupon_code,
                is_active=True,
                valid_from__lte=booking_date,
                valid_until__gte=booking_date,
            )
            .first()
        )

        if coupon:

            ride_is_allowed = (
                not coupon.rides.exists()
                or coupon.rides.filter(
                    id=ride.id
                ).exists()
            )

            usage_is_allowed = (
                coupon.usage_limit is None
                or coupon.times_used
                < coupon.usage_limit
            )

            minimum_is_met = (
                subtotal
                >= coupon.minimum_amount
            )

            if (
                ride_is_allowed
                and usage_is_allowed
                and minimum_is_met
            ):

                if (
                    coupon.discount_type
                    == "percentage"
                ):
                    discount_amount = (
                        subtotal
                        * coupon.discount_value
                        / Decimal("100")
                    )
                else:
                    discount_amount = (
                        coupon.discount_value
                    )

                discount_amount = min(
                    discount_amount,
                    subtotal,
                )

            else:
                coupon = None

    total_amount = (
        subtotal - discount_amount
    )

    # ==================================================
    # STORE DATA IN SESSION
    # ==================================================

    booking_data = {
        "ride_id": ride.id,
        "ride_price_id": ride_price.id,
        "ride_name": ride.name,

        "booking_date": (
            booking_date.isoformat()
        ),

        "time_slot": time_slot,

        "participants": participants,

        "quantity": quantity,

        "price_per_person": str(
            price_per_person
        ),

        "participant_subtotal": str(
            participant_subtotal
        ),

        "photo_addon": photo_addon,
        "video_addon": video_addon,

        "addon_total": str(
            addon_total
        ),

        "coupon_id": (
            coupon.id
            if coupon
            else None
        ),

        "coupon_code": (
            coupon.code
            if coupon
            else ""
        ),

        "discount_amount": str(
            discount_amount
        ),

        "subtotal": str(
            subtotal
        ),

        "total_amount": str(
            total_amount
        ),
    }

    request.session[
        "pending_booking"
    ] = booking_data

    request.session.modified = True

    # ==================================================
    # OPEN REVIEW PAGE
    # ==================================================

    return render(
        request,
        "frontend/booking_review.html",
        {
            "booking_data": booking_data,
            "ride": ride,
            "ride_price": ride_price,
            "participants": participants,
        },
    )




@transaction.atomic
def booking_confirm(request):

    if request.method != "POST":
        return redirect("bookings")

    booking_data = request.session.get(
        "pending_booking"
    )

    if not booking_data:
        messages.error(
            request,
            "Your booking session has expired. "
            "Please start again.",
        )
        return redirect("bookings")

    if not request.user.is_authenticated:
        messages.error(
            request,
            "Please sign in before completing the booking.",
        )
        return redirect("login")

    terms_accepted = (
        request.POST.get("terms_accepted") == "1"
    )

    if not terms_accepted:
        messages.error(
            request,
            "Please accept the terms and conditions.",
        )
        return redirect("booking_review")

    billing_full_name = request.POST.get(
        "billing_full_name",
        "",
    ).strip()

    billing_email = request.POST.get(
        "billing_email",
        "",
    ).strip()

    billing_phone = request.POST.get(
        "billing_phone",
        "",
    ).strip()

    billing_pincode = request.POST.get(
        "billing_pincode",
        "",
    ).strip()

    if not all(
        [
            billing_full_name,
            billing_email,
            billing_phone,
            billing_pincode,
        ]
    ):
        messages.error(
            request,
            "Please complete all billing details.",
        )
        return redirect("booking_review")

    ride = get_object_or_404(
        Ride,
        id=booking_data["ride_id"],
        is_active=True,
    )

    ride_price = get_object_or_404(
        RidePrice,
        id=booking_data["ride_price_id"],
        ride=ride,
        is_active=True,
    )

    booking_date = parse_date(
        booking_data["booking_date"]
    )

    # Revalidate price for selected date.
    if not (
        ride_price.start_date
        <= booking_date
        <= ride_price.end_date
    ):
        messages.error(
            request,
            "The selected ride price is no longer valid.",
        )
        return redirect("bookings")

    participants = booking_data[
        "participants"
    ]

    quantity = len(participants)

    price_per_person = ride_price.price

    participant_subtotal = (
        price_per_person * quantity
    )

    addon_total = Decimal(
        booking_data["addon_total"]
    )

    subtotal = (
        participant_subtotal
        + addon_total
    )

    coupon = None
    discount_amount = Decimal("0.00")

    coupon_id = booking_data.get(
        "coupon_id"
    )

    if coupon_id:

        coupon = (
            Coupon.objects
            .select_for_update()
            .filter(
                id=coupon_id,
                is_active=True,
                valid_from__lte=booking_date,
                valid_until__gte=booking_date,
            )
            .first()
        )

        if coupon:

            if (
                coupon.usage_limit is not None
                and coupon.times_used
                >= coupon.usage_limit
            ):
                coupon = None

        if coupon:

            ride_is_allowed = (
                not coupon.rides.exists()
                or coupon.rides.filter(
                    id=ride.id
                ).exists()
            )

            if (
                ride_is_allowed
                and subtotal
                >= coupon.minimum_amount
            ):

                if (
                    coupon.discount_type
                    == "percentage"
                ):
                    discount_amount = (
                        subtotal
                        * coupon.discount_value
                        / Decimal("100")
                    )
                else:
                    discount_amount = (
                        coupon.discount_value
                    )

                discount_amount = min(
                    discount_amount,
                    subtotal,
                )

            else:
                coupon = None

    total_amount = (
        subtotal - discount_amount
    )

    try:
        user_profile = request.user.userprofile
    except AttributeError:
        messages.error(
            request,
            "Your user profile could not be found.",
        )
        return redirect("bookings")

    booking = Booking.objects.create(
        user=user_profile,
        ride=ride,
        ride_price=ride_price,
        booking_date=booking_date,
        quantity=quantity,
        price_per_person=price_per_person,
        coupon=coupon,
        discount_amount=discount_amount,
        subtotal=subtotal,
        total_amount=total_amount,
        status="pending",
    )

    for participant in participants:

        BookingPerson.objects.create(
            booking=booking,
            full_name=participant[
                "full_name"
            ],
            age=participant["age"],
            weight=Decimal(
                participant["weight"]
            ),
            phone=participant["phone"],
        )

    Payment.objects.create(
        booking=booking,
        gateway="razorpay",
        amount=total_amount,
        status="created",
    )

    if coupon:
        coupon.times_used += 1
        coupon.save(
            update_fields=["times_used"]
        )

    request.session.pop(
        "pending_booking",
        None,
    )

    request.session[
        "current_booking_id"
    ] = str(booking.booking_id)

    # Replace this with your actual payment-start URL.
    return redirect(
        "payment_start",
        booking_id=booking.booking_id,
    )




def generate_ticket_qr(request, ticket):
    """
    Generate and save a QR code containing the ticket verification URL.
    """

    verification_url = request.build_absolute_uri(
        reverse(
            "verify_ticket",
            kwargs={
                "qr_token": ticket.qr_token,
            },
        )
    )

    qr_code = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr_code.add_data(verification_url)
    qr_code.make(fit=True)

    qr_image = qr_code.make_image(
        fill_color="black",
        back_color="white",
    )

    buffer = BytesIO()
    qr_image.save(buffer, format="PNG")

    ticket.qr_image.save(
        f"ticket-{ticket.ticket_id}.png",
        ContentFile(buffer.getvalue()),
        save=False,
    )



def generate_ticket_pdf(ticket):
    """
    Generate and save a basic PDF ticket.
    """

    booking = ticket.booking

    buffer = BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4,
    )

    page_width, page_height = A4

    pdf.setTitle(
        f"Flying Fox Ticket {ticket.ticket_id}"
    )

    # Heading
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(
        55,
        page_height - 70,
        "FLYING FOX ADVENTURE",
    )

    pdf.setFont("Helvetica", 12)
    pdf.drawString(
        55,
        page_height - 95,
        "Munnar, Kerala",
    )

    # Divider
    pdf.line(
        55,
        page_height - 115,
        page_width - 55,
        page_height - 115,
    )

    y_position = page_height - 155

    ticket_rows = [
        ("Ticket ID", str(ticket.ticket_id)),
        ("Booking ID", str(booking.booking_id)),
        ("Customer", booking.customer_name),
        ("Email", booking.customer_email),
        ("Phone", booking.customer_phone),
        ("Ride", booking.ride.name),
        (
            "Visit Date",
            booking.booking_date.strftime("%d %B %Y"),
        ),
        ("Time Slot", booking.time_slot),
        ("Participants", str(booking.quantity)),
        (
            "Price Per Person",
            f"INR {booking.price_per_person}",
        ),
        (
            "Total Paid",
            f"INR {booking.total_amount}",
        ),
        ("Booking Status", booking.get_status_display()),
    ]

    for label, value in ticket_rows:
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(
            55,
            y_position,
            f"{label}:",
        )

        pdf.setFont("Helvetica", 11)
        pdf.drawString(
            180,
            y_position,
            str(value),
        )

        y_position -= 25

    # Participant details
    y_position -= 10

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(
        55,
        y_position,
        "Participants",
    )

    y_position -= 25

    for index, participant in enumerate(
        booking.participants.all(),
        start=1,
    ):
        participant_text = (
            f"{index}. {participant.full_name} | "
            f"Age: {participant.age or '-'} | "
            f"Weight: {participant.weight or '-'} kg"
        )

        pdf.setFont("Helvetica", 10)
        pdf.drawString(
            65,
            y_position,
            participant_text,
        )

        y_position -= 20

    # QR image
    if ticket.qr_image:
        try:
            pdf.drawImage(
                ticket.qr_image.path,
                page_width - 210,
                90,
                width=145,
                height=145,
                preserveAspectRatio=True,
                mask="auto",
            )
        except (OSError, ValueError):
            pass

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(
        55,
        150,
        "Important:",
    )

    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        55,
        132,
        "Show this QR ticket at the Flying Fox counter.",
    )

    pdf.drawString(
        55,
        116,
        "Please arrive at least 30 minutes before your time slot.",
    )

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    ticket.pdf_ticket.save(
        f"ticket-{ticket.ticket_id}.pdf",
        ContentFile(buffer.getvalue()),
        save=False,
    )



def send_ticket_email(ticket):
    """
    Send booking confirmation and the PDF ticket
    to the customer's email address.

    Returns True when Django successfully submits
    the email to the SMTP server.
    """

    booking = ticket.booking

    # -----------------------------------------
    # 1. Validate customer email
    # -----------------------------------------

    if not booking.customer_email:
        print(
            "EMAIL ERROR: Customer email is empty."
        )
        return False

    # -----------------------------------------
    # 2. Validate email settings
    # -----------------------------------------

    if not settings.EMAIL_HOST_USER:
        print(
            "EMAIL ERROR: EMAIL_HOST_USER "
            "is not configured."
        )
        return False

    if not settings.EMAIL_HOST_PASSWORD:
        print(
            "EMAIL ERROR: EMAIL_HOST_PASSWORD "
            "is not configured."
        )
        return False

    # -----------------------------------------
    # 3. Customer-friendly IDs
    # -----------------------------------------

    short_booking_id = str(
        booking.booking_id
    ).split("-")[0].upper()

    short_ticket_id = str(
        ticket.ticket_id
    ).split("-")[0].upper()

    # -----------------------------------------
    # 4. Prepare email content
    # -----------------------------------------

    subject = (
        f"Flying Fox Booking Confirmed - "
        f"{short_booking_id}"
    )

    body = (
        f"Hello {booking.customer_name},\n\n"

        "Your Flying Fox Adventure booking "
        "has been confirmed successfully.\n\n"

        "BOOKING DETAILS\n"
        "--------------------------------\n"

        f"Booking ID: {short_booking_id}\n"
        f"Ticket ID: {short_ticket_id}\n"
        f"Ride: {booking.ride.name}\n"
        f"Visit Date: "
        f"{booking.booking_date.strftime('%d %B %Y')}\n"
        f"Time Slot: {booking.time_slot}\n"
        f"Participants: {booking.quantity}\n"
        f"Amount Paid: INR {booking.total_amount}\n\n"

        "Your PDF ticket is attached to this email.\n\n"

        "Please arrive at least 30 minutes before "
        "your selected time slot and show the QR "
        "ticket at the Flying Fox counter.\n\n"

        "Thank you for choosing Flying Fox Adventure.\n\n"

        "Regards,\n"
        "Flying Fox Adventure\n"
        "Munnar, Kerala"
    )

    # -----------------------------------------
    # 5. Create email
    # -----------------------------------------

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[
            booking.customer_email,
        ],
    )

    # -----------------------------------------
    # 6. Attach generated PDF ticket
    # -----------------------------------------

    if ticket.pdf_ticket:

        try:
            ticket.pdf_ticket.open("rb")

            pdf_content = (
                ticket.pdf_ticket.read()
            )

            ticket.pdf_ticket.close()

            email.attach(
                (
                    f"flying-fox-ticket-"
                    f"{short_ticket_id}.pdf"
                ),
                pdf_content,
                "application/pdf",
            )

        except (
            FileNotFoundError,
            OSError,
            ValueError,
        ) as error:

            print(
                "EMAIL PDF ATTACHMENT ERROR:",
                error,
            )

            return False

    else:
        print(
            "EMAIL ERROR: PDF ticket is missing."
        )
        return False

    # -----------------------------------------
    # 7. Send email
    # -----------------------------------------

    try:
        sent_count = email.send(
            fail_silently=False
        )

        if sent_count == 1:

            print(
                "\n========== TICKET EMAIL SENT =========="
            )
            print(
                "TO:",
                booking.customer_email,
            )
            print(
                "BOOKING ID:",
                booking.booking_id,
            )
            print(
                "TICKET ID:",
                ticket.ticket_id,
            )
            print(
                "=======================================\n"
            )

            return True

        print(
            "EMAIL ERROR: Email backend returned:",
            sent_count,
        )

        return False

    except Exception as error:

        print(
            "\n========== TICKET EMAIL FAILED =========="
        )
        print(
            "TO:",
            booking.customer_email,
        )
        print(
            "ERROR TYPE:",
            type(error).__name__,
        )
        print(
            "ERROR:",
            error,
        )
        print(
            "=========================================\n"
        )

        return False



# def send_ticket_sms(ticket):
#     """
#     Send booking and ticket information by SMS.

#     Returns True when the SMS provider accepts
#     the message request. Returns False on failure.
#     """

#     booking = ticket.booking

#     # -----------------------------------------
#     # 1. Check customer phone
#     # -----------------------------------------

#     if not booking.customer_phone:
#         print("SMS ERROR: Customer phone is empty.")
#         return False

#     # -----------------------------------------
#     # 2. Check Twilio settings
#     # -----------------------------------------

#     if not settings.TWILIO_ACCOUNT_SID:
#         print(
#             "SMS ERROR: TWILIO_ACCOUNT_SID "
#             "is not configured."
#         )
#         return False

#     if not settings.TWILIO_AUTH_TOKEN:
#         print(
#             "SMS ERROR: TWILIO_AUTH_TOKEN "
#             "is not configured."
#         )
#         return False

#     if not settings.TWILIO_PHONE_NUMBER:
#         print(
#             "SMS ERROR: TWILIO_PHONE_NUMBER "
#             "is not configured."
#         )
#         return False

#     # -----------------------------------------
#     # 3. Clean customer phone number
#     # -----------------------------------------

#     phone = (
#         booking.customer_phone
#         .replace(" ", "")
#         .replace("-", "")
#         .replace("(", "")
#         .replace(")", "")
#     )

#     # Convert an Indian 10-digit number:
#     # 9876543210 -> +919876543210
#     if len(phone) == 10 and phone.isdigit():
#         phone = f"+91{phone}"

#     # Convert 91xxxxxxxxxx:
#     # 919876543210 -> +919876543210
#     elif (
#         len(phone) == 12
#         and phone.startswith("91")
#         and phone.isdigit()
#     ):
#         phone = f"+{phone}"

#     # Reject invalid numbers
#     elif not phone.startswith("+"):
#         print(
#             "SMS ERROR: Invalid phone number:",
#             phone,
#         )
#         return False

#     # -----------------------------------------
#     # 4. Create SMS content
#     # -----------------------------------------

#     message_body = (
#         "Flying Fox booking confirmed. "
#         f"Booking ID: {booking.booking_id}. "
#         f"Ticket ID: {ticket.ticket_id}. "
#         f"Ride: {booking.ride.name}. "
#         f"Date: "
#         f"{booking.booking_date.strftime('%d-%m-%Y')}. "
#         f"Time: {booking.time_slot}. "
#         "Please show your QR ticket at the venue."
#     )

#     # -----------------------------------------
#     # 5. Send SMS using Twilio
#     # -----------------------------------------

#     try:
#         client = Client(
#             settings.TWILIO_ACCOUNT_SID,
#             settings.TWILIO_AUTH_TOKEN,
#         )

#         message = client.messages.create(
#             body=message_body,
#             from_=settings.TWILIO_PHONE_NUMBER,
#             to=phone,
#         )

#         print("\n========== SMS REQUEST ACCEPTED ==========")
#         print("TO:", phone)
#         print("MESSAGE SID:", message.sid)
#         print("INITIAL STATUS:", message.status)
#         print("==========================================\n")

#         return True

#     except TwilioRestException as error:
#         print("\n============ TWILIO SMS FAILED ============")
#         print("TO:", phone)
#         print("ERROR CODE:", error.code)
#         print("ERROR MESSAGE:", error.msg)
#         print("===========================================\n")

#         return False

#     except Exception as error:
#         print("\n========== UNEXPECTED SMS ERROR ==========")
#         print("TO:", phone)
#         print("ERROR:", error)
#         print("==========================================\n")

#         return False
    

def send_ticket_sms(ticket):
    """
    Send Twilio's predefined trial order-confirmation SMS.

    Important:
    This does not send the actual Booking ID or Ticket ID.
    It sends Twilio's fixed trial confirmation template.
    """

    booking = ticket.booking

    # -----------------------------------------
    # 1. Validate customer phone
    # -----------------------------------------

    if not booking.customer_phone:
        print("SMS ERROR: Customer phone is empty.")
        return False

    # -----------------------------------------
    # 2. Read Twilio settings
    # -----------------------------------------

    account_sid = getattr(
        settings,
        "TWILIO_ACCOUNT_SID",
        "",
    )

    auth_token = getattr(
        settings,
        "TWILIO_AUTH_TOKEN",
        "",
    )

    twilio_number = getattr(
        settings,
        "TWILIO_PHONE_NUMBER",
        "",
    )

    if not account_sid:
        print(
            "SMS ERROR: TWILIO_ACCOUNT_SID "
            "is not configured."
        )
        return False

    if not auth_token:
        print(
            "SMS ERROR: TWILIO_AUTH_TOKEN "
            "is not configured."
        )
        return False

    if not twilio_number:
        print(
            "SMS ERROR: TWILIO_PHONE_NUMBER "
            "is not configured."
        )
        return False

    # -----------------------------------------
    # 3. Format Indian phone number
    # -----------------------------------------

    phone = (
        booking.customer_phone
        .strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )

    # 9633390345 -> +919633390345
    if len(phone) == 10 and phone.isdigit():
        phone = f"+91{phone}"

    # 919633390345 -> +919633390345
    elif (
        len(phone) == 12
        and phone.startswith("91")
        and phone.isdigit()
    ):
        phone = f"+{phone}"

    # Already in +919633390345 format
    elif (
        len(phone) == 13
        and phone.startswith("+91")
        and phone[1:].isdigit()
    ):
        pass

    else:
        print(
            "SMS ERROR: Invalid customer phone number:",
            phone,
        )

        ticket.sms_sent = False
        ticket.sms_status = "invalid_number"

        ticket.save(
            update_fields=[
                "sms_sent",
                "sms_status",
            ]
        )

        return False

    # -----------------------------------------
    # 4. Send predefined Twilio trial template
    # -----------------------------------------

    try:
        client = Client(
            account_sid,
            auth_token,
        )

        message = client.messages.create(
            to=phone,
            from_=twilio_number,

            # Twilio trial predefined template
            body="sms_order_confirmation",
        )

        ticket.sms_sent = True
        ticket.sms_message_id = message.sid
        ticket.sms_status = (
            message.status or "queued"
        )

        ticket.save(
            update_fields=[
                "sms_sent",
                "sms_message_id",
                "sms_status",
            ]
        )

        print(
            "\n========== SMS REQUEST ACCEPTED =========="
        )
        print("TO:", phone)
        print("FROM:", twilio_number)
        print("MESSAGE SID:", message.sid)
        print("INITIAL STATUS:", message.status)
        print(
            "==========================================\n"
        )

        return True

    except TwilioRestException as error:

        ticket.sms_sent = False
        ticket.sms_status = "failed"

        ticket.save(
            update_fields=[
                "sms_sent",
                "sms_status",
            ]
        )

        print(
            "\n============ TWILIO SMS FAILED ============"
        )
        print("TO:", phone)
        print("ERROR CODE:", error.code)
        print("ERROR MESSAGE:", error.msg)
        print(
            "===========================================\n"
        )

        return False

    except Exception as error:

        ticket.sms_sent = False
        ticket.sms_status = "error"

        ticket.save(
            update_fields=[
                "sms_sent",
                "sms_status",
            ]
        )

        print(
            "\n========== UNEXPECTED SMS ERROR =========="
        )
        print("TO:", phone)
        print("ERROR:", error)
        print(
            "==========================================\n"
        )

        return False





def send_ticket_whatsapp(request, ticket):
    """
    Send Twilio's predefined WhatsApp trial template.

    This currently sends only the predefined trial
    confirmation message. It does not send dynamic
    booking details or the QR/PDF ticket yet.

    Returns True when Twilio accepts the request.
    Returns False when sending fails.
    """

    booking = ticket.booking

    # ==========================================
    # 1. Validate customer phone number
    # ==========================================

    if not booking.customer_phone:
        print(
            "WHATSAPP ERROR: Customer phone is empty."
        )
        return False

    # ==========================================
    # 2. Read Twilio configuration
    # ==========================================

    account_sid = getattr(
        settings,
        "TWILIO_ACCOUNT_SID",
        "",
    )

    auth_token = getattr(
        settings,
        "TWILIO_AUTH_TOKEN",
        "",
    )

    whatsapp_from = getattr(
        settings,
        "TWILIO_WHATSAPP_FROM",
        "",
    )

    content_sid = getattr(
        settings,
        "TWILIO_WHATSAPP_CONTENT_SID",
        "",
    )

    if not account_sid:
        print(
            "WHATSAPP ERROR: TWILIO_ACCOUNT_SID "
            "is missing."
        )
        return False

    if not auth_token:
        print(
            "WHATSAPP ERROR: TWILIO_AUTH_TOKEN "
            "is missing."
        )
        return False

    if not whatsapp_from:
        print(
            "WHATSAPP ERROR: TWILIO_WHATSAPP_FROM "
            "is missing."
        )
        return False

    if not content_sid:
        print(
            "WHATSAPP ERROR: "
            "TWILIO_WHATSAPP_CONTENT_SID "
            "is missing."
        )
        return False

    # ==========================================
    # 3. Format the recipient phone number
    # ==========================================

    phone = (
        booking.customer_phone
        .strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )

    # 9633390345 -> +919633390345
    if len(phone) == 10 and phone.isdigit():
        phone = f"+91{phone}"

    # 919633390345 -> +919633390345
    elif (
        len(phone) == 12
        and phone.startswith("91")
        and phone.isdigit()
    ):
        phone = f"+{phone}"

    # Already +919633390345
    elif (
        len(phone) == 13
        and phone.startswith("+91")
        and phone[1:].isdigit()
    ):
        pass

    else:
        print(
            "WHATSAPP ERROR: Invalid phone number:",
            phone,
        )

        return False

    whatsapp_to = f"whatsapp:{phone}"

    # ==========================================
    # 4. Send Twilio predefined content template
    # ==========================================

    try:
        client = Client(
            account_sid,
            auth_token,
        )

        message = client.messages.create(
            to=whatsapp_to,
            from_=whatsapp_from,
            content_sid=content_sid,
        )

        print(
            "\n====== WHATSAPP REQUEST ACCEPTED ======"
        )
        print("TO:", whatsapp_to)
        print("FROM:", whatsapp_from)
        print("CONTENT SID:", content_sid)
        print("MESSAGE SID:", message.sid)
        print("INITIAL STATUS:", message.status)
        print(
            "========================================\n"
        )

        return True

    except TwilioRestException as error:

         print(
        "\n========== WHATSAPP FAILED =========="
    )
         print("TO:", whatsapp_to)
         print("FROM:", whatsapp_from)
         print(
        "ERROR CODE:",
        getattr(error, "code", ""),
    )
         print(
        "ERROR MESSAGE:",
        getattr(error, "msg", str(error)),
    )
         print(
        "ERROR STATUS:",
        getattr(error, "status", ""),
    )
         print(
        "=======================================\n"
    )

         return False

    except Exception as error:

        print(
            "\n===== UNEXPECTED WHATSAPP ERROR ====="
        )
        print("TO:", whatsapp_to)
        print("ERROR TYPE:", type(error).__name__)
        print("ERROR:", error)
        print(
            "======================================\n"
        )

        return False

@require_POST
@transaction.atomic
def temporary_payment_success(request):
    """
    Temporary development-only payment success.

    This creates a paid booking without contacting
    a real payment gateway.
    """

    if not settings.DEBUG:
        raise Http404(
            "Temporary payment is disabled."
        )

    booking_data = request.session.get(
        "pending_booking"
    )

    if not booking_data:
        messages.error(
            request,
            "Your booking session has expired. Please start again.",
        )
        return redirect("bookings")

    customer_name = request.POST.get(
        "customer_name",
        "",
    ).strip()

    customer_email = request.POST.get(
        "customer_email",
        "",
    ).strip()

    customer_phone = request.POST.get(
        "customer_phone",
        "",
    ).strip()

    customer_pincode = request.POST.get(
        "customer_pincode",
        "",
    ).strip()

    terms_accepted = (
        request.POST.get("terms_accepted") == "1"
    )

    if not customer_name:
        messages.error(
            request,
            "Please enter your full name.",
        )
        return redirect("booking_review")

    if not customer_email:
        messages.error(
            request,
            "Please enter your email address.",
        )
        return redirect("booking_review")

    if (
        not customer_phone.isdigit()
        or len(customer_phone) != 10
    ):
        messages.error(
            request,
            "Please enter a valid 10-digit mobile number.",
        )
        return redirect("booking_review")

    if (
        not customer_pincode.isdigit()
        or len(customer_pincode) != 6
    ):
        messages.error(
            request,
            "Please enter a valid 6-digit PIN code.",
        )
        return redirect("booking_review")

    if not terms_accepted:
        messages.error(
            request,
            "Please accept the terms and conditions.",
        )
        return redirect("booking_review")

    booking_date = parse_date(
        booking_data.get(
            "booking_date",
            "",
        )
    )

    if not booking_date:
        messages.error(
            request,
            "The booking date is invalid.",
        )
        return redirect("bookings")

    ride = get_object_or_404(
        Ride,
        id=booking_data["ride_id"],
        is_active=True,
    )

    # Re-fetch the valid price from the database.
    ride_price = (
        RidePrice.objects
        .filter(
            ride=ride,
            is_active=True,
            start_date__lte=booking_date,
            end_date__gte=booking_date,
        )
        .order_by(
            "-start_date",
            "-created_at",
        )
        .first()
    )

    if not ride_price:
        messages.error(
            request,
            "No active price exists for the selected date.",
        )
        return redirect("bookings")

    participants = booking_data.get(
        "participants",
        [],
    )

    if not participants:
        messages.error(
            request,
            "No participants were found.",
        )
        return redirect("bookings")

    quantity = len(participants)

    price_per_person = ride_price.price

    participant_subtotal = (
        price_per_person * quantity
    )

    photo_addon = bool(
        booking_data.get("photo_addon")
    )

    video_addon = bool(
        booking_data.get("video_addon")
    )

    addon_amount = Decimal(
        booking_data.get(
            "addon_total",
            "0",
        )
    )

    subtotal = (
        participant_subtotal
        + addon_amount
    )

    discount_amount = Decimal(
        booking_data.get(
            "discount_amount",
            "0",
        )
    )

    if discount_amount > subtotal:
        discount_amount = subtotal

    total_amount = (
        subtotal - discount_amount
    )

    coupon = None

    coupon_id = booking_data.get(
        "coupon_id"
    )

    if coupon_id:
        coupon = (
            Coupon.objects
            .filter(
                id=coupon_id,
                is_active=True,
            )
            .first()
        )

    booking = Booking.objects.create(
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        customer_pincode=customer_pincode,

        ride=ride,
        ride_price=ride_price,

        booking_date=booking_date,
        time_slot=booking_data.get(
            "time_slot",
            "",
        ),

        quantity=quantity,
        price_per_person=price_per_person,

        photo_addon=photo_addon,
        video_addon=video_addon,
        addon_amount=addon_amount,

        coupon=coupon,
        discount_amount=discount_amount,
        subtotal=subtotal,
        total_amount=total_amount,

        status="confirmed",
    )

    for participant in participants:
        BookingPerson.objects.create(
            booking=booking,
            full_name=participant.get(
                "full_name",
                "",
            ),
            age=participant.get("age"),
            weight=participant.get("weight"),
            phone=participant.get(
                "phone",
                "",
            ),
        )

    # Temporary paid payment record
    Payment.objects.create(
        booking=booking,
        gateway="temporary",
        gateway_order_id=(
            f"TEMP-ORDER-{booking.booking_id}"
        ),
        gateway_payment_id=(
            f"TEMP-PAYMENT-{booking.booking_id}"
        ),
        amount=total_amount,
        status="paid",
        paid_at=timezone.now(),
    )

    ticket = Ticket.objects.create(
        booking=booking
    )

    generate_ticket_qr(
        request,
        ticket,
    )

    # Save QR before PDF generation so that the PDF
    # can include the stored QR image.
    ticket.save()

    generate_ticket_pdf(ticket)

    ticket.save()

    email_sent = send_ticket_email(ticket)
    sms_sent = send_ticket_sms(ticket)
    whatsapp_sent = send_ticket_whatsapp(
        request,
        ticket,
    )

    ticket.email_sent = email_sent
    ticket.whatsapp_sent = whatsapp_sent

    ticket.save(
        update_fields=[
            "email_sent",
            "whatsapp_sent",
        ]
    )

    booking.notifications_sent = (
        email_sent
        and sms_sent
        and whatsapp_sent
    )

    booking.save(
        update_fields=[
            "notifications_sent",
            "updated_at",
        ]
    )

    request.session.pop(
        "pending_booking",
        None,
    )

    request.session[
        "show_ticket_modal"
    ] = True

    return redirect(
        "booking_success",
        booking_id=booking.booking_id,
    )



def booking_success(request, booking_id):
    booking = get_object_or_404(
        Booking.objects
        .select_related(
            "ride",
            "ride_price",
            "payment",
            "ticket",
        )
        .prefetch_related(
            "participants"
        ),
        booking_id=booking_id,
        status="confirmed",
    )

    show_ticket_modal = request.session.pop(
        "show_ticket_modal",
        False,
    )

    return render(
        request,
        "frontend/booking_success.html",
        {
            "booking": booking,
            "ticket": booking.ticket,
            "show_ticket_modal": show_ticket_modal,
        },
    )




def download_ticket(request, ticket_id):
    ticket = get_object_or_404(
        Ticket.objects.select_related(
            "booking"
        ),
        ticket_id=ticket_id,
    )

    if not ticket.pdf_ticket:
        raise Http404(
            "Ticket PDF is not available."
        )

    try:
        file_handle = ticket.pdf_ticket.open(
            "rb"
        )
    except (FileNotFoundError, OSError):
        raise Http404(
            "Ticket PDF file was not found."
        )

    return FileResponse(
        file_handle,
        as_attachment=True,
        filename=(
            f"flying-fox-ticket-"
            f"{ticket.ticket_id}.pdf"
        ),
        content_type="application/pdf",
    )



def verify_ticket(request, qr_token):
    ticket = get_object_or_404(
        Ticket.objects
        .select_related(
            "booking",
            "booking__ride",
            "booking__payment",
        )
        .prefetch_related(
            "booking__participants"
        ),
        qr_token=qr_token,
    )

    return render(
        request,
        "frontend/ticket_verify.html",
        {
            "ticket": ticket,
            "booking": ticket.booking,
        },
    )











# ==========================================
# STATIC FRONTEND PAGES
# ==========================================

def about(request):
    return render(request, "frontend/about.html")


def activity(request):
    return render(request, "frontend/activity.html")


def activity_single(request):
    return render(request, "frontend/activity-single.html")

def blog(request):

    blogs_queryset = (
        Blog.objects
        .all()
        .order_by("-created_at")
    )

    paginator = Paginator(
        blogs_queryset,
        6,
    )

    blogs = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "frontend/blogs.html",
        {
            "blogs": blogs,
        },
    )


def blog_single(request):
    return render(request, "frontend/blog-single.html")


def contact(request):
    return render(request, "frontend/contact.html")


def destination(request):
    return render(request, "frontend/destination.html")


def destination_single(request):
    return render(request, "frontend/destination-single.html")


def destination_two(request):
    return render(request, "frontend/destination-2.html")


def faq(request):
    return render(request, "frontend/faq.html")


def gallery(request):

    gallery_queryset = (
        GalleryItem.objects
        .select_related("category")
        .order_by("-uploaded_at")
    )

    paginator = Paginator(
        gallery_queryset,
        12,
    )

    gallery_items = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "frontend/gallery.html",
        {
            "gallery_items": gallery_items,
        },
    )


def login_page(request):
    return render(request, "frontend/login.html")


def register(request):
    return render(request, "frontend/register.html")


def team(request):
    return render(request, "frontend/team.html")


def privacy(request):
    return render(request, "frontend/privacy.html")


def terms(request):
    return render(request, "frontend/terms.html")


def testimonial(request):
    return render(request, "frontend/testimonial.html")


def tour_two(request):
    return render(request, "frontend/tour-2.html")


def tour_three(request):
    return render(request, "frontend/tour-3.html")


def forgot_password(request):
    return render(request, "frontend/forgot-password.html")


def coming_soon(request):
    return render(request, "frontend/coming-soon.html")


def page_404(request):
    return render(request, "frontend/404.html")






# chatbot rule management views for admin panel

@_admin_required
def chatbot_rule_list(request):

    rules = ChatbotRule.objects.all().order_by(
        "-priority",
        "title",
    )

    paginator = Paginator(
        rules,
        10,
    )

    page = request.GET.get("page")

    rules = paginator.get_page(page)

    return render(
        request,
        "admin_pages/chatbot_rule_list.html",
        {
            "rules": rules,
        },
    )


@_admin_required
def chatbot_rule_create(request):

    if request.method == "POST":

        ChatbotRule.objects.create(

            title=request.POST.get("title"),

            keywords=json.loads(
                request.POST.get("keywords")
            ),

            response=request.POST.get("response"),

            action_text=request.POST.get(
                "action_text",
            ),

            action_url=request.POST.get(
                "action_url",
            ),

            priority=request.POST.get(
                "priority",
                10,
            ),

            is_active="is_active" in request.POST,
        )

        messages.success(
            request,
            "Rule created successfully.",
        )

        return redirect(
            "chatbot_rule_list"
        )

    return render(
        request,
        "admin_pages/chatbot_rule_form.html",
    )


@_admin_required
def chatbot_rule_update(request, pk):

    rule = get_object_or_404(
        ChatbotRule,
        pk=pk,
    )

    if request.method == "POST":

        title = request.POST.get(
            "title",
            "",
        ).strip()

        keywords_raw = request.POST.get(
            "keywords",
            "",
        ).strip()

        response = request.POST.get(
            "response",
            "",
        ).strip()

        action_text = request.POST.get(
            "action_text",
            "",
        ).strip()

        action_url = request.POST.get(
            "action_url",
            "",
        ).strip()

        priority_raw = request.POST.get(
            "priority",
            "10",
        ).strip()

        is_active = (
            "is_active" in request.POST
        )

        form_data = {
            "title": title,
            "keywords": keywords_raw,
            "response": response,
            "action_text": action_text,
            "action_url": action_url,
            "priority": priority_raw,
            "is_active": is_active,
        }

        # --------------------------------------
        # Validate title
        # --------------------------------------

        if not title:

            messages.error(
                request,
                "Rule title is required.",
            )

            return render(
                request,
                "admin_pages/chatbot_rule_form.html",
                {
                    "rule": rule,
                    "form_data": form_data,
                    "keywords_json": keywords_raw,
                },
            )

        # --------------------------------------
        # Validate keywords
        # --------------------------------------

        if not keywords_raw:

            messages.error(
                request,
                "Keywords are required.",
            )

            return render(
                request,
                "admin_pages/chatbot_rule_form.html",
                {
                    "rule": rule,
                    "form_data": form_data,
                    "keywords_json": keywords_raw,
                },
            )

        try:

            keywords = json.loads(
                keywords_raw
            )

        except json.JSONDecodeError:

            messages.error(
                request,
                (
                    "Keywords must be valid JSON. "
                    'Example: ["hello", "hi"]'
                ),
            )

            return render(
                request,
                "admin_pages/chatbot_rule_form.html",
                {
                    "rule": rule,
                    "form_data": form_data,
                    "keywords_json": keywords_raw,
                },
            )

        if (
            not isinstance(keywords, list)
            or not all(
                isinstance(keyword, str)
                for keyword in keywords
            )
        ):

            messages.error(
                request,
                "Keywords must be a JSON list of text values.",
            )

            return render(
                request,
                "admin_pages/chatbot_rule_form.html",
                {
                    "rule": rule,
                    "form_data": form_data,
                    "keywords_json": keywords_raw,
                },
            )

        keywords = [
            keyword.strip()
            for keyword in keywords
            if keyword.strip()
        ]

        if not keywords:

            messages.error(
                request,
                "Add at least one keyword.",
            )

            return render(
                request,
                "admin_pages/chatbot_rule_form.html",
                {
                    "rule": rule,
                    "form_data": form_data,
                    "keywords_json": keywords_raw,
                },
            )

        # --------------------------------------
        # Validate response
        # --------------------------------------

        if not response:

            messages.error(
                request,
                "Bot response is required.",
            )

            return render(
                request,
                "admin_pages/chatbot_rule_form.html",
                {
                    "rule": rule,
                    "form_data": form_data,
                    "keywords_json": keywords_raw,
                },
            )

        # --------------------------------------
        # Validate priority
        # --------------------------------------

        try:

            priority = int(
                priority_raw
            )

        except (
            TypeError,
            ValueError,
        ):

            priority = 10

        # --------------------------------------
        # Update rule
        # --------------------------------------

        rule.title = title
        rule.keywords = keywords
        rule.response = response
        rule.action_text = action_text
        rule.action_url = action_url
        rule.priority = max(
            priority,
            0,
        )
        rule.is_active = is_active

        rule.save()

        messages.success(
            request,
            "Chatbot rule updated successfully.",
        )

        return redirect(
            "chatbot_rule_list"
        )

    # ------------------------------------------
    # GET request: show existing database values
    # ------------------------------------------

    return render(
        request,
        "admin_pages/chatbot_rule_form.html",
        {
            "rule": rule,

            "keywords_json": json.dumps(
                rule.keywords,
                ensure_ascii=False,
            ),
        },
    )

@_admin_required
def chatbot_rule_delete(request, pk):

    rule = get_object_or_404(
        ChatbotRule,
        pk=pk,
    )

    if request.method == "POST":

        rule.delete()

        messages.success(
            request,
            "Rule deleted successfully.",
        )

    return redirect(
        "chatbot_rule_list"
    )


@_admin_required
def chatbot_rule_toggle_status(request, pk):

    rule = get_object_or_404(
        ChatbotRule,
        pk=pk,
    )

    if request.method == "POST":

        rule.is_active = not rule.is_active

        rule.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        messages.success(
            request,
            "Rule status updated successfully.",
        )

    return redirect(
        "chatbot_rule_list"
    )


def get_or_create_chat_session(request):

    if not request.session.session_key:
        request.session.create()

    browser_session_key = (
        request.session.session_key
    )

    chatbot_session_id = request.session.get(
        "chatbot_session_id"
    )

    if chatbot_session_id:

        chat_session = (
            ChatSession.objects
            .filter(
                session_id=chatbot_session_id,
                is_closed=False,
            )
            .first()
        )

        if chat_session:
            return chat_session

    chat_session = ChatSession.objects.create(
        browser_session_key=browser_session_key,
        onboarding_step="name",
    )

    request.session[
        "chatbot_session_id"
    ] = str(chat_session.session_id)

    request.session.modified = True

    return chat_session

def normalize_chatbot_text(value):
    value = str(value or "").lower().strip()

    value = re.sub(
        r"[^a-z0-9\s]",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value




def find_chatbot_rule(user_message):

    normalized_message = normalize_chatbot_text(
        user_message
    )

    rules = (
        ChatbotRule.objects
        .filter(is_active=True)
        .order_by(
            "-priority",
            "title",
        )
    )

    best_rule = None
    best_score = 0

    for rule in rules:

        score = 0

        for keyword in rule.keywords or []:

            normalized_keyword = (
                normalize_chatbot_text(
                    keyword
                )
            )

            if (
                normalized_keyword
                and normalized_keyword
                in normalized_message
            ):
                score += (
                    len(
                        normalized_keyword.split()
                    ) * 100
                    + len(normalized_keyword)
                )

        if score > best_score:
            best_score = score
            best_rule = rule

    return best_rule



def clean_indian_phone(phone):

    phone = (
        str(phone or "")
        .strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )

    if phone.startswith("+91"):
        phone = phone[3:]

    elif phone.startswith("91") and len(phone) == 12:
        phone = phone[2:]

    if (
        len(phone) != 10
        or not phone.isdigit()
    ):
        return None

    if phone[0] not in ["6", "7", "8", "9"]:
        return None

    return phone











@require_POST
def chatbot_message(request):

    # ==========================================
    # 1. READ JSON REQUEST
    # ==========================================

    try:
        payload = json.loads(
            request.body.decode("utf-8")
        )

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):
        return JsonResponse(
            {
                "success": False,
                "error": "Invalid request data.",
            },
            status=400,
        )

    user_message = payload.get(
        "message",
        "",
    ).strip()

    if not user_message:
        return JsonResponse(
            {
                "success": False,
                "error": "Please enter a message.",
            },
            status=400,
        )

    if len(user_message) > 1000:
        return JsonResponse(
            {
                "success": False,
                "error": "Your message is too long.",
            },
            status=400,
        )

    # ==========================================
    # 2. GET OR CREATE CHAT SESSION
    # ==========================================

    chat_session = get_or_create_chat_session(
        request
    )

    # Store visitor message.
    ChatMessage.objects.create(
        session=chat_session,
        sender="user",
        message=user_message,
    )

    # ==========================================
    # 3. ONBOARDING: FULL NAME
    # ==========================================

    if chat_session.onboarding_step == "name":

        full_name = user_message.strip()

        if len(full_name) < 2:

            bot_response = (
                "Please enter your complete name."
            )

            ChatMessage.objects.create(
                session=chat_session,
                sender="bot",
                message=bot_response,
                intent="collect_name",
            )

            return JsonResponse(
                {
                    "success": True,
                    "response": bot_response,
                    "response_type": "text",
                    "onboarding_step": "name",
                    "show_quick_replies": False,
                }
            )

        if not re.fullmatch(
            r"[A-Za-zÀ-ÿ.'\-\s]+",
            full_name,
        ):

            bot_response = (
                "Please enter a valid name using "
                "letters only."
            )

            ChatMessage.objects.create(
                session=chat_session,
                sender="bot",
                message=bot_response,
                intent="collect_name",
            )

            return JsonResponse(
                {
                    "success": True,
                    "response": bot_response,
                    "response_type": "text",
                    "onboarding_step": "name",
                    "show_quick_replies": False,
                }
            )

        chat_session.customer_name = full_name
        chat_session.onboarding_step = "phone"

        chat_session.save(
            update_fields=[
                "customer_name",
                "onboarding_step",
                "updated_at",
            ]
        )

        bot_response = (
            f"Nice to meet you, {full_name}! "
            "Please enter your 10-digit mobile number."
        )

        ChatMessage.objects.create(
            session=chat_session,
            sender="bot",
            message=bot_response,
            intent="collect_phone",
        )

        return JsonResponse(
            {
                "success": True,
                "response": bot_response,
                "response_type": "text",
                "onboarding_step": "phone",
                "show_quick_replies": False,
            }
        )

    # ==========================================
    # 4. ONBOARDING: PHONE NUMBER
    # ==========================================

    if chat_session.onboarding_step == "phone":

        phone = clean_indian_phone(
            user_message
        )

        if not phone:

            bot_response = (
                "Please enter a valid 10-digit "
                "Indian mobile number."
            )

            ChatMessage.objects.create(
                session=chat_session,
                sender="bot",
                message=bot_response,
                intent="collect_phone",
            )

            return JsonResponse(
                {
                    "success": True,
                    "response": bot_response,
                    "response_type": "text",
                    "onboarding_step": "phone",
                    "show_quick_replies": False,
                }
            )

        chat_session.customer_phone = phone
        chat_session.onboarding_step = "email"

        chat_session.save(
            update_fields=[
                "customer_phone",
                "onboarding_step",
                "updated_at",
            ]
        )

        bot_response = (
            "Thank you. Please enter your email "
            "address, or type Skip if you do not "
            "want to provide one."
        )

        ChatMessage.objects.create(
            session=chat_session,
            sender="bot",
            message=bot_response,
            intent="collect_email",
        )

        return JsonResponse(
            {
                "success": True,
                "response": bot_response,
                "response_type": "text",
                "onboarding_step": "email",
                "show_quick_replies": False,
            }
        )

    # ==========================================
    # 5. ONBOARDING: EMAIL
    # ==========================================

    if chat_session.onboarding_step == "email":

        submitted_email = user_message.strip()

        normalized_email_message = (
            submitted_email.lower()
        )

        skip_values = [
            "skip",
            "no",
            "not now",
            "later",
        ]

        if normalized_email_message in skip_values:

            chat_session.customer_email = ""

        else:

            try:
                validate_email(
                    submitted_email
                )

            except ValidationError:

                bot_response = (
                    "Please enter a valid email "
                    "address, or type Skip."
                )

                ChatMessage.objects.create(
                    session=chat_session,
                    sender="bot",
                    message=bot_response,
                    intent="collect_email",
                )

                return JsonResponse(
                    {
                        "success": True,
                        "response": bot_response,
                        "response_type": "text",
                        "onboarding_step": "email",
                        "show_quick_replies": False,
                    }
                )

            chat_session.customer_email = (
                submitted_email
            )

        chat_session.onboarding_step = "completed"

        chat_session.save(
            update_fields=[
                "customer_email",
                "onboarding_step",
                "updated_at",
            ]
        )

        bot_response = (
            f"Thank you, "
            f"{chat_session.customer_name}! "
            "How can I help you today? "
            "You can ask about rides, prices, "
            "booking, safety, payment or tickets."
        )

        ChatMessage.objects.create(
            session=chat_session,
            sender="bot",
            message=bot_response,
            intent="onboarding_completed",
        )

        return JsonResponse(
            {
                "success": True,
                "response": bot_response,
                "response_type": "menu",
                "onboarding_step": "completed",
                "show_quick_replies": True,
                "session_id": str(
                    chat_session.session_id
                ),
            }
        )

    # ==========================================
    # 6. NORMAL CHATBOT QUESTIONS
    # ==========================================

    normalized_message = normalize_chatbot_text(
        user_message
    )

    # ==========================================
    # 7. CREATE ENQUIRY
    # ==========================================

    enquiry_phrases = [
        "contact team",
        "contact me",
        "call me",
        "talk to agent",
        "human agent",
        "send enquiry",
        "submit enquiry",
        "need help",
    ]

    wants_enquiry = any(
        phrase in normalized_message
        for phrase in enquiry_phrases
    )

    if wants_enquiry:

        enquiry = ChatEnquiry.objects.create(
            session=chat_session,
            name=chat_session.customer_name,
            phone=chat_session.customer_phone,
            email=chat_session.customer_email,
            message=user_message,
            status="new",
        )

        bot_response = (
            "Your enquiry has been submitted "
            "successfully. Our team will contact "
            "you shortly."
        )

        ChatMessage.objects.create(
            session=chat_session,
            sender="bot",
            message=bot_response,
            intent="enquiry_created",
        )

        return JsonResponse(
            {
                "success": True,
                "response": bot_response,
                "response_type": "text",
                "enquiry_created": True,
                "enquiry_id": enquiry.id,
                "show_quick_replies": True,
                "session_id": str(
                    chat_session.session_id
                ),
            }
        )

    # ==========================================
    # 8. SHOW CURRENT ACTIVE RIDE PRICES
    # ==========================================

    ride_price_keywords = [
        "price",
        "prices",
        "ride price",
        "ride prices",
        "show ride prices",
        "cost",
        "charges",
        "rate",
    ]

    wants_ride_prices = any(
        keyword in normalized_message
        for keyword in ride_price_keywords
    )

    if wants_ride_prices:

        today = date.today()

        active_prices = (
            RidePrice.objects
            .filter(
                is_active=True,
                ride__is_active=True,
                start_date__lte=today,
                end_date__gte=today,
            )
            .select_related("ride")
            .order_by(
                "ride__name",
                "-start_date",
                "-created_at",
            )
        )

        # Keep only one current price per ride.
        latest_prices = {}

        for ride_price in active_prices:

            if (
                ride_price.ride_id
                not in latest_prices
            ):
                latest_prices[
                    ride_price.ride_id
                ] = ride_price

        if latest_prices:

            response_lines = [
                "Current active ride prices:",
                "",
            ]

            for ride_price in latest_prices.values():

                formatted_price = (
                    f"{ride_price.price:,.2f}"
                )

                response_lines.append(
                    f"• {ride_price.ride.name} "
                    f"- ₹{formatted_price} per person"
                )

            bot_response = "\n".join(
                response_lines
            )

            action = {
                "text": "Book Your Adventure",
                "url": "/bookings/",
            }

        else:

            bot_response = (
                "Currently, no active ride prices "
                "are available for today."
            )

            action = None

        ChatMessage.objects.create(
            session=chat_session,
            sender="bot",
            message=bot_response,
            intent="ride_prices",
        )

        return JsonResponse(
            {
                "success": True,
                "response": bot_response,
                "response_type": "text",
                "action": action,
                "show_quick_replies": True,
                "session_id": str(
                    chat_session.session_id
                ),
            }
        )

    # ==========================================
    # 9. FIND STATIC CHATBOT RULE
    # ==========================================

    matched_rule = find_chatbot_rule(
        user_message
    )

    if matched_rule:

        bot_response = (
            matched_rule.response
        )

        intent = matched_rule.title
        action = None

        if (
            matched_rule.action_text
            and matched_rule.action_url
        ):
            action = {
                "text": (
                    matched_rule.action_text
                ),
                "url": (
                    matched_rule.action_url
                ),
            }

    else:

        bot_response = (
            "Sorry, I could not understand that "
            "question. Please choose one of the "
            "options below or ask about booking, "
            "ride prices, safety, payment or tickets."
        )

        intent = "fallback"
        action = None

    # ==========================================
    # 10. STORE BOT RESPONSE
    # ==========================================

    ChatMessage.objects.create(
        session=chat_session,
        sender="bot",
        message=bot_response,
        intent=intent,
        matched_rule=matched_rule,
    )

    return JsonResponse(
        {
            "success": True,
            "response": bot_response,
            "response_type": "text",
            "session_id": str(
                chat_session.session_id
            ),
            "action": action,
            "show_quick_replies": True,
        }
    )


def chatbot_initialize(request):

    chat_session = get_or_create_chat_session(
        request
    )

    if chat_session.onboarding_step == "name":

        response = (
            "Welcome to Flying Fox Adventure! "
            "Before we begin, may I know your "
            "full name?"
        )

    elif chat_session.onboarding_step == "phone":

        response = (
            f"Hello {chat_session.customer_name}! "
            "Please enter your 10-digit mobile number."
        )

    elif chat_session.onboarding_step == "email":

        response = (
            "Please enter your email address, "
            "or type Skip."
        )

    else:

        response = (
            f"Welcome back, "
            f"{chat_session.customer_name}! "
            "How can I help you today?"
        )

    return JsonResponse(
        {
            "success": True,
            "response": response,
            "onboarding_step": (
                chat_session.onboarding_step
            ),
            "show_quick_replies": (
                chat_session.onboarding_step
                == "completed"
            ),
            "customer_name": (
                chat_session.customer_name
            ),
        }
    )




@_admin_required
def chat_session_list(request):

    search = request.GET.get(
        "search",
        "",
    ).strip()

    status = request.GET.get(
        "status",
        "",
    ).strip()

    sessions_qs = (
        ChatSession.objects
        .annotate(
            message_count=Count(
                "messages"
            )
        )
        .order_by("-updated_at")
    )

    if search:

        sessions_qs = sessions_qs.filter(
            Q(
                customer_name__icontains=search
            )
            | Q(
                customer_email__icontains=search
            )
            | Q(
                customer_phone__icontains=search
            )
            | Q(
                session_id__icontains=search
            )
        )

    if status == "open":

        sessions_qs = sessions_qs.filter(
            is_closed=False
        )

    elif status == "closed":

        sessions_qs = sessions_qs.filter(
            is_closed=True
        )

    paginator = Paginator(
        sessions_qs,
        10,
    )

    sessions = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "admin_pages/chat_session_list.html",
        {
            "sessions": sessions,
            "search": search,
            "selected_status": status,
        },
    )



@_admin_required
def chat_session_detail(request, pk):

    chat_session = get_object_or_404(
        ChatSession.objects.prefetch_related(
            "messages",
            "enquiries",
        ),
        pk=pk,
    )

    chat_messages = (
        chat_session.messages
        .select_related(
            "matched_rule"
        )
        .order_by("created_at")
    )

    enquiries = (
        chat_session.enquiries
        .order_by("-created_at")
    )

    return render(
        request,
        "admin_pages/chat_session_detail.html",
        {
            "chat_session": chat_session,
            "chat_messages": chat_messages,
            "enquiries": enquiries,
        },
    )



@_admin_required
@require_POST
def chat_session_toggle_status(
    request,
    pk,
):

    chat_session = get_object_or_404(
        ChatSession,
        pk=pk,
    )

    chat_session.is_closed = (
        not chat_session.is_closed
    )

    chat_session.save(
        update_fields=[
            "is_closed",
            "updated_at",
        ]
    )

    if chat_session.is_closed:

        message_text = (
            "Chat session closed successfully."
        )

    else:

        message_text = (
            "Chat session reopened successfully."
        )

    messages.success(
        request,
        message_text,
    )

    return redirect(
        "chat_session_detail",
        pk=chat_session.pk,
    )


@_admin_required
@require_POST
def chat_session_delete(
    request,
    pk,
):

    chat_session = get_object_or_404(
        ChatSession,
        pk=pk,
    )

    chat_session.delete()

    messages.success(
        request,
        "Chat session deleted successfully.",
    )

    return redirect(
        "chat_session_list"
    )




@_admin_required
def chat_enquiry_list(request):

    search = request.GET.get(
        "search",
        "",
    ).strip()

    status = request.GET.get(
        "status",
        "",
    ).strip()

    enquiries_qs = (
        ChatEnquiry.objects
        .select_related(
            "session"
        )
        .order_by("-created_at")
    )

    if search:

        enquiries_qs = enquiries_qs.filter(
            Q(name__icontains=search)
            | Q(phone__icontains=search)
            | Q(email__icontains=search)
            | Q(message__icontains=search)
        )

    if status:

        enquiries_qs = enquiries_qs.filter(
            status=status
        )

    paginator = Paginator(
        enquiries_qs,
        10,
    )

    enquiries = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "admin_pages/chat_enquiry_list.html",
        {
            "enquiries": enquiries,
            "search": search,
            "selected_status": status,
            "status_choices": (
                ChatEnquiry.STATUS_CHOICES
            ),
        },
    )



@_admin_required
def chat_enquiry_detail(
    request,
    pk,
):

    enquiry = get_object_or_404(
        ChatEnquiry.objects.select_related(
            "session"
        ),
        pk=pk,
    )

    conversation = []

    if enquiry.session_id:

        conversation = (
            enquiry.session.messages
            .select_related(
                "matched_rule"
            )
            .order_by("created_at")
        )

    return render(
        request,
        "admin_pages/chat_enquiry_detail.html",
        {
            "enquiry": enquiry,
            "conversation": conversation,
             "status_choices": ChatEnquiry.STATUS_CHOICES,
        },
    )



@_admin_required
@require_POST
def chat_enquiry_update_status(
    request,
    pk,
):

    enquiry = get_object_or_404(
        ChatEnquiry,
        pk=pk,
    )

    new_status = request.POST.get(
        "status",
        "",
    ).strip()

    valid_statuses = {
        value
        for value, label
        in ChatEnquiry.STATUS_CHOICES
    }

    if new_status not in valid_statuses:

        messages.error(
            request,
            "Invalid enquiry status.",
        )

        return redirect(
            "chat_enquiry_detail",
            pk=enquiry.pk,
        )

    enquiry.status = new_status

    enquiry.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    messages.success(
        request,
        "Enquiry status updated successfully.",
    )

    return redirect(
        "chat_enquiry_detail",
        pk=enquiry.pk,
    )



@_admin_required
@require_POST
def chat_enquiry_delete(
    request,
    pk,
):

    enquiry = get_object_or_404(
        ChatEnquiry,
        pk=pk,
    )

    enquiry.delete()

    messages.success(
        request,
        "Chat enquiry deleted successfully.",
    )

    return redirect(
        "chat_enquiry_list"
    )




# blog details 

def blog_detail(request, slug):

    blog = get_object_or_404(
        Blog,
        slug=slug,
    )

    return render(
        request,
        "frontend/blog_detail.html",
        {
            "blog": blog,
        },
    )