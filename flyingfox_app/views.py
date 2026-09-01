import json
import os
import re
import secrets

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower, TruncDate, TruncMonth
from django.db.models import Q, Count, Sum
from django.db import transaction
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Prefetch
from datetime import date, time
from django.utils.dateparse import parse_date
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from datetime import datetime, time


import razorpay



from .chatbot.engine import process_message
from .chatbot.responses import get_response
from .chatbot.languages import SUPPORTED_LANGUAGES

from django.contrib.auth.decorators import permission_required
from django.contrib.auth import (
    authenticate,
    login,
    logout,
)

import re

# chatbot updation 
from .chatbot.engine import process_message
from .chatbot.languages import SUPPORTED_LANGUAGES


import unicodedata

from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from django.db.models import Prefetch
from django.utils.dateparse import parse_date
from .forms import OfferForm
import qrcode

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.conf import settings
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.db import transaction
from django.http import FileResponse, Http404, JsonResponse, request
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST
from .utils import send_otp, verify_otp,send_ticket_whatsapp


from django.views.decorators.http import (
    require_GET,
    require_POST,
)


from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date


from flyingfox_app.forms import ContactEnquiryForm, TestimonialForm
from .services.refunds import create_razorpay_refund
from .services.refund_status import (
    mark_refund_processed,
    mark_refund_failed,
)
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


from .services.ride_slot_service import (
    get_available_slots,
    allocate_participants_from_start_slot,
)

from .services.telinfy import (
    send_payment_confirmation_sms,
)


from .models import (
    BookingWeightGroup,
    ChatEnquiry,
    ChatbotRule,
    ChatMessage,
    ChatSession,
    ContactEnquiry,
    GalleryCategory,
    GalleryItem,
    Blog,
    ContactMessage,
    Offer,
    UserProfile,
    RideMedia,
    Ride, RidePrice, Booking,
    Payment,
    Ticket,
    Coupon,Testimonial,Offer,WEIGHT_RANGES, Refund,BookingRideItem,BookingRideSlot
)



# =========================================================
# LOGIN PHONE COUNTRIES
# =========================================================

LOGIN_COUNTRIES = {
    "IN": {
        "name": "India",
        "dial_code": "+91",
        "flag": "🇮🇳",
        "min_length": 10,
        "max_length": 10,
        "placeholder": "9633650345",
    },

    "AE": {
        "name": "United Arab Emirates",
        "dial_code": "+971",
        "flag": "🇦🇪",
        "min_length": 9,
        "max_length": 9,
        "placeholder": "501234567",
    },

    "SA": {
        "name": "Saudi Arabia",
        "dial_code": "+966",
        "flag": "🇸🇦",
        "min_length": 9,
        "max_length": 9,
        "placeholder": "501234567",
    },

    "QA": {
        "name": "Qatar",
        "dial_code": "+974",
        "flag": "🇶🇦",
        "min_length": 8,
        "max_length": 8,
        "placeholder": "33123456",
    },

    "KW": {
        "name": "Kuwait",
        "dial_code": "+965",
        "flag": "🇰🇼",
        "min_length": 8,
        "max_length": 8,
        "placeholder": "51234567",
    },

    "OM": {
        "name": "Oman",
        "dial_code": "+968",
        "flag": "🇴🇲",
        "min_length": 8,
        "max_length": 8,
        "placeholder": "92123456",
    },

    "BH": {
        "name": "Bahrain",
        "dial_code": "+973",
        "flag": "🇧🇭",
        "min_length": 8,
        "max_length": 8,
        "placeholder": "36123456",
    },

    "GB": {
        "name": "United Kingdom",
        "dial_code": "+44",
        "flag": "🇬🇧",
        "min_length": 10,
        "max_length": 10,
        "placeholder": "7911123456",
    },

    "US": {
        "name": "United States",
        "dial_code": "+1",
        "flag": "🇺🇸",
        "min_length": 10,
        "max_length": 10,
        "placeholder": "2025550123",
    },
}






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





@_admin_required
def admin_dashboard(request):

    today = timezone.localdate()

    # ============================================================
    # BASIC COUNTS
    # ============================================================

    total_bookings = Booking.objects.count()

    today_bookings = Booking.objects.filter(
        booking_date=today
    ).count()

    confirmed_bookings = Booking.objects.filter(
        status="confirmed"
    ).count()

    payment_pending = Booking.objects.filter(
        status="payment_pending"
    ).count()

    cancelled_bookings = Booking.objects.filter(
        status="cancelled"
    ).count()

    active_rides = Ride.objects.filter(
        is_active=True
    ).count()

    total_coupons = Coupon.objects.count()


    # ============================================================
    # REVENUE
    #
    # Only count successfully paid payments.
    # ============================================================

    revenue_data = Payment.objects.filter(
        status="paid"
    ).aggregate(
        total=Sum("amount")
    )

    total_revenue = revenue_data["total"] or 0


    # ============================================================
    # TODAY'S REVENUE
    # ============================================================

    today_revenue_data = Payment.objects.filter(
        status="paid",
        paid_at__date=today
    ).aggregate(
        total=Sum("amount")
    )

    today_revenue = today_revenue_data["total"] or 0


    # ============================================================
    # LAST 6 MONTHS
    # ============================================================

    month_labels = []
    booking_counts = []
    revenue_counts = []

    year = today.year
    month = today.month

    for i in range(5, -1, -1):

        current_month = month - i
        current_year = year

        while current_month <= 0:
            current_month += 12
            current_year -= 1

        month_start = date(
            current_year,
            current_month,
            1
        )

        if current_month == 12:
            next_month = date(
                current_year + 1,
                1,
                1
            )
        else:
            next_month = date(
                current_year,
                current_month + 1,
                1
            )


        # --------------------------------------------------------
        # Label
        # --------------------------------------------------------

        month_labels.append(
            month_start.strftime("%b")
        )


        # --------------------------------------------------------
        # Bookings
        # --------------------------------------------------------

        monthly_bookings = Booking.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lt=next_month
        ).count()

        booking_counts.append(
            monthly_bookings
        )


        # --------------------------------------------------------
        # Revenue
        # --------------------------------------------------------

        monthly_revenue = Payment.objects.filter(
            status="paid",
            paid_at__date__gte=month_start,
            paid_at__date__lt=next_month
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0

        revenue_counts.append(
            float(monthly_revenue)
        )


    # ============================================================
    # BOOKING STATUS CHART
    # ============================================================

    status_labels = [
    "Confirmed",
    "Payment Pending",
    "Cancelled",
    "Checked In",
    "Refunded",
     ]

    status_values = [
       Booking.objects.filter(
        status="confirmed"
    ).count(),

       Booking.objects.filter(
        status="payment_pending"
    ).count(),

       Booking.objects.filter(
        status="cancelled"
    ).count(),

        Booking.objects.filter(
        status="checked_in"
    ).count(),

        Booking.objects.filter(
        status="refunded"
    ).count(),
    ] 


    # ============================================================
    # TODAY'S BOOKINGS
    # ============================================================

    today_bookings_list = (
        Booking.objects
        .filter(
            booking_date=today
        )
        .select_related(
            "ride",
            "ride_price",
            "user",
        )
        .order_by(
            "time_slot",
            "-created_at"
        )[:8]
    )


    # ============================================================
    # RECENT BOOKINGS
    # ============================================================

    recent_bookings = (
        Booking.objects
        .select_related(
            "ride",
            "user",
        )
        .order_by(
            "-created_at"
        )[:8]
    )


    # ============================================================
    # RECENT PAYMENTS
    # ============================================================

    recent_payments = (
        Payment.objects
        .select_related(
            "booking",
            "booking__ride",
        )
        .order_by(
            "-created_at"
        )[:8]
    )


    # ============================================================
    # CONTEXT
    # ============================================================

    context = {

        # -----------------------------
        # Stats
        # -----------------------------

        "stats": {
            "total_bookings": total_bookings,
            "today_bookings": today_bookings,
            "confirmed_bookings": confirmed_bookings,
            "payment_pending": payment_pending,
            "cancelled_bookings": cancelled_bookings,
            "active_rides": active_rides,
            "total_coupons": total_coupons,
            "total_revenue": total_revenue,
            "today_revenue": today_revenue,
        },


        # -----------------------------
        # Chart data
        # -----------------------------

        "month_labels": month_labels,

        "booking_counts": booking_counts,

        "revenue_counts": revenue_counts,

        "status_labels": status_labels,

        "status_values": status_values,


        # -----------------------------
        # Lists
        # -----------------------------

        "today_bookings": today_bookings_list,

        "recent_bookings": recent_bookings,

        "recent_payments": recent_payments,

    }


    return render(
        request,
        "admin_pages/dashboard.html",
        context
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



def contact_enquiry_list(request):

    enquiries = ContactEnquiry.objects.all().order_by("-created_at")

    # Search
    search = request.GET.get("search", "").strip()

    if search:
        enquiries = enquiries.filter(
            Q(name__icontains=search)
        ) | enquiries.filter(
            Q(email__icontains=search)
        ) | enquiries.filter(
            Q(subject__icontains=search)
        )

    # Pagination
    paginator = Paginator(enquiries, 10)

    page_number = request.GET.get("page")

    contacts = paginator.get_page(page_number)

    return render(
        request,
        "admin_pages/contact_enquiry_list.html",
        {
            "contacts": contacts,
            "search": search,
        }
    )




def contact_enquiry_detail(request, pk):

    contact = get_object_or_404(
        ContactEnquiry,
        pk=pk
    )

    # Mark enquiry as read
    if not contact.is_read:
        contact.is_read = True
        contact.save(
            update_fields=["is_read"]
        )

    return render(
        request,
        "admin_pages/contact_enquiry_detail.html",
        {
            "contact": contact
        }
    )




def contact_enquiry_delete(request, pk):

    contact = get_object_or_404(
        ContactEnquiry,
        pk=pk
    )

    if request.method == "POST":

        contact.delete()

        messages.success(
            request,
            "Contact enquiry deleted successfully."
        )

    return redirect(
        "contact_enquiry_list"
    )







# ==========================================
# USER MANAGEMENT
# ==========================================


@login_required(
    login_url="admin_login"
)
def user_list(request):

    # =====================================================
    # USERS
    # =====================================================

    users_qs = (
        UserProfile.objects
        .annotate(
            booking_count=Count(
                "bookings"
            )
        )
        .order_by(
            "-created_at"
        )
    )


    # =====================================================
    # FILTER VALUES
    # =====================================================

    search = (
        request.GET.get(
            "search",
            ""
        )
        .strip()
    )


    verification = (
        request.GET.get(
            "verification",
            ""
        )
        .strip()
    )


    # =====================================================
    # SEARCH
    # =====================================================

    if search:

        users_qs = (
            users_qs.filter(

                Q(
                    full_name__icontains=
                        search
                )

                |

                Q(
                    email__icontains=
                        search
                )

                |

                Q(
                    phone__icontains=
                        search
                )

                |

                Q(
                    region__icontains=
                        search
                )

                |

                Q(
                    pincode__icontains=
                        search
                )

            )
        )


    # =====================================================
    # VERIFICATION FILTER
    # =====================================================

    if verification == "verified":

        users_qs = (
            users_qs.filter(
                phone_verified=True
            )
        )


    elif verification == "unverified":

        users_qs = (
            users_qs.filter(
                phone_verified=False
            )
        )


    # =====================================================
    # PAGINATION
    # =====================================================

    paginator = Paginator(
        users_qs,
        10,
    )


    users = (
        paginator.get_page(
            request.GET.get(
                "page"
            )
        )
    )


    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "admin_pages/user_list.html",
        {
            "users":
                users,

            "search":
                search,

            "selected_verification":
                verification,
        },
    )


@login_required(
    login_url="admin_login"
)
def user_delete(
    request,
    pk,
):

    user = get_object_or_404(
        UserProfile,
        pk=pk,
    )


    if request.method != "POST":

        return redirect(
            "user_list"
        )


    display_name = (
        user.full_name
        or
        user.phone
    )


    user.delete()


    messages.success(
        request,
        (
            f'User "{display_name}" '
            f"deleted successfully."
        )
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



from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from .models import Ride, RideMedia




@login_required(login_url="admin_login")
def ride_create(request):

    if request.method == "POST":

        # =====================================================
        # BASIC RIDE DETAILS
        # =====================================================

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


        # =====================================================
        # SLOT SETTINGS
        # =====================================================

        capacity_per_slot_raw = request.POST.get(
            "capacity_per_slot",
            ""
        ).strip()

        slot_duration_minutes_raw = request.POST.get(
            "slot_duration_minutes",
            ""
        ).strip()


        # =====================================================
        # STATUS
        # =====================================================

        is_featured = (
            request.POST.get("is_featured")
            ==
            "on"
        )

        is_active = (
            request.POST.get("is_active")
            ==
            "on"
        )


        # =====================================================
        # PRESERVE FORM DATA
        # =====================================================

        form_data = {

            "name":
                name,

            "description":
                description,

            "duration":
                duration,

            "safety_notes":
                safety_notes,

            "capacity_per_slot":
                capacity_per_slot_raw,

            "slot_duration_minutes":
                slot_duration_minutes_raw,

            "is_featured":
                is_featured,

            "is_active":
                is_active,
        }


        # =====================================================
        # VALIDATE BASIC FIELDS
        # =====================================================

        if not name:

            messages.error(
                request,
                "Ride name is required."
            )

            return render(
                request,
                "admin_pages/ride_form.html",
                {
                    "form_data":
                        form_data
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
                    "form_data":
                        form_data
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
                    "form_data":
                        form_data
                }
            )


        # =====================================================
        # VALIDATE CAPACITY
        # =====================================================

        try:

            capacity_per_slot = int(
                capacity_per_slot_raw
            )

        except (
            TypeError,
            ValueError
        ):

            capacity_per_slot = 0


        if capacity_per_slot <= 0:

            messages.error(
                request,
                (
                    "Capacity per slot must be "
                    "greater than zero."
                )
            )

            return render(
                request,
                "admin_pages/ride_form.html",
                {
                    "form_data":
                        form_data
                }
            )


        # =====================================================
        # VALIDATE SLOT DURATION
        # =====================================================

        try:

            slot_duration_minutes = int(
                slot_duration_minutes_raw
            )

        except (
            TypeError,
            ValueError
        ):

            slot_duration_minutes = 0


        if slot_duration_minutes <= 0:

            messages.error(
                request,
                (
                    "Slot duration must be "
                    "greater than zero."
                )
            )

            return render(
                request,
                "admin_pages/ride_form.html",
                {
                    "form_data":
                        form_data
                }
            )


        # =====================================================
        # MEDIA
        # =====================================================

        images = request.FILES.getlist(
            "images"
        )

        video = request.FILES.get(
            "video"
        )


        # =====================================================
        # CREATE RIDE
        # =====================================================

        try:

            with transaction.atomic():

                ride = Ride.objects.create(

                    name=
                        name,

                    description=
                        description,

                    duration=
                        duration,

                    safety_notes=
                        safety_notes,

                    capacity_per_slot=
                        capacity_per_slot,

                    slot_duration_minutes=
                        slot_duration_minutes,

                    is_featured=
                        is_featured,

                    is_active=
                        is_active,
                )


                # =================================================
                # IMAGES
                # =================================================

                for image in images:

                    RideMedia.objects.create(

                        ride=
                            ride,

                        media_type=
                            "image",

                        image=
                            image,
                    )


                # =================================================
                # VIDEO
                # =================================================

                if video:

                    RideMedia.objects.create(

                        ride=
                            ride,

                        media_type=
                            "video",

                        video=
                            video,
                    )


        except Exception as error:

            print(
                "RIDE CREATION ERROR:",
                error
            )

            messages.error(
                request,
                f"Unable to create ride: {error}"
            )

            return render(
                request,
                "admin_pages/ride_form.html",
                {
                    "form_data":
                        form_data
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

        # =====================================================
        # BASIC DETAILS
        # =====================================================

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


        # =====================================================
        # SLOT SETTINGS
        # =====================================================

        capacity_per_slot_raw = request.POST.get(
            "capacity_per_slot",
            ""
        ).strip()

        slot_duration_minutes_raw = request.POST.get(
            "slot_duration_minutes",
            ""
        ).strip()


        # =====================================================
        # STATUS
        # =====================================================

        is_featured = (
            request.POST.get("is_featured")
            ==
            "on"
        )

        is_active = (
            request.POST.get("is_active")
            ==
            "on"
        )


        # =====================================================
        # VALIDATION
        # =====================================================

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


        # =====================================================
        # CAPACITY VALIDATION
        # =====================================================

        try:

            capacity_per_slot = int(
                capacity_per_slot_raw
            )

        except (
            TypeError,
            ValueError
        ):

            capacity_per_slot = 0


        if capacity_per_slot <= 0:

            messages.error(
                request,
                (
                    "Capacity per slot must be "
                    "greater than zero."
                )
            )

            return render(
                request,
                "admin_pages/ride_form.html",
                {
                    "ride": ride,
                }
            )


        # =====================================================
        # SLOT DURATION VALIDATION
        # =====================================================

        try:

            slot_duration_minutes = int(
                slot_duration_minutes_raw
            )

        except (
            TypeError,
            ValueError
        ):

            slot_duration_minutes = 0


        if slot_duration_minutes <= 0:

            messages.error(
                request,
                (
                    "Slot duration must be "
                    "greater than zero."
                )
            )

            return render(
                request,
                "admin_pages/ride_form.html",
                {
                    "ride": ride,
                }
            )


        # =====================================================
        # MEDIA
        # =====================================================

        images = request.FILES.getlist(
            "images"
        )

        video = request.FILES.get(
            "video"
        )


        try:

            with transaction.atomic():

                # =================================================
                # UPDATE RIDE
                # =================================================

                ride.name = name

                ride.description = description

                ride.duration = duration

                ride.safety_notes = safety_notes

                ride.capacity_per_slot = (
                    capacity_per_slot
                )

                ride.slot_duration_minutes = (
                    slot_duration_minutes
                )

                ride.is_featured = (
                    is_featured
                )

                ride.is_active = (
                    is_active
                )

                ride.save()


                # =================================================
                # ADD NEW IMAGES
                # =================================================

                for image in images:

                    RideMedia.objects.create(

                        ride=
                            ride,

                        media_type=
                            "image",

                        image=
                            image,
                    )


                # =================================================
                # ADD NEW VIDEO
                # =================================================

                if video:

                    RideMedia.objects.create(

                        ride=
                            ride,

                        media_type=
                            "video",

                        video=
                            video,
                    )


        except Exception as error:

            print(
                "RIDE UPDATE ERROR:",
                error
            )

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

    # =====================================================
    # PREFETCH RIDE SLOT ALLOCATIONS
    #
    # We keep every slot status so admin can understand
    # pending / confirmed / cancelled / expired bookings.
    # =====================================================

    slot_queryset = (
        BookingRideSlot.objects
        .order_by(
            "slot_start_time"
        )
    )


    # =====================================================
    # BOOKINGS
    # =====================================================

    bookings_qs = (
        Booking.objects

        .select_related(
            "user",
            "payment",
            "ticket",
        )

        .prefetch_related(

            "ride_items__ride",

            "ride_items__ride_price",

            "ride_items__offer",

            "ride_items__weight_groups",

            Prefetch(
                "ride_items__allocated_slots",
                queryset=slot_queryset,
                to_attr="admin_slots",
            ),
        )

        .order_by(
            "-created_at"
        )
    )


    # =====================================================
    # SEARCH
    # =====================================================

    search = (
        request.GET.get(
            "search",
            ""
        )
        .strip()
    )


    status = (
        request.GET.get(
            "status",
            ""
        )
        .strip()
    )


    if search:

        bookings_qs = (
            bookings_qs

            .filter(

                Q(
                    customer_name__icontains=
                        search
                )

                |

                Q(
                    customer_email__icontains=
                        search
                )

                |

                Q(
                    customer_phone__icontains=
                        search
                )

                |

                Q(
                    booking_id__icontains=
                        search
                )

                |

                Q(
                    applied_coupon_code__icontains=
                        search
                )

                |

                Q(
                    ride_items__ride__name__icontains=
                        search
                )
            )

            .distinct()
        )


    # =====================================================
    # STATUS FILTER
    # =====================================================

    if status:

        bookings_qs = (
            bookings_qs.filter(
                status=status
            )
        )


    # =====================================================
    # PAGINATION
    # =====================================================

    paginator = Paginator(
        bookings_qs,
        10,
    )


    bookings = (
        paginator.get_page(
            request.GET.get(
                "page"
            )
        )
    )


    # =====================================================
    # PREPARE DISPLAY DATA
    #
    # Add admin_ride_items directly to each Booking so the
    # template does not need complicated slot logic.
    # =====================================================

    for booking in bookings:

        ride_items = list(
            booking.ride_items.all()
        )

        booking_total_participants = 0


        for item in ride_items:

            booking_total_participants += (
                item.quantity or 0
            )


            # =============================================
            # SLOT ROWS WERE PREFETCHED ABOVE
            # =============================================

            slot_rows = list(
                getattr(
                    item,
                    "admin_slots",
                    []
                )
            )


            # =============================================
            # DISPLAY SLOT INFORMATION
            # =============================================

            display_slots = []


            for slot in slot_rows:

                display_slots.append(
                    {
                        "start_time":
                            slot.slot_start_time,

                        "end_time":
                            slot.slot_end_time,

                        "start_label":
                            slot.slot_start_time.strftime(
                                "%I:%M %p"
                            ),

                        "end_label":
                            slot.slot_end_time.strftime(
                                "%I:%M %p"
                            ),

                        "participant_count":
                            slot.participant_count,

                        "status":
                            slot.status,

                        "status_label":
                            slot.get_status_display(),

                        "hold_expires_at":
                            slot.hold_expires_at,
                    }
                )


            item.admin_display_slots = (
                display_slots
            )


        booking.admin_ride_items = (
            ride_items
        )


        booking.admin_total_participants = (
            booking_total_participants
        )


    # =====================================================
    # RENDER
    # =====================================================

    return render(

        request,

        "admin_pages/booking_list.html",

        {
            "bookings":
                bookings,

            "search":
                search,

            "selected_status":
                status,

            "status_choices":
                Booking.STATUS_CHOICES,
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

    # =====================================================
    # SLOT PREFETCH
    # =====================================================

    slot_queryset = (
        BookingRideSlot.objects
        .order_by(
            "slot_start_time"
        )
    )


    # =====================================================
    # BOOKING
    # =====================================================

    booking = get_object_or_404(

        Booking.objects

        .select_related(
            "user",
            "payment",
            "ticket",
        )

        .prefetch_related(

            "ride_items__ride",

            "ride_items__ride_price",

            "ride_items__offer",

            "ride_items__weight_groups",

            Prefetch(
                "ride_items__allocated_slots",
                queryset=slot_queryset,
                to_attr="admin_slots",
            ),
        ),

        pk=pk,

    )


    # =====================================================
    # PAYMENT
    # =====================================================

    payment = getattr(
        booking,
        "payment",
        None,
    )


    # =====================================================
    # TICKET
    # =====================================================

    ticket = getattr(
        booking,
        "ticket",
        None,
    )


    # =====================================================
    # RIDE ITEMS
    # =====================================================

    ride_items = list(
        booking.ride_items.all()
    )


    # =====================================================
    # PREPARE RIDE SLOT SCHEDULES
    # =====================================================

    total_confirmed_riders = 0
    total_held_riders = 0
    total_cancelled_riders = 0
    total_expired_riders = 0


    for item in ride_items:

        slot_rows = list(
            getattr(
                item,
                "admin_slots",
                []
            )
        )


        display_slots = []


        for slot in slot_rows:

            # =============================================
            # COUNT SLOT STATUS
            # =============================================

            if slot.status == "confirmed":

                total_confirmed_riders += (
                    slot.participant_count
                )

            elif slot.status == "held":

                total_held_riders += (
                    slot.participant_count
                )

            elif slot.status == "cancelled":

                total_cancelled_riders += (
                    slot.participant_count
                )

            elif slot.status == "expired":

                total_expired_riders += (
                    slot.participant_count
                )


            # =============================================
            # DISPLAY DATA
            # =============================================

            display_slots.append(
                {
                    "start_time":
                        slot.slot_start_time,

                    "end_time":
                        slot.slot_end_time,

                    "start_label":
                        slot.slot_start_time.strftime(
                            "%I:%M %p"
                        ),

                    "end_label":
                        slot.slot_end_time.strftime(
                            "%I:%M %p"
                        ),

                    "participant_count":
                        slot.participant_count,

                    "status":
                        slot.status,

                    "status_label":
                        slot.get_status_display(),

                    "hold_expires_at":
                        slot.hold_expires_at,
                }
            )


        item.admin_display_slots = (
            display_slots
        )


        # =============================================
        # TOTAL ALLOCATED RIDERS FOR THIS RIDE
        # =============================================

        item.admin_allocated_riders = sum(

            slot["participant_count"]

            for slot
            in display_slots

        )


    # =====================================================
    # TOTAL PARTICIPANTS
    # =====================================================

    total_participants = sum(

        (
            item.quantity
            or 0
        )

        for item
        in ride_items

    )


    # =====================================================
    # TOTAL BOOKING AMOUNT
    # =====================================================

    total_amount = sum(

        (
            item.total_amount
            or 0
        )

        for item
        in ride_items

    )


    # =====================================================
    # CONTEXT
    # =====================================================

    return render(

        request,

        "admin_pages/booking_detail.html",

        {
            "booking":
                booking,

            "payment":
                payment,

            "ticket":
                ticket,

            "ride_items":
                ride_items,

            "total_participants":
                total_participants,

            "total_amount":
                total_amount,

            "total_confirmed_riders":
                total_confirmed_riders,

            "total_held_riders":
                total_held_riders,

            "total_cancelled_riders":
                total_cancelled_riders,

            "total_expired_riders":
                total_expired_riders,
        },

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


# =========================================================
# TRANSACTION LIST
# =========================================================

@_admin_required
def transaction_list(request):

    # =====================================================
    # SLOT PREFETCH
    # =====================================================

    slot_queryset = (
        BookingRideSlot.objects
        .order_by(
            "slot_start_time"
        )
    )


    # =====================================================
    # PAYMENT QUERY
    # =====================================================

    payments_qs = (
        Payment.objects

        .select_related(
            "booking",
            "booking__user",
            "booking__ticket",
        )

        .prefetch_related(

            "booking__ride_items__ride",

            "booking__ride_items__ride_price",

            "booking__ride_items__offer",

            "booking__ride_items__weight_groups",

            Prefetch(
                "booking__ride_items__allocated_slots",
                queryset=slot_queryset,
                to_attr="admin_slots",
            ),
        )

        .order_by(
            "-created_at"
        )
    )


    # =====================================================
    # FILTER VALUES
    # =====================================================

    search = (
        request.GET.get(
            "search",
            ""
        )
        .strip()
    )


    status = (
        request.GET.get(
            "status",
            ""
        )
        .strip()
    )


    booking_date_raw = (
        request.GET.get(
            "booking_date",
            ""
        )
        .strip()
    )


    booking_date = (
        parse_date(
            booking_date_raw
        )
        if booking_date_raw
        else None
    )


    # =====================================================
    # SEARCH
    # =====================================================

    if search:

        payments_qs = (
            payments_qs

            .filter(

                Q(
                    booking__customer_name__icontains=
                        search
                )

                |

                Q(
                    booking__customer_email__icontains=
                        search
                )

                |

                Q(
                    booking__customer_phone__icontains=
                        search
                )

                |

                Q(
                    booking__booking_id__icontains=
                        search
                )

                |

                Q(
                    booking__ride_items__ride__name__icontains=
                        search
                )

                |

                Q(
                    gateway_order_id__icontains=
                        search
                )

                |

                Q(
                    gateway_payment_id__icontains=
                        search
                )
            )

            .distinct()
        )


    # =====================================================
    # PAYMENT STATUS FILTER
    # =====================================================

    if status:

        payments_qs = (
            payments_qs.filter(
                status=status
            )
        )


    # =====================================================
    # VISIT DATE FILTER
    # =====================================================

    if booking_date:

        payments_qs = (
            payments_qs.filter(
                booking__booking_date=
                    booking_date
            )
        )


    # =====================================================
    # PAGINATION
    # =====================================================

    paginator = Paginator(
        payments_qs,
        10,
    )


    payments = (
        paginator.get_page(
            request.GET.get(
                "page"
            )
        )
    )


    # =====================================================
    # PREPARE MULTI-RIDE DISPLAY DATA
    # =====================================================

    for payment in payments:

        booking = (
            payment.booking
        )


        ride_items = list(
            booking.ride_items.all()
        )


        total_participants = 0


        for item in ride_items:

            total_participants += (
                item.quantity or 0
            )


            slot_rows = list(
                getattr(
                    item,
                    "admin_slots",
                    []
                )
            )


            item.admin_display_slots = []


            for slot in slot_rows:

                item.admin_display_slots.append(
                    {
                        "start_label":
                            slot.slot_start_time.strftime(
                                "%I:%M %p"
                            ),

                        "end_label":
                            slot.slot_end_time.strftime(
                                "%I:%M %p"
                            ),

                        "participant_count":
                            slot.participant_count,

                        "status":
                            slot.status,

                        "status_label":
                            slot.get_status_display(),
                    }
                )


        booking.admin_ride_items = (
            ride_items
        )


        booking.admin_total_participants = (
            total_participants
        )


    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "admin_pages/transaction_list.html",
        {
            "payments":
                payments,

            "search":
                search,

            "selected_status":
                status,

            "selected_booking_date":
                booking_date,

            "status_choices":
                Payment.STATUS_CHOICES,
        },
    )




# =========================================================
# TRANSACTION DETAIL
# =========================================================

# =========================================================
# TRANSACTION DETAIL
# =========================================================

@_admin_required
def transaction_detail(
    request,
    pk,
):

    # =====================================================
    # SLOT PREFETCH
    # =====================================================

    slot_queryset = (
        BookingRideSlot.objects
        .order_by(
            "slot_start_time"
        )
    )


    # =====================================================
    # PAYMENT
    # =====================================================

    payment = get_object_or_404(

        Payment.objects

        .select_related(
            "booking",
            "booking__user",
            "booking__ticket",
        )

        .prefetch_related(

            "booking__ride_items__ride",

            "booking__ride_items__ride_price",

            "booking__ride_items__offer",

            "booking__ride_items__weight_groups",

            Prefetch(
                "booking__ride_items__allocated_slots",
                queryset=slot_queryset,
                to_attr="admin_slots",
            ),

        ),

        pk=pk,
    )


    # =====================================================
    # BOOKING
    # =====================================================

    booking = (
        payment.booking
    )


    # =====================================================
    # TICKET
    # =====================================================

    ticket = getattr(
        booking,
        "ticket",
        None,
    )


    # =====================================================
    # RIDE ITEMS
    # =====================================================

    ride_items = list(
        booking.ride_items.all()
    )


    # =====================================================
    # PREPARE SLOT DATA
    # =====================================================

    total_confirmed_riders = 0
    total_held_riders = 0
    total_cancelled_riders = 0
    total_expired_riders = 0


    for item in ride_items:

        slot_rows = list(
            getattr(
                item,
                "admin_slots",
                []
            )
        )


        display_slots = []


        for slot in slot_rows:

            # =============================================
            # STATUS TOTALS
            # =============================================

            if slot.status == "confirmed":

                total_confirmed_riders += (
                    slot.participant_count
                )

            elif slot.status == "held":

                total_held_riders += (
                    slot.participant_count
                )

            elif slot.status == "cancelled":

                total_cancelled_riders += (
                    slot.participant_count
                )

            elif slot.status == "expired":

                total_expired_riders += (
                    slot.participant_count
                )


            # =============================================
            # DISPLAY SLOT
            # =============================================

            display_slots.append(
                {
                    "start_time":
                        slot.slot_start_time,

                    "end_time":
                        slot.slot_end_time,

                    "start_label":
                        slot.slot_start_time.strftime(
                            "%I:%M %p"
                        ),

                    "end_label":
                        slot.slot_end_time.strftime(
                            "%I:%M %p"
                        ),

                    "participant_count":
                        slot.participant_count,

                    "status":
                        slot.status,

                    "status_label":
                        slot.get_status_display(),

                    "hold_expires_at":
                        slot.hold_expires_at,
                }
            )


        item.admin_display_slots = (
            display_slots
        )


        item.admin_allocated_riders = sum(

            slot[
                "participant_count"
            ]

            for slot
            in display_slots

        )


    # =====================================================
    # TOTAL PARTICIPANTS
    # =====================================================

    total_participants = sum(

        (
            item.quantity
            or 0
        )

        for item
        in ride_items

    )


    # =====================================================
    # TOTAL BOOKING AMOUNT
    # =====================================================

    total_amount = sum(

        (
            item.total_amount
            or 0
        )

        for item
        in ride_items

    )


    # =====================================================
    # CONTEXT
    # =====================================================

    return render(

        request,

        "admin_pages/transaction_detail.html",

        {
            "payment":
                payment,

            "booking":
                booking,

            "ticket":
                ticket,

            "ride_items":
                ride_items,

            "total_participants":
                total_participants,

            "total_amount":
                total_amount,

            "total_confirmed_riders":
                total_confirmed_riders,

            "total_held_riders":
                total_held_riders,

            "total_cancelled_riders":
                total_cancelled_riders,

            "total_expired_riders":
                total_expired_riders,
        },

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
        return redirect("user_dashboard")

    selected_country = "IN"
    phone = ""

    if request.method == "POST":

        selected_country = (
            request.POST.get("country", "IN")
            .strip()
            .upper()
        )

        phone = (
            request.POST.get("phone", "")
            .strip()
        )

        # ---------------------------------------------
        # COUNTRY
        # ---------------------------------------------

        country = LOGIN_COUNTRIES.get(selected_country)

        if not country:

            messages.error(
                request,
                "Please select a valid country."
            )

            return render(
                request,
                "authenticate/signin.html",
                {
                    "phone": phone,
                    "countries": LOGIN_COUNTRIES,
                    "selected_country": "IN",
                }
            )

        # ---------------------------------------------
        # CLEAN PHONE
        # ---------------------------------------------

        phone = "".join(
            char for char in phone
            if char.isdigit()
        )

        phone = phone.lstrip("0")

        # ---------------------------------------------
        # VALIDATE PHONE
        # ---------------------------------------------

        if not phone:

            messages.error(
                request,
                "Please enter your mobile number."
            )

            return render(
                request,
                "authenticate/signin.html",
                {
                    "phone": phone,
                    "countries": LOGIN_COUNTRIES,
                    "selected_country": selected_country,
                }
            )

        min_length = country["min_length"]
        max_length = country["max_length"]

        if not (
            min_length <= len(phone) <= max_length
        ):

            if min_length == max_length:

                error_message = (
                    f"Please enter a valid "
                    f"{min_length}-digit mobile number "
                    f"for {country['name']}."
                )

            else:

                error_message = (
                    f"Please enter a valid mobile number "
                    f"for {country['name']}."
                )

            messages.error(
                request,
                error_message
            )

            return render(
                request,
                "authenticate/signin.html",
                {
                    "phone": phone,
                    "countries": LOGIN_COUNTRIES,
                    "selected_country": selected_country,
                }
            )

        # ---------------------------------------------
        # FULL INTERNATIONAL PHONE
        # ---------------------------------------------

        full_phone = (
            country["dial_code"] + phone
        )

        # ---------------------------------------------
        # FIND OR CREATE USER PROFILE
        # ---------------------------------------------

        profile, created = UserProfile.objects.get_or_create(
            phone=full_phone
        )

        # ---------------------------------------------
        # SEND OTP BY SMS
        # ---------------------------------------------

        try:

            otp_record, response = send_otp(
                full_phone
            )

        except Exception as e:

            print("OTP ERROR:", e)

            messages.error(
                request,
                "Unable to send OTP. Please try again."
            )

            return render(
                request,
                "authenticate/signin.html",
                {
                    "phone": phone,
                    "countries": LOGIN_COUNTRIES,
                    "selected_country": selected_country,
                }
            )

        # ---------------------------------------------
        # SAVE LOGIN SESSION
        # ---------------------------------------------

        request.session["login_phone"] = full_phone

        request.session["login_local_phone"] = phone

        request.session["login_country"] = selected_country

        request.session["login_country_code"] = (
            country["dial_code"]
        )

        request.session["login_profile_id"] = profile.id

        request.session["login_otp_verified"] = False

        # ---------------------------------------------
        # MESSAGE
        # ---------------------------------------------

        if created:

            messages.success(
                request,
                "Your account has been created. "
                "An OTP has been sent to your mobile."
            )

        else:

            messages.success(
                request,
                "OTP has been sent to your mobile number."
            )

        return redirect(
            "verify_login_otp"
        )

    # ---------------------------------------------
    # GET
    # ---------------------------------------------

    phone = (
        request.GET.get("phone", "")
        .strip()
    )

    phone = "".join(
        char for char in phone
        if char.isdigit()
    )

    return render(
        request,
        "authenticate/signin.html",
        {
            "phone": phone,
            "countries": LOGIN_COUNTRIES,
            "selected_country": selected_country,
        }
    )



       
def verify_login_otp(request):

    # =====================================================
    # GET PHONE FROM SESSION
    # =====================================================

    phone = request.session.get("login_phone")

    if not phone:

        messages.error(
            request,
            "Please enter your mobile number first."
        )

        return redirect("user_signin")


    # =====================================================
    # POST - VERIFY OTP
    # =====================================================

    if request.method == "POST":

        # -------------------------------------------------
        # Get OTP from 6 input boxes
        # -------------------------------------------------

        otp_1 = request.POST.get(
            "otp_1",
            ""
        ).strip()

        otp_2 = request.POST.get(
            "otp_2",
            ""
        ).strip()

        otp_3 = request.POST.get(
            "otp_3",
            ""
        ).strip()

        otp_4 = request.POST.get(
            "otp_4",
            ""
        ).strip()

        otp_5 = request.POST.get(
            "otp_5",
            ""
        ).strip()

        otp_6 = request.POST.get(
            "otp_6",
            ""
        ).strip()


        # -------------------------------------------------
        # Combine OTP
        # -------------------------------------------------

        entered_otp = (
            otp_1
            + otp_2
            + otp_3
            + otp_4
            + otp_5
            + otp_6
        )


        # -------------------------------------------------
        # Validate OTP format
        # -------------------------------------------------

        if (
            len(entered_otp) != 6
            or not entered_otp.isdigit()
        ):

            messages.error(
                request,
                "Please enter the complete 6-digit OTP."
            )

            return render(
                request,
                "authenticate/verify_otp.html",
                {
                    "phone": phone
                }
            )


        # -------------------------------------------------
        # Verify OTP from OTPVerification model
        # -------------------------------------------------

        success, message = verify_otp(
            phone,
            entered_otp
        )


        # -------------------------------------------------
        # Invalid / expired / too many attempts
        # -------------------------------------------------

        if not success:

            messages.error(
                request,
                message
            )

            return render(
                request,
                "authenticate/verify_otp.html",
                {
                    "phone": phone
                }
            )


        # =================================================
        # OTP VERIFIED
        # =================================================

        request.session[
            "login_otp_verified"
        ] = True


        # =================================================
        # FIND OR CREATE USER PROFILE
        # =================================================

        user, created = UserProfile.objects.get_or_create(
            phone=phone
        )


        # =================================================
        # MARK PHONE VERIFIED
        # =================================================

        if not user.phone_verified:

            user.phone_verified = True

            user.save(
                update_fields=[
                    "phone_verified"
                ]
            )


        # =================================================
        # CREATE LOGIN SESSION
        # =================================================

        request.session[
            "user_id"
        ] = user.id

        request.session[
            "user_name"
        ] = (
            user.full_name
            or "Flying Fox User"
        )


        # =================================================
        # CLEAN LOGIN SESSION DATA
        # =================================================

        request.session.pop(
            "login_phone",
            None
        )

        request.session.pop(
            "login_local_phone",
            None
        )

        request.session.pop(
            "login_country",
            None
        )

        request.session.pop(
            "login_country_code",
            None
        )

        request.session.pop(
            "login_otp_verified",
            None
        )


        # =================================================
        # SUCCESS
        # =================================================

        messages.success(
            request,
            "Mobile number verified successfully."
        )


        # =================================================
        # DASHBOARD
        # =================================================

        return redirect(
            "user_dashboard"
        )


    # =====================================================
    # GET
    # =====================================================

    return render(
        request,
        "authenticate/verify_otp.html",
        {
            "phone": phone
        }
    )



def resend_login_otp(request):

    # =====================================================
    # GET PHONE FROM SESSION
    # =====================================================

    phone = request.session.get(
        "login_phone"
    )

    if not phone:

        messages.error(
            request,
            "Please enter your mobile number first."
        )

        return redirect(
            "user_signin"
        )


    # =====================================================
    # ONLY ALLOW POST
    # =====================================================

    if request.method != "POST":

        return redirect(
            "verify_login_otp"
        )


    # =====================================================
    # SEND NEW OTP
    # =====================================================

    try:

        otp_record, response = send_otp(
            phone
        )

    except Exception as e:

        print(
            "RESEND OTP ERROR:",
            e
        )

        messages.error(
            request,
            "Unable to send OTP. Please try again."
        )

        return redirect(
            "verify_login_otp"
        )


    # =====================================================
    # SUCCESS
    # =====================================================

    messages.success(
        request,
        "A new OTP has been sent to your mobile number."
    )


    return redirect(
        "verify_login_otp"
    )





# =========================================================
# USER ACCOUNT - PROFILE
# =========================================================

def user_dashboard(request):

    user_id = request.session.get(
        "user_id"
    )


    if not user_id:

        messages.error(
            request,
            "Please login to access your account."
        )

        return redirect(
            "user_signin"
        )


    profile = get_object_or_404(
        UserProfile,
        id=user_id
    )


    # =====================================================
    # UPDATE PROFILE
    # =====================================================

    if request.method == "POST":

        full_name = request.POST.get(
            "full_name",
            ""
        ).strip()


        email = request.POST.get(
            "email",
            ""
        ).strip().lower()


        gender = request.POST.get(
            "gender",
            ""
        ).strip()


        date_of_birth = request.POST.get(
            "date_of_birth",
            ""
        ).strip()


        address = request.POST.get(
            "address",
            ""
        ).strip()


        pincode = request.POST.get(
            "pincode",
            ""
        ).strip()


        region = request.POST.get(
            "region",
            ""
        ).strip()


        # FULL NAME
        if not full_name:

            messages.error(
                request,
                "Please enter your full name."
            )

            return redirect(
                "user_dashboard"
            )


        # EMAIL DUPLICATE
        if email:

            exists = (
                UserProfile.objects
                .filter(
                    email__iexact=email
                )
                .exclude(
                    id=profile.id
                )
                .exists()
            )


            if exists:

                messages.error(
                    request,
                    "This email address is already registered."
                )

                return redirect(
                    "user_dashboard"
                )


        # PINCODE
        if pincode:

            if (
                not pincode.isdigit()
                or
                len(pincode) != 6
            ):

                messages.error(
                    request,
                    "Please enter a valid 6-digit PIN code."
                )

                return redirect(
                    "user_dashboard"
                )


        # SAVE
        profile.full_name = full_name

        profile.email = (
            email
            if email
            else None
        )

        profile.gender = gender

        profile.date_of_birth = (
            date_of_birth
            if date_of_birth
            else None
        )

        profile.address = address
        profile.pincode = pincode
        profile.region = region


        profile.whatsapp_updates = (
            request.POST.get(
                "whatsapp_updates"
            )
            ==
            "on"
        )


        profile.email_updates = (
            request.POST.get(
                "email_updates"
            )
            ==
            "on"
        )


        profile.save()


        request.session[
            "user_name"
        ] = (
            profile.full_name
            or
            "Flying Fox User"
        )


        messages.success(
            request,
            "Profile updated successfully."
        )


        return redirect(
            "user_dashboard"
        )


    return render(
        request,
        "authenticate/user_dashboard.html",
        {
            "profile": profile,
            "active_page": "profile",
        }
    )



# =========================================================
# USER BOOKINGS
# =========================================================

# =========================================================
# USER BOOKINGS
# =========================================================

def user_bookings(request):

    user_id = request.session.get(
        "user_id"
    )


    if not user_id:

        messages.error(
            request,
            "Please login to view your bookings."
        )

        return redirect(
            "user_signin"
        )


    # =====================================================
    # USER PROFILE
    # =====================================================

    profile = get_object_or_404(
        UserProfile,
        id=user_id
    )


    # =====================================================
    # USER BOOKINGS
    # =====================================================

    bookings = list(

        Booking.objects
        .filter(
            user=profile
        )
        .select_related(
            "payment",
            "ticket",
        )
        .prefetch_related(
            "refunds",
            "ride_items__ride",
            "ride_items__ride_price",
            "ride_items__offer",
            "ride_items__weight_groups",
            "ride_items__allocated_slots",
        )
        .order_by(
            "-created_at"
        )

    )


    # =====================================================
    # PREPARE BOOKING INFORMATION
    # =====================================================

    for booking in bookings:

        # ---------------------------------------------
        # MULTI-RIDE ITEMS
        # ---------------------------------------------

        ride_items = list(
            booking.ride_items.all()
        )


        booking.display_ride_items = (
            ride_items
        )


        # ---------------------------------------------
        # SLOT INFORMATION FOR EACH RIDE
        #
        # Show:
        #
        # confirmed -> active paid booking
        # cancelled -> historical cancelled booking
        # held      -> payment still pending
        #
        # Do not show expired abandoned holds.
        # ---------------------------------------------

        for item in ride_items:

            display_slots = [

                slot

                for slot
                in item.allocated_slots.all()

                if slot.status in [
                    "held",
                    "confirmed",
                    "cancelled",
                ]

            ]


            display_slots.sort(
                key=lambda slot:
                    slot.slot_start_time
            )


            item.display_slots = (
                display_slots
            )


        # ---------------------------------------------
        # PAYMENT
        # ---------------------------------------------

        payment = getattr(
            booking,
            "payment",
            None,
        )


        # ---------------------------------------------
        # MOST RECENT REFUND REQUEST
        # ---------------------------------------------

        refund_list = list(
            booking.refunds.all()
        )


        refund_list.sort(
            key=lambda item:
                item.requested_at,
            reverse=True,
        )


        booking.latest_refund = (

            refund_list[0]

            if refund_list

            else None

        )


        # ---------------------------------------------
        # CANCELLED BOOKING
        #
        # Never show another refund request button.
        # ---------------------------------------------

        if booking.status == "cancelled":

            booking.refund_info = {

                "eligible": False,

                "message": (
                    "This booking has already "
                    "been cancelled."
                ),

            }

            continue


        # ---------------------------------------------
        # EXISTING REFUND REQUEST
        # ---------------------------------------------

        if booking.latest_refund:

            booking.refund_info = {

                "eligible": False,

                "message": (
                    "A cancellation/refund request "
                    "already exists for this booking."
                ),

            }

            continue


        # ---------------------------------------------
        # CALCULATE CURRENT REFUND ELIGIBILITY
        # ---------------------------------------------

        if payment:

            booking.refund_info = (
                _calculate_booking_refund(
                    booking,
                    payment,
                )
            )

        else:

            booking.refund_info = {

                "eligible": False,

                "message": (
                    "No successful payment "
                    "was found for this booking."
                ),

            }


    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "authenticate/user_bookings.html",
        {

            "profile":
                profile,

            "bookings":
                bookings,

            "active_page":
                "bookings",

        }
    )


# =========================================================
# USER TICKETS
# =========================================================

def user_tickets(request):

    user_id = request.session.get(
        "user_id"
    )


    if not user_id:

        messages.error(
            request,
            "Please login to view your tickets."
        )

        return redirect(
            "user_signin"
        )


    profile = get_object_or_404(
        UserProfile,
        id=user_id
    )


    tickets = list(

        Ticket.objects
        .filter(
            booking__user=profile
        )
        .select_related(
            "booking",
        )
        .prefetch_related(
            "booking__ride_items__ride",
            "booking__ride_items__allocated_slots",
        )
        .order_by(
            "-created_at"
        )

    )


    # =====================================================
    # PREPARE MULTI-RIDE + SLOT INFORMATION
    # =====================================================

    for ticket in tickets:

        booking = ticket.booking


        ride_items = list(
            booking.ride_items.all()
        )


        ticket.display_ride_items = (
            ride_items
        )


        for item in ride_items:

            display_slots = [

                slot

                for slot
                in item.allocated_slots.all()

                if slot.status in [
                    "confirmed",
                    "cancelled",
                ]

            ]


            display_slots.sort(
                key=lambda slot:
                    slot.slot_start_time
            )


            item.display_slots = (
                display_slots
            )


        # ---------------------------------------------
        # ACTIVE / CANCELLED TICKET STATE
        # ---------------------------------------------

        ticket.booking_cancelled = (
            booking.status == "cancelled"
        )


    return render(
        request,
        "authenticate/user_tickets.html",
        {
            "profile":
                profile,

            "tickets":
                tickets,

            "active_page":
                "tickets",
        }
    )




# =========================================================
# USER SUPPORT
# =========================================================

def user_support(request):

    user_id = request.session.get(
        "user_id"
    )


    if not user_id:

        messages.error(
            request,
            "Please login to access support."
        )

        return redirect(
            "user_signin"
        )


    profile = get_object_or_404(
        UserProfile,
        id=user_id
    )


    return render(
        request,
        "authenticate/user_support.html",
        {
            "profile": profile,
            "active_page": "support",
        }
    )



# =========================================================
# USER LOGOUT
# =========================================================

def user_logout(request):

    request.session.flush()


    messages.success(
        request,
        "You have been logged out successfully."
    )


    return redirect("home")






# home page 

def home(request):

    today = timezone.localdate()

    # -----------------------------------------
    # RIDE VIDEOS
    # -----------------------------------------

    video_media = (
        RideMedia.objects
        .filter(
            media_type="video",
            video__isnull=False,
        )
        .exclude(video="")
        .order_by("-created_at")
    )


    # -----------------------------------------
    # RIDE IMAGES
    # -----------------------------------------

    image_media = (
        RideMedia.objects
        .filter(
            media_type="image",
            image__isnull=False,
        )
        .exclude(image="")
        .order_by("-created_at")
    )


    # -----------------------------------------
    # CURRENT RIDE PRICES
    # -----------------------------------------

    current_prices = (
        RidePrice.objects
        .filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        )
        .order_by("price")
    )


    # -----------------------------------------
    # GALLERY VIDEOS
    # -----------------------------------------

    gallery_videos = (
        GalleryItem.objects
        .filter(video__isnull=False)
        .exclude(video="")
        .order_by("-uploaded_at")[:10]
    )


    # -----------------------------------------
    # GALLERY IMAGES
    # -----------------------------------------

    gallery_images = (
        GalleryItem.objects
        .filter(image__isnull=False)
        .exclude(image="")
        .select_related("category")
        .order_by("-uploaded_at")[:8]
    )


    # -----------------------------------------
    # ALL ACTIVE RIDES
    # -----------------------------------------

    rides = (
        Ride.objects
        .filter(is_active=True)
        .prefetch_related(

            # Videos
            Prefetch(
                "media",
                queryset=video_media,
                to_attr="uploaded_videos",
            ),

            # Images
            Prefetch(
                "media",
                queryset=image_media,
                to_attr="uploaded_images",
            ),

            # Current Prices
            Prefetch(
                "prices",
                queryset=current_prices,
                to_attr="current_prices",
            ),

        )
        .order_by("-created_at")
    )


    # -----------------------------------------
# FEATURED RIDES
# -----------------------------------------

    featured_rides = (
    Ride.objects
    .filter(
        is_active=True,
        is_featured=True,
    )
    .prefetch_related(

        # Featured ride videos
        Prefetch(
            "media",
            queryset=video_media,
            to_attr="featured_videos",
        ),

        # Featured ride images
        Prefetch(
            "media",
            queryset=image_media,
            to_attr="featured_images",
        ),

        # Featured ride prices
        Prefetch(
            "prices",
            queryset=current_prices,
            to_attr="featured_prices",
        ),

    )
    .order_by("-created_at")
)


   # =========================================
# SUPERMAN RIDE
# =========================================

    superman_ride = (
        Ride.objects
       .filter(
        slug="super-man",
        is_active=True,
       )
       .first()
    )


# =========================================
# SUPERMAN CURRENT PRICE
# =========================================

    superman_price = None

    if superman_ride:

      superman_price = (
        RidePrice.objects
        .filter(
            ride=superman_ride,
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        )
        .order_by("price")
        .first()
    )


    # -----------------------------------------
    # TESTIMONIALS
    # -----------------------------------------

    testimonials = (
        Testimonial.objects
        .all()
        .order_by("-created_at")
    )


    # -----------------------------------------
    # BLOGS
    # -----------------------------------------

    blogs = (
        Blog.objects
        .all()
        .order_by("-created_at")[:3]
    )

    today = timezone.now().date()

    active_offers = (
    Offer.objects
    .filter(
        is_active=True,
        start_date__lte=today,
        end_date__gte=today,
    )
    .exclude(
        banner_image=""
    )
    .filter(
        banner_image__isnull=False
    )
    .order_by("-created_at")
    )


    return render(
        request,
        "frontend/index.html",
        {
            "rides": rides,
            "featured_rides": featured_rides,
            "gallery_videos": gallery_videos,
            "gallery_images": gallery_images,
            "testimonials": testimonials,
            "blogs": blogs,
            "active_offers": active_offers,
             # Superman
            "superman_ride": superman_ride,
            "superman_price": superman_price,
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

    today = date.today()

    # =====================================================
    # RIDE
    # =====================================================

    ride = get_object_or_404(
        Ride,
        slug=slug,
        is_active=True,
    )


    # =====================================================
    # ALL RIDE IMAGES
    # =====================================================

    ride_images = (
        RideMedia.objects
        .filter(
            ride=ride,
            media_type="image",
            image__isnull=False,
        )
        .exclude(image="")
        .order_by("created_at")
    )


    # =====================================================
    # HERO IMAGE
    # First uploaded image only
    # =====================================================

    hero_image = ride_images.first()


    # =====================================================
    # GALLERY IMAGES
    # All images except hero image
    # =====================================================

    if hero_image:

        gallery_images = ride_images.exclude(
            pk=hero_image.pk
        )

    else:

        gallery_images = RideMedia.objects.none()


    # =====================================================
    # RIDE VIDEOS
    # =====================================================

    ride_videos = (
        RideMedia.objects
        .filter(
            ride=ride,
            media_type="video",
            video__isnull=False,
        )
        .exclude(video="")
        .order_by("created_at")
    )


    # =====================================================
    # CURRENT PRICE
    # =====================================================

    current_price = (
        RidePrice.objects
        .filter(
            ride=ride,
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        )
        .order_by("-start_date")
        .first()
    )


    return render(
        request,
        "frontend/ride-detail.html",
        {
            "ride": ride,
            "hero_image": hero_image,
            "gallery_images": gallery_images,
            "ride_videos": ride_videos,
            "current_price": current_price,
        },
    )





from django.db.models import Prefetch
from django.utils import timezone

from .models import (
    Ride,
    RideMedia,
    RidePrice,
    Offer,
)

from django.db.models import Prefetch
from django.shortcuts import render
from django.utils import timezone

from .models import (
    Offer,
    Ride,
    RideMedia,
    RidePrice,
)







SUCCESSFUL_BOOKING_STATUSES = [
    "confirmed",
    "checked_in",
]


def _booking_user_profile(request):

    # Preferred session key
    profile_id = (
        request.session.get(
            "user_profile_id"
        )
        or
        request.session.get(
            "user_id"
        )
    )

    if profile_id:

        profile = (
            UserProfile.objects
            .filter(
                id=profile_id
            )
            .first()
        )

        if profile:
            return profile


    # Optional fallback for older OTP code
    phone = (
        request.session.get(
            "user_phone"
        )
        or
        request.session.get(
            "phone"
        )
    )

    if phone:

        return (
            UserProfile.objects
            .filter(
                phone=str(phone).strip(),
                phone_verified=True,
            )
            .first()
        )


    return None



def _identity_booking_queryset(
    *,
    user_profile=None,
    customer_phone="",
):

    bookings = (
        Booking.objects
        .filter(
            status__in=[
                "confirmed",
                "checked_in",
            ]
        )
    )


    # =====================================================
    # USER PROFILE ALREADY KNOWN
    # =====================================================

    if user_profile:

        return bookings.filter(
            user=user_profile
        )


    # =====================================================
    # FIND USER BY UNIQUE MOBILE NUMBER
    # =====================================================

    if customer_phone:

        profile = (
            UserProfile.objects
            .filter(
                phone=customer_phone
            )
            .first()
        )


        if profile:

            return bookings.filter(
                user=profile
            )


    return Booking.objects.none()


def bookings(request):

    today = timezone.localdate()


    # =====================================================
    # STATIC PARTICIPANT WEIGHT RANGES
    # =====================================================

    weight_ranges = [

        {
            "key":
                key,

            "label":
                data["label"],

            "min_weight":
                data["min_weight"],

            "max_weight":
                data["max_weight"],
        }

        for key, data
        in WEIGHT_RANGES.items()
    ]


    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "frontend/booking.html",
        {
            "weight_ranges":
                weight_ranges,

            "today":
                today,
        },
    )




@require_GET
def booking_options_for_date(request):

    try:

        # =====================================================
        # 1. BOOKING DATE
        # =====================================================

        booking_date_raw = (
            request.GET.get(
                "date",
                ""
            )
            .strip()
        )


        booking_date = parse_date(
            booking_date_raw
        )


        if not booking_date:

            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        "Please select a valid visit date."
                    ),
                    "rides": [],
                },
                status=400,
            )


        if (
            booking_date
            <
            timezone.localdate()
        ):

            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        "The visit date cannot be in the past."
                    ),
                    "rides": [],
                },
                status=400,
            )


        # =====================================================
        # 2. ACTIVE RIDES
        # =====================================================

        rides = (
            Ride.objects
            .filter(
                is_active=True
            )
            .order_by(
                "name"
            )
        )


        ride_results = []


        # =====================================================
        # 3. PROCESS EACH RIDE
        # =====================================================

        for ride in rides:


            # =================================================
            # PRICE VALID FOR SELECTED DATE
            # =================================================

            ride_price = (
                RidePrice.objects
                .filter(
                    ride=ride,
                    is_active=True,
                    start_date__lte=
                        booking_date,
                    end_date__gte=
                        booking_date,
                )
                .order_by(
                    "-start_date",
                    "-created_at",
                )
                .first()
            )


            # No valid price = do not show ride
            if not ride_price:
                continue


            # =================================================
            # RIDE IMAGE
            # =================================================

            ride_image = (
                RideMedia.objects
                .filter(
                    ride=ride,
                    media_type="image",
                    image__isnull=False,
                )
                .exclude(
                    image=""
                )
                .order_by(
                    "-created_at"
                )
                .first()
            )


            image_url = ""


            if (
                ride_image
                and
                ride_image.image
            ):

                try:

                    image_url = (
                        ride_image.image.url
                    )

                except Exception:

                    image_url = ""


            # =================================================
            # OFFERS VALID FOR SELECTED DATE + RIDE
            # =================================================

            offers = (
                Offer.objects
                .filter(
                    rides=ride,
                    is_active=True,
                    start_date__lte=
                        booking_date,
                    end_date__gte=
                        booking_date,
                )
                .order_by(
                    "-created_at"
                )
            )


            offer_results = []


            # =================================================
            # PROCESS OFFERS
            # =================================================

            for offer in offers:


                # ---------------------------------------------
                # WEEKDAY OFFER
                # ---------------------------------------------

                if (
                    offer.offer_type
                    ==
                    "weekday"
                    and
                    booking_date.weekday()
                    >=
                    5
                ):

                    continue


                # ---------------------------------------------
                # EARLY BIRD OFFER
                # ---------------------------------------------

                if (
                    offer.offer_type
                    ==
                    "early_bird"
                ):

                    required_days = (
                        getattr(
                            offer,
                            "minimum_advance_days",
                            0
                        )
                        or
                        0
                    )


                    advance_days = (
                        booking_date
                        -
                        timezone.localdate()
                    ).days


                    if (
                        advance_days
                        <
                        required_days
                    ):

                        continue


                # =============================================
                # OFFER JSON
                # =============================================

                offer_results.append(
                    {

                        "id":
                            offer.id,

                        "title":
                            offer.title,

                        "description":
                            offer.description
                            or
                            "",

                        "offer_type":
                            offer.offer_type,

                        "discount_value":
                            str(
                                offer.discount_value
                                or
                                Decimal("0.00")
                            ),

                        "discount_label":
                            getattr(
                                offer,
                                "discount_label",
                                ""
                            )
                            or
                            "",

                        "minimum_participants":
                            getattr(
                                offer,
                                "minimum_participants",
                                1
                            )
                            or
                            1,

                        "minimum_booking_amount":
                            str(
                                getattr(
                                    offer,
                                    "minimum_booking_amount",
                                    Decimal("0.00")
                                )
                                or
                                Decimal("0.00")
                            ),

                        "maximum_discount":
                            (
                                str(
                                    offer.maximum_discount
                                )
                                if
                                getattr(
                                    offer,
                                    "maximum_discount",
                                    None
                                )
                                is not None
                                else
                                "0"
                            ),

                        "buy_quantity":
                            getattr(
                                offer,
                                "buy_quantity",
                                0
                            )
                            or
                            0,

                        "free_quantity":
                            getattr(
                                offer,
                                "free_quantity",
                                0
                            )
                            or
                            0,

                        "coupon_required":
                            bool(
                                getattr(
                                    offer,
                                    "coupon_required",
                                    False
                                )
                                or
                                offer.offer_type
                                ==
                                "coupon"
                            ),

                        "coupon_code":
                            getattr(
                                offer,
                                "coupon_code",
                                ""
                            )
                            or
                            "",

                        "first_booking_only":
                            bool(
                                getattr(
                                    offer,
                                    "first_booking_only",
                                    False
                                )
                            ),

                        "minimum_advance_days":
                            getattr(
                                offer,
                                "minimum_advance_days",
                                0
                            )
                            or
                            0,

                        "start_date":
                            offer.start_date.isoformat(),

                        "end_date":
                            offer.end_date.isoformat(),
                    }
                )


            # =================================================
            # RIDE JSON
            # =================================================

            ride_results.append(
                {

                    "id":
                        ride.id,

                    "name":
                        ride.name,

                    "description":
                        ride.description
                        or
                        "",

                    "image":
                        image_url,


                    # =========================================
                    # SLOT SETTINGS
                    # =========================================

                    "capacity_per_slot":
                        ride.capacity_per_slot,

                    "slot_duration_minutes":
                        ride.slot_duration_minutes,


                    # =========================================
                    # PRICE
                    # =========================================

                    "price_id":
                        ride_price.id,

                    "price":
                        str(
                            ride_price.price
                        ),


                    # =========================================
                    # OFFERS
                    # =========================================

                    "offers":
                        offer_results,
                }
            )


        # =====================================================
        # 4. SUCCESS RESPONSE
        # =====================================================

        return JsonResponse(
            {

                "success":
                    True,

                "date":
                    booking_date.isoformat(),

                "rides":
                    ride_results,
            }
        )


    except Exception as error:

        print(
            "\n================================"
        )

        print(
            "BOOKING OPTIONS ERROR"
        )

        print(
            "TYPE:",
            type(error).__name__
        )

        print(
            "ERROR:",
            repr(error)
        )

        print(
            "================================\n"
        )


        return JsonResponse(
            {
                "success":
                    False,

                "message":
                    (
                        "Unable to load rides for "
                        "the selected date. "
                        "Please try again."
                    ),

                "rides":
                    [],
            },
            status=500,
        )





@require_GET
def booking_slot_availability(request):

    try:

        # =====================================================
        # 1. READ REQUEST DATA
        # =====================================================

        booking_date_raw = (
            request.GET.get(
                "date",
                ""
            )
            .strip()
        )

        ride_id_raw = (
            request.GET.get(
                "ride_id",
                ""
            )
            .strip()
        )

        quantity_raw = (
            request.GET.get(
                "quantity",
                ""
            )
            .strip()
        )


        # =====================================================
        # 2. VALIDATE DATE
        # =====================================================

        booking_date = parse_date(
            booking_date_raw
        )


        if not booking_date:

            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        "Please select a valid visit date."
                    ),
                    "slots": [],
                },
                status=400,
            )


        if (
            booking_date
            <
            timezone.localdate()
        ):

            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        "The visit date cannot be in the past."
                    ),
                    "slots": [],
                },
                status=400,
            )


        # =====================================================
        # 3. VALIDATE RIDE
        # =====================================================

        try:

            ride_id = int(
                ride_id_raw
            )

        except (
            TypeError,
            ValueError
        ):

            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        "Please select a valid ride."
                    ),
                    "slots": [],
                },
                status=400,
            )


        ride = (
            Ride.objects
            .filter(
                id=ride_id,
                is_active=True,
            )
            .first()
        )


        if not ride:

            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        "The selected ride is not available."
                    ),
                    "slots": [],
                },
                status=404,
            )


        # =====================================================
        # 4. VALIDATE QUANTITY
        # =====================================================

        try:

            quantity = int(
                quantity_raw
            )

        except (
            TypeError,
            ValueError
        ):

            quantity = 0


        if quantity <= 0:

            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        "Participant quantity must be "
                        "greater than zero."
                    ),
                    "slots": [],
                },
                status=400,
            )


        # =====================================================
        # 5. GET RAW SLOT AVAILABILITY
        # =====================================================

        slot_data = get_available_slots(
            ride=ride,
            booking_date=booking_date,
        )


        # =====================================================
        # 6. CHECK EACH SLOT AS POSSIBLE START
        # =====================================================

        result_slots = []


        for slot in slot_data:

            allocation_result = (
                allocate_participants_from_start_slot(
                    ride=ride,
                    booking_date=booking_date,
                    requested_quantity=quantity,
                    selected_start_time=
                        slot["start_time"],
                )
            )


            allocations = []


            if allocation_result[
                "available"
            ]:

                for allocation in (
                    allocation_result[
                        "allocations"
                    ]
                ):

                    allocations.append(
                        {
                            "start_time":
                                allocation[
                                    "start_time"
                                ].strftime(
                                    "%H:%M"
                                ),

                            "end_time":
                                allocation[
                                    "end_time"
                                ].strftime(
                                    "%H:%M"
                                ),

                            "participant_count":
                                allocation[
                                    "participant_count"
                                ],
                        }
                    )


            # =================================================
            # DISPLAY LABEL
            # =================================================

            start_label = (
                slot[
                    "start_time"
                ].strftime(
                    "%I:%M %p"
                )
            )

            end_label = (
                slot[
                    "end_time"
                ].strftime(
                    "%I:%M %p"
                )
            )


            result_slots.append(
                {
                    "start_time":
                        slot[
                            "start_time"
                        ].strftime(
                            "%H:%M"
                        ),

                    "end_time":
                        slot[
                            "end_time"
                        ].strftime(
                            "%H:%M"
                        ),

                    "start_label":
                        start_label,

                    "end_label":
                        end_label,

                    "capacity":
                        slot[
                            "capacity"
                        ],

                    "booked":
                        slot[
                            "booked"
                        ],

                    "remaining":
                        slot[
                            "remaining"
                        ],

                    "available":
                        allocation_result[
                            "available"
                        ],

                    "allocations":
                        allocations,
                }
            )


        # =====================================================
        # 7. CHECK IF ANY START TIME CAN TAKE GROUP
        # =====================================================

        has_available_slot = any(
            slot["available"]
            for slot
            in result_slots
        )


        # =====================================================
        # 8. RESPONSE
        # =====================================================

        return JsonResponse(
            {
                "success": True,

                "date":
                    booking_date.isoformat(),

                "ride": {
                    "id":
                        ride.id,

                    "name":
                        ride.name,

                    "capacity_per_slot":
                        ride.capacity_per_slot,

                    "slot_duration_minutes":
                        ride.slot_duration_minutes,
                },

                "quantity":
                    quantity,

                "has_available_slot":
                    has_available_slot,

                "slots":
                    result_slots,
            }
        )


    except Exception as error:

        print(
            "\n================================"
        )

        print(
            "BOOKING SLOT AVAILABILITY ERROR"
        )

        print(
            "TYPE:",
            type(error).__name__
        )

        print(
            "ERROR:",
            repr(error)
        )

        print(
            "================================\n"
        )


        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Unable to load ride availability. "
                    "Please try again."
                ),
                "slots": [],
            },
            status=500,
        )




    
def _booking_user_profile(request):
    """
    Return the UserProfile connected to the current visitor when available.
    Booking.user is nullable, so guest booking can still continue.
    """

    if getattr(request, "user", None) and request.user.is_authenticated:

        profile = getattr(
            request.user,
            "userprofile",
            None,
        )

        if profile:
            return profile

    profile_id = request.session.get(
        "user_id"
    )

    if profile_id:

        return (
            UserProfile.objects
            .filter(
                pk=profile_id
            )
            .first()
        )

    return None


def _calculate_offer_discount(
    *,
    offer,
    ride,
    booking_date,
    quantity,
    participant_subtotal,
    subtotal_before_discount,
    user_profile=None,
    customer_phone="",
    strict_identity=False,
    check_customer_history=True,
):

    ZERO = Decimal("0.00")


    if not offer:

        return ZERO, ""


    # =====================================================
    # ACTIVE / DATE
    # =====================================================

    if not offer.is_active:

        return (
            ZERO,
            "This offer is inactive."
        )


    if not (
        offer.start_date
        <=
        booking_date
        <=
        offer.end_date
    ):

        return (
            ZERO,
            (
                "This offer is not valid "
                "for the selected visit date."
            )
        )


    # =====================================================
    # MINIMUM PARTICIPANTS
    # =====================================================

    minimum_participants = (
        offer.minimum_participants
        or
        1
    )


    if quantity < minimum_participants:

        remaining = (
            minimum_participants
            -
            quantity
        )

        return (
            ZERO,
            (
                f"Add {remaining} more rider"
                f"{'' if remaining == 1 else 's'} "
                f'to unlock "{offer.title}".'
            )
        )


    # =====================================================
    # MINIMUM BOOKING AMOUNT
    # =====================================================

    minimum_amount = (
        offer.minimum_booking_amount
        or
        ZERO
    )


    if subtotal_before_discount < minimum_amount:

        difference = (
            minimum_amount
            -
            subtotal_before_discount
        )

        return (
            ZERO,
            (
                f"Add ₹{difference:.2f} more "
                f'to unlock "{offer.title}".'
            )
        )


    # =====================================================
    # CUSTOMER HISTORY
    #
    # During booking preview we can disable this check.
    # During payment validation this must be enabled.
    # =====================================================

    if check_customer_history:

        identity_bookings = (
            _identity_booking_queryset(
                user_profile=
                    user_profile,

                customer_phone=
                    customer_phone
            )
        )


        has_identity = bool(
            user_profile
            or
            (customer_phone or "").strip()
        )


        # =================================================
        # MAX USES PER CUSTOMER (SCOPED TO THIS RIDE)
        # =================================================

        if offer.max_uses_per_user:

            if (
                strict_identity
                and
                not has_identity
            ):

                return (
                    ZERO,
                    (
                        "Customer identity is required "
                        "to use this offer."
                    )
                )


            if has_identity:

                already_used = (
                    BookingRideItem.objects
                    .filter(
                        booking__in=identity_bookings,
                        offer=offer,
                        ride=ride,
                    )
                    .count()
                )


                if (
                    already_used
                    >=
                    offer.max_uses_per_user
                ):

                    return (
                        ZERO,
                        (
                            f'You have already used '
                            f'"{offer.title}" on '
                            f'"{ride.name}". '
                            f"This offer can be used only "
                            f"{offer.max_uses_per_user} "
                            f"time(s) per customer for this ride."
                        )
                    )


        # =================================================
        # FIRST BOOKING
        # =================================================

        if (
            offer.first_booking_only
            or
            offer.offer_type
            ==
            "first_booking"
        ):

            if (
                strict_identity
                and
                not has_identity
            ):

                return (
                    ZERO,
                    (
                        "Customer details are required "
                        "to verify this offer."
                    )
                )


            if (
                has_identity
                and
                identity_bookings.exists()
            ):

                return (
                    ZERO,
                    (
                        "This offer is available for "
                        "your first successful booking only."
                    )
                )


    # =====================================================
    # WEEKDAY
    # =====================================================

    if (
        offer.offer_type
        ==
        "weekday"
    ):

        # Saturday=5, Sunday=6
        if booking_date.weekday() >= 5:

            return (
                ZERO,
                (
                    "This offer is available "
                    "on weekdays only."
                )
            )


    # =====================================================
    # EARLY BIRD
    # =====================================================

    if (
        offer.offer_type
        ==
        "early_bird"
    ):

        advance_days = (
            booking_date
            -
            timezone.localdate()
        ).days


        required_days = (
            offer.minimum_advance_days
            or
            0
        )


        if advance_days < required_days:

            return (
                ZERO,
                (
                    f"This Early Bird offer requires "
                    f"booking at least "
                    f"{required_days} day(s) "
                    f"before the visit."
                )
            )


    # =====================================================
    # BIRTHDAY
    # Uses birthday month
    # =====================================================

    if (
        offer.offer_type
        ==
        "birthday"
    ):

        if not user_profile:

            return (
                ZERO,
                (
                    "Please log in with your verified "
                    "account to use the Birthday Offer."
                )
            )


        if not user_profile.date_of_birth:

            return (
                ZERO,
                (
                    "Please add your date of birth "
                    "to your profile."
                )
            )


        if (
            user_profile.date_of_birth.month
            !=
            booking_date.month
        ):

            return (
                ZERO,
                (
                    "Birthday Offer is available "
                    "during your birthday month."
                )
            )


    # =====================================================
    # BUY X GET Y
    # =====================================================

    if (
        offer.offer_type
        ==
        "buy_x_get_y"
    ):

        if (
            not offer.buy_quantity
            or
            not offer.free_quantity
        ):

            return (
                ZERO,
                (
                    "This Buy X Get Y offer "
                    "is not configured correctly."
                )
            )


        group_size = (
            offer.buy_quantity
            +
            offer.free_quantity
        )


        if quantity < group_size:

            remaining = (
                group_size
                -
                quantity
            )

            return (
                ZERO,
                (
                    f"Add {remaining} more rider"
                    f"{'' if remaining == 1 else 's'} "
                    f"to unlock Buy "
                    f"{offer.buy_quantity} "
                    f"Get "
                    f"{offer.free_quantity} Free."
                )
            )


        completed_groups = (
            quantity
            //
            group_size
        )


        free_riders = (
            completed_groups
            *
            offer.free_quantity
        )


        price_per_person = (
            participant_subtotal
            /
            Decimal(quantity)
        )


        discount = (
            price_per_person
            *
            Decimal(free_riders)
        )


    # =====================================================
    # FIXED
    # =====================================================

    elif (
        offer.offer_type
        ==
        "fixed"
    ):

        discount = (
            offer.discount_value
            or
            ZERO
        )


    # =====================================================
    # PERCENTAGE TYPES
    # =====================================================

    else:

        discount = (
            subtotal_before_discount
            *
            (
                offer.discount_value
                or
                ZERO
            )
            /
            Decimal("100")
        )


    # =====================================================
    # MAXIMUM DISCOUNT
    # =====================================================

    if (
        offer.maximum_discount
        is not None
    ):

        discount = min(
            discount,
            offer.maximum_discount,
        )


    # Never exceed subtotal
    discount = min(
        max(
            discount,
            ZERO
        ),
        subtotal_before_discount,
    )


    if discount <= ZERO:

        return (
            ZERO,
            (
                "This offer does not produce "
                "a valid discount."
            )
        )


    return (
        discount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        ),
        "",
    )




def booking_review(request):

    ZERO = Decimal("0.00")


    # =====================================================
    # HELPER — FAIL AND RETURN TO BOOKING PAGE
    # =====================================================

    def booking_fail(message):

        print("\n" + "=" * 70)
        print("BOOKING REVIEW FAILED")
        print("MESSAGE:", message)
        print("=" * 70 + "\n")

        messages.error(
            request,
            message
        )

        return redirect(
            "bookings"
        )


    # =====================================================
    # GET — SHOW EXISTING REVIEW SESSION
    # =====================================================

    if request.method == "GET":

        booking_data = (
            request.session.get(
                "pending_booking"
            )
        )

        if not booking_data:

            return booking_fail(
                "Your booking session has expired. "
                "Please start again."
            )


        items = (
            booking_data.get(
                "items",
                []
            )
            or
            []
        )

        if not items:

            return booking_fail(
                "No rides were found in your booking. "
                "Please start again."
            )


        return render(
            request,
            "frontend/booking_review.html",
            {
                "booking_data":
                    booking_data,

                "profile":
                    _booking_user_profile(
                        request
                    ),
            },
        )


    # =====================================================
    # ONLY POST IS ALLOWED AFTER THIS POINT
    # =====================================================

    if request.method != "POST":

        return redirect(
            "bookings"
        )


    # =====================================================
    # DEBUG — RAW POST
    # =====================================================

    print("\n" + "=" * 70)
    print("BOOKING REVIEW POST")
    print("POST DATA:", request.POST)
    print("=" * 70 + "\n")


    # =====================================================
    # 1. BOOKING DATE
    # =====================================================

    booking_date_raw = (
        request.POST.get(
            "booking_date",
            ""
        )
        .strip()
    )


    print(
        "BOOKING DATE RAW:",
        booking_date_raw
    )


    booking_date = parse_date(
        booking_date_raw
    )


    if not booking_date:

        return booking_fail(
            "Please select a valid visit date."
        )


    if (
        booking_date
        <
        timezone.localdate()
    ):

        return booking_fail(
            "The visit date cannot be in the past."
        )


    # =====================================================
    # 2. READ MULTI-RIDE JSON
    # =====================================================

    booking_items_raw = (
        request.POST.get(
            "booking_items_json",
            ""
        )
        .strip()
    )


    print(
        "BOOKING ITEMS RAW:",
        booking_items_raw
    )


    if not booking_items_raw:

        return booking_fail(
            "No ride information was received. "
            "Please add at least one ride."
        )


    # =====================================================
    # 3. PARSE JSON
    # =====================================================

    try:

        submitted_items = json.loads(
            booking_items_raw
        )

    except (
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ) as error:

        print(
            "JSON ERROR:",
            repr(error)
        )

        return booking_fail(
            "The booking information is invalid. "
            "Please select your rides again."
        )


    print(
        "PARSED BOOKING ITEMS:",
        submitted_items
    )


    if (
        not isinstance(
            submitted_items,
            list
        )
        or
        not submitted_items
    ):

        return booking_fail(
            "Please add at least one ride "
            "before continuing."
        )


    # =====================================================
    # 4. INITIAL VALUES
    # =====================================================

    validated_items = []

    used_ride_ids = set()

    total_quantity = 0

    booking_subtotal = ZERO

    booking_discount = ZERO

    booking_total = ZERO


    user_profile = (
        _booking_user_profile(
            request
        )
    )


    # =====================================================
    # 5. PROCESS EACH SELECTED RIDE
    # =====================================================

    for item_index, submitted_item in enumerate(
        submitted_items,
        start=1,
    ):

        print("\n" + "-" * 60)
        print(
            f"PROCESSING RIDE ITEM #{item_index}"
        )
        print(
            submitted_item
        )
        print("-" * 60)


        # =================================================
        # VALIDATE ITEM FORMAT
        # =================================================

        if not isinstance(
            submitted_item,
            dict
        ):

            return booking_fail(
                f"Ride #{item_index} contains "
                "invalid booking information."
            )


        # =================================================
        # RIDE ID
        # =================================================

        ride_id = (
            submitted_item.get(
                "rideId"
            )
        )


        if not ride_id:

            return booking_fail(
                f"Ride #{item_index} is invalid."
            )


        try:

            ride_id = int(
                ride_id
            )

        except (
            TypeError,
            ValueError,
        ):

            return booking_fail(
                f"Ride #{item_index} has "
                "an invalid ride ID."
            )


        # =================================================
        # PREVENT SAME RIDE TWICE
        # =================================================

        if ride_id in used_ride_ids:

            return booking_fail(
                "The same ride cannot be "
                "added more than once."
            )


        used_ride_ids.add(
            ride_id
        )


        # =================================================
        # FIND ACTIVE RIDE
        # =================================================

        ride = (
            Ride.objects
            .filter(
                id=ride_id,
                is_active=True,
            )
            .first()
        )


        if not ride:

            return booking_fail(
                "One of the selected rides "
                "is no longer available."
            )


        print(
            "RIDE:",
            ride.id,
            ride.name
        )


        # =================================================
        # FIND PRICE VALID FOR SELECTED DATE
        # =================================================

        ride_price = (
            RidePrice.objects
            .filter(
                ride=ride,
                is_active=True,
                start_date__lte=
                    booking_date,
                end_date__gte=
                    booking_date,
            )
            .order_by(
                "-start_date",
                "-created_at",
            )
            .first()
        )


        print(
            "RIDE PRICE:",
            ride_price
        )


        if not ride_price:

            return booking_fail(
                (
                    f"{ride.name} does not have "
                    f"a valid price for "
                    f"{booking_date.strftime('%d %b %Y')}."
                )
            )


        # =================================================
        # WEIGHT GROUPS
        # =================================================

        submitted_groups = (
            submitted_item.get(
                "weightGroups",
                []
            )
            or
            []
        )


        print(
            "SUBMITTED WEIGHT GROUPS:",
            submitted_groups
        )


        if not isinstance(
            submitted_groups,
            list
        ):

            return booking_fail(
                (
                    f"Invalid participant information "
                    f"for {ride.name}."
                )
            )


        if not submitted_groups:

            return booking_fail(
                (
                    f"Please add participant weight "
                    f"details for {ride.name}."
                )
            )


        validated_weight_groups = []

        used_range_keys = set()

        item_quantity = 0


        # =================================================
        # PROCESS WEIGHT GROUPS
        # =================================================

        for group_index, group in enumerate(
            submitted_groups,
            start=1,
        ):

            if not isinstance(
                group,
                dict
            ):

                return booking_fail(
                    (
                        f"Invalid participant information "
                        f"for {ride.name}."
                    )
                )


            # =============================================
            # RANGE KEY
            # =============================================

            range_key = str(
                group.get(
                    "rangeKey",
                    ""
                )
                or
                ""
            ).strip()


            if not range_key:

                return booking_fail(
                    (
                        f"Please select a weight range "
                        f"for {ride.name}."
                    )
                )


            # =============================================
            # CHECK AGAINST SERVER WEIGHT RANGES
            # =============================================

            range_data = (
                WEIGHT_RANGES.get(
                    range_key
                )
            )


            if not range_data:

                print(
                    "INVALID RANGE KEY:",
                    range_key
                )

                print(
                    "AVAILABLE RANGE KEYS:",
                    list(
                        WEIGHT_RANGES.keys()
                    )
                )

                return booking_fail(
                    (
                        f"The selected weight range "
                        f"for {ride.name} is invalid."
                    )
                )


            # =============================================
            # DUPLICATE WEIGHT RANGE
            # =============================================

            if range_key in used_range_keys:

                return booking_fail(
                    (
                        f"The weight range "
                        f"{range_data['label']} "
                        f"was selected more than once "
                        f"for {ride.name}."
                    )
                )


            used_range_keys.add(
                range_key
            )


            # =============================================
            # PARTICIPANT COUNT
            # =============================================

            try:

                participant_count = int(
                    group.get(
                        "participantCount",
                        0
                    )
                )

            except (
                TypeError,
                ValueError,
            ):

                participant_count = 0


            if participant_count <= 0:

                return booking_fail(
                    (
                        f"Please enter at least one rider "
                        f"for {range_data['label']} "
                        f"in {ride.name}."
                    )
                )


            item_quantity += (
                participant_count
            )


            validated_weight_groups.append(
                {
                    "range_key":
                        range_key,

                    "label":
                        range_data[
                            "label"
                        ],

                    "min_weight":
                        range_data[
                            "min_weight"
                        ],

                    "max_weight":
                        range_data[
                            "max_weight"
                        ],

                    "participant_count":
                        participant_count,
                }
            )


        # =================================================
        # PARTICIPANT LIMIT
        # =================================================

        if item_quantity < 1:

            return booking_fail(
                (
                    f"Please add at least one "
                    f"participant for {ride.name}."
                )
            )


        if item_quantity > 10:

            return booking_fail(
                (
                    f"A maximum of 10 riders "
                    f"is allowed for {ride.name}."
                )
            )


        print(
            "ITEM QUANTITY:",
            item_quantity
        )

        print(
            "VALIDATED WEIGHT GROUPS:",
            validated_weight_groups
        )


        # =================================================
        # SELECTED START TIME / SERVER SLOT VALIDATION
        # =================================================

        selected_start_raw = str(
            submitted_item.get(
                "selectedStart",
                ""
            )
            or
            ""
        ).strip()


        print(
            "SELECTED START RAW:",
            selected_start_raw
        )


        if not selected_start_raw:

            return booking_fail(
                (
                    f"Please choose a start time "
                    f"for {ride.name}."
                )
            )


        try:

            selected_start_time = (
                datetime.strptime(
                    selected_start_raw,
                    "%H:%M"
                ).time()
            )

        except (
            TypeError,
            ValueError,
        ):

            return booking_fail(
                (
                    f"The selected start time "
                    f"for {ride.name} is invalid."
                )
            )


        allocation_result = (
            allocate_participants_from_start_slot(
                ride=ride,
                booking_date=booking_date,
                requested_quantity=item_quantity,
                selected_start_time=selected_start_time,
            )
        )


        print(
            "SLOT ALLOCATION RESULT:",
            allocation_result
        )


        if not allocation_result.get(
            "available",
            False,
        ):

            return booking_fail(
                (
                    f"The selected start time "
                    f"{selected_start_time.strftime('%I:%M %p')} "
                    f"for {ride.name} no longer has enough "
                    f"capacity for {item_quantity} rider"
                    f"{'' if item_quantity == 1 else 's'}. "
                    f"Please choose another start time."
                )
            )


        validated_slot_allocations = []


        for allocation in (
            allocation_result.get(
                "allocations",
                []
            )
            or
            []
        ):

            validated_slot_allocations.append(
                {
                    "start_time":
                        allocation[
                            "start_time"
                        ].strftime(
                            "%H:%M"
                        ),

                    "end_time":
                        allocation[
                            "end_time"
                        ].strftime(
                            "%H:%M"
                        ),

                    "start_label":
                        allocation[
                            "start_time"
                        ].strftime(
                            "%I:%M %p"
                        ),

                    "end_label":
                        allocation[
                            "end_time"
                        ].strftime(
                            "%I:%M %p"
                        ),

                    "participant_count":
                        allocation[
                            "participant_count"
                        ],
                }
            )


        if not validated_slot_allocations:

            return booking_fail(
                (
                    f"A valid slot allocation could not "
                    f"be created for {ride.name}. "
                    f"Please choose another start time."
                )
            )


        selected_start = (
            selected_start_time.strftime(
                "%H:%M"
            )
        )

        selected_start_label = (
            selected_start_time.strftime(
                "%I:%M %p"
            )
        )


        print(
            "VALIDATED START TIME:",
            selected_start
        )

        print(
            "VALIDATED SLOT ALLOCATIONS:",
            validated_slot_allocations
        )


        # =================================================
        # PRICE CALCULATION
        # =================================================

        price_per_person = Decimal(
            str(
                ride_price.price
            )
        )


        participant_subtotal = (
            price_per_person
            *
            Decimal(
                item_quantity
            )
        )


        item_subtotal = (
            participant_subtotal
        )


        print(
            "PRICE PER PERSON:",
            price_per_person
        )

        print(
            "ITEM SUBTOTAL:",
            item_subtotal
        )


        # =================================================
        # OFFER
        # =================================================

        selected_offer = None

        item_discount = ZERO


        offer_id = (
            submitted_item.get(
                "offerId"
            )
        )


        if (
            offer_id
            in
            {
                "",
                "0",
                0,
                "none",
                "null",
                None,
            }
        ):

            offer_id = None


        coupon_code = str(
            submitted_item.get(
                "couponCode",
                ""
            )
            or
            ""
        ).strip().upper()


        print(
            "OFFER ID:",
            offer_id
        )

        print(
            "COUPON CODE:",
            coupon_code
        )


        # =================================================
        # VALIDATE OFFER
        # =================================================

        if offer_id:

            try:

                offer_id = int(
                    offer_id
                )

            except (
                TypeError,
                ValueError,
            ):

                return booking_fail(
                    (
                        f"The selected offer for "
                        f"{ride.name} is invalid."
                    )
                )


            selected_offer = (
               Offer.objects
               .filter(
               id=offer_id,
               rides=ride,
               is_active=True,
               start_date__lte=booking_date,
               end_date__gte=booking_date,
               )
              .first()
            )      


            print(
                "SELECTED OFFER:",
                selected_offer
            )


            if not selected_offer:

                return booking_fail(
                    (
                        f"The selected offer is not "
                        f"available for {ride.name} "
                        f"on "
                        f"{booking_date.strftime('%d %b %Y')}."
                    )
                )


            # =============================================
            # COUPON VALIDATION
            # =============================================

            requires_coupon = (
                selected_offer.coupon_required
                or
                selected_offer.offer_type
                ==
                "coupon"
            )


            if requires_coupon:

                expected_code = (
                    selected_offer.coupon_code
                    or
                    ""
                ).strip().upper()


                if not coupon_code:

                    return booking_fail(
                        (
                            f"Please enter the coupon "
                            f"code for {ride.name}."
                        )
                    )


                if (
                    not expected_code
                    or
                    coupon_code
                    !=
                    expected_code
                ):

                    return booking_fail(
                        (
                            f"The coupon code entered "
                            f"for {ride.name} is invalid."
                        )
                    )


            # =============================================
            # SERVER-SIDE OFFER CALCULATION
            # =============================================

            (
    item_discount,
    offer_error,
) = _calculate_offer_discount(

    offer=
        selected_offer,
    ride=
        ride,    

    booking_date=
        booking_date,

    quantity=
        item_quantity,

    participant_subtotal=
        participant_subtotal,

    subtotal_before_discount=
        item_subtotal,

    user_profile=
        user_profile,

    strict_identity=
        False,

    # IMPORTANT:
    # Do not check previous customer bookings yet.
    # Customer information will be verified before payment.
    check_customer_history=
        False,
)


            if offer_error:

                return booking_fail(
                    (
                        f"{ride.name}: "
                        f"{offer_error}"
                    )
                )


        # =================================================
        # NORMALIZE DISCOUNT
        # =================================================

        item_discount = Decimal(
            str(
                item_discount
                or
                ZERO
            )
        )


        if item_discount < ZERO:

            item_discount = ZERO


        if item_discount > item_subtotal:

            item_discount = (
                item_subtotal
            )


        # =================================================
        # ITEM TOTAL
        # =================================================

        item_total = max(
            item_subtotal
            -
            item_discount,

            ZERO,
        )


        print(
            "ITEM DISCOUNT:",
            item_discount
        )

        print(
            "ITEM TOTAL:",
            item_total
        )


        # =================================================
        # SAVE VALIDATED ITEM
        # =================================================

        validated_items.append(
            {

                "ride_id":
                    ride.id,

                "ride_price_id":
                    ride_price.id,

                "ride_name":
                    ride.name,

                "quantity":
                    item_quantity,

                "weight_groups":
                    validated_weight_groups,

                "selected_start":
                    selected_start,

                "selected_start_label":
                    selected_start_label,

                "slot_allocations":
                    validated_slot_allocations,

                "price_per_person":
                    str(
                        price_per_person
                    ),

                "participant_subtotal":
                    str(
                        participant_subtotal
                    ),

                "subtotal":
                    str(
                        item_subtotal
                    ),

                "offer_id":
                    (
                        selected_offer.id
                        if selected_offer
                        else
                        None
                    ),

                "offer_title":
                    (
                        selected_offer.title
                        if selected_offer
                        else
                        ""
                    ),

                "offer_label":
                    (
                        selected_offer.discount_label
                        if selected_offer
                        else
                        ""
                    ),

                "coupon_code":
                    (
                        coupon_code
                        if selected_offer
                        else
                        ""
                    ),

                "discount_amount":
                    str(
                        item_discount
                    ),

                "total_amount":
                    str(
                        item_total
                    ),
            }
        )


        # =================================================
        # ADD TO BOOKING TOTALS
        # =================================================

        total_quantity += (
            item_quantity
        )

        booking_subtotal += (
            item_subtotal
        )

        booking_discount += (
            item_discount
        )

        booking_total += (
            item_total
        )


    # =====================================================
    # 6. FINAL VALIDATION
    # =====================================================

    if not validated_items:

        return booking_fail(
            "No valid rides were found "
            "in your booking."
        )


    if total_quantity <= 0:

        return booking_fail(
            "Please add at least one participant."
        )


    # =====================================================
    # 7. BUILD FINAL SESSION DATA
    # =====================================================

    booking_data = {

        "booking_date":
            booking_date.isoformat(),

        "items":
            validated_items,

        "quantity":
            total_quantity,

        "subtotal":
            str(
                booking_subtotal
            ),

        "discount_amount":
            str(
                booking_discount
            ),

        "total_amount":
            str(
                booking_total
            ),
    }


    # =====================================================
    # DEBUG FINAL DATA
    # =====================================================

    print("\n" + "=" * 70)
    print("BOOKING REVIEW SUCCESS")
    print("DATE:", booking_date)
    print(
        "NUMBER OF RIDES:",
        len(
            validated_items
        )
    )
    print(
        "TOTAL RIDERS:",
        total_quantity
    )
    print(
        "SUBTOTAL:",
        booking_subtotal
    )
    print(
        "DISCOUNT:",
        booking_discount
    )
    print(
        "TOTAL:",
        booking_total
    )
    print(
        "BOOKING DATA:",
        booking_data
    )
    print("=" * 70 + "\n")


    # =====================================================
    # 8. SAVE TO SESSION
    # =====================================================

    request.session[
        "pending_booking"
    ] = booking_data


    # Remove previous unfinished booking
    request.session.pop(
        "current_booking_id",
        None,
    )


    request.session.modified = True


    # =====================================================
    # 9. SHOW REVIEW PAGE
    # =====================================================

    return render(
        request,
        "frontend/booking_review.html",
        {
            "booking_data":
                booking_data,

            "profile":
                user_profile,
        },
    )



from django.http import JsonResponse
from django.views.decorators.http import require_POST


@require_POST
def booking_send_otp(request):

    # =====================================================
    # PHONE
    # =====================================================

    phone_number = (
        request.POST.get(
            "phone_number",
            ""
        )
        .strip()
    )


    if not phone_number:

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Please enter your mobile number."
                ),
            },
            status=400,
        )


    # =====================================================
    # VALIDATE INTERNATIONAL PHONE FORMAT
    #
    # Example:
    # +919633390345
    # =====================================================

    if not re.fullmatch(
        r"\+[1-9]\d{7,14}",
        phone_number,
    ):

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Please enter a valid mobile number."
                ),
            },
            status=400,
        )


    # =====================================================
    # IMPORTANT:
    # Any previous booking OTP verification becomes invalid
    # when a new OTP is requested.
    # =====================================================

    request.session.pop(
        "booking_verified_phone",
        None,
    )


    # =====================================================
    # SEND OTP
    # =====================================================

    try:

        send_otp(
            phone_number
        )

    except Exception as error:

        print(
            "BOOKING OTP SEND ERROR:",
            repr(error),
        )

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Unable to send OTP. "
                    "Please try again."
                ),
            },
            status=500,
        )


    return JsonResponse(
        {
            "success": True,
            "message": (
                "OTP sent successfully."
            ),
        }
    )


@require_POST
def booking_verify_otp(request):

    # =====================================================
    # PHONE + OTP
    # =====================================================

    phone_number = (
        request.POST.get(
            "phone_number",
            ""
        )
        .strip()
    )

    entered_otp = (
        request.POST.get(
            "otp",
            ""
        )
        .strip()
    )


    if not phone_number:

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Mobile number is missing."
                ),
            },
            status=400,
        )


    if (
        not entered_otp.isdigit()
        or
        len(entered_otp) != 6
    ):

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Please enter the 6-digit OTP."
                ),
            },
            status=400,
        )


    # =====================================================
    # VERIFY USING EXISTING OTP SYSTEM
    # =====================================================

    success, message = verify_otp(
        phone_number,
        entered_otp,
    )


    if not success:

        return JsonResponse(
            {
                "success": False,
                "message": message,
            },
            status=400,
        )


    # =====================================================
    # STORE VERIFIED EXACT PHONE IN SESSION
    # =====================================================

    request.session[
        "booking_verified_phone"
    ] = phone_number

    request.session.modified = True


    return JsonResponse(
        {
            "success": True,
            "message": (
                "Mobile number verified successfully."
            ),
        }
    )

    


def _validate_pending_booking_before_payment(
    request,
    *,
    customer_phone="",
    customer_email="",
):

    ZERO = Decimal("0.00")


    # =====================================================
    # 1. PENDING BOOKING SESSION
    # =====================================================

    booking_data = (
        request.session.get(
            "pending_booking"
        )
    )


    if not booking_data:

        return (
            None,
            "Your booking session has expired. "
            "Please start your booking again."
        )


    # =====================================================
    # 2. BOOKING DATE
    # =====================================================

    booking_date = parse_date(
        booking_data.get(
            "booking_date",
            ""
        )
    )


    if not booking_date:

        return (
            None,
            "The selected visit date is invalid."
        )


    if (
        booking_date
        <
        timezone.localdate()
    ):

        return (
            None,
            "The selected visit date is no longer valid."
        )


    # =====================================================
    # 3. MULTI-RIDE ITEMS
    # =====================================================

    items_data = (
        booking_data.get(
            "items",
            []
        )
        or
        []
    )


    if (
        not isinstance(
            items_data,
            list
        )
        or
        not items_data
    ):

        return (
            None,
            "No rides were found in your booking."
        )


    # =====================================================
    # 4. CUSTOMER IDENTITY
    #
    # Logged-in user:
    #     user_profile can identify customer.
    #
    # Guest:
    #     customer_phone can identify previous bookings.
    # =====================================================

    user_profile = (
        _booking_user_profile(
            request
        )
    )


    customer_phone = (
        customer_phone
        or
        ""
    ).strip()


    customer_email = (
        customer_email
        or
        ""
    ).strip()


    if not customer_phone:

        return (
            None,
            "Customer phone number is required "
            "to verify booking offers."
        )


    # =====================================================
    # 5. PREPARE FINAL TOTALS
    # =====================================================

    validated_items = []

    used_ride_ids = set()

    total_quantity = 0

    booking_subtotal = ZERO

    booking_discount = ZERO

    booking_total = ZERO


    # =====================================================
    # 6. VALIDATE EVERY RIDE
    # =====================================================

    for item_index, item_data in enumerate(
        items_data,
        start=1,
    ):


        # =================================================
        # ITEM FORMAT
        # =================================================

        if not isinstance(
            item_data,
            dict
        ):

            return (
                None,
                (
                    f"Adventure #{item_index} "
                    f"contains invalid booking data."
                )
            )


        # =================================================
        # RIDE ID
        # =================================================

        ride_id = (
            item_data.get(
                "ride_id"
            )
        )


        if not ride_id:

            return (
                None,
                (
                    f"Adventure #{item_index} "
                    f"is no longer valid."
                )
            )


        try:

            ride_id = int(
                ride_id
            )

        except (
            TypeError,
            ValueError,
        ):

            return (
                None,
                (
                    f"Adventure #{item_index} "
                    f"contains an invalid ride."
                )
            )


        # =================================================
        # PREVENT SAME RIDE TWICE
        # =================================================

        if ride_id in used_ride_ids:

            return (
                None,
                (
                    "The same ride cannot appear "
                    "more than once in one booking."
                )
            )


        used_ride_ids.add(
            ride_id
        )


        # =================================================
        # ACTIVE RIDE
        # =================================================

        ride = (
            Ride.objects
            .filter(
                id=ride_id,
                is_active=True,
            )
            .first()
        )


        if not ride:

            return (
                None,
                (
                    f"One of your selected rides "
                    f"is no longer available."
                )
            )


        # =================================================
        # RIDE PRICE
        #
        # Recheck exact price row saved during review.
        # =================================================

        ride_price_id = (
            item_data.get(
                "ride_price_id"
            )
        )


        ride_price = (
            RidePrice.objects
            .filter(
                id=ride_price_id,
                ride=ride,
                is_active=True,
                start_date__lte=
                    booking_date,
                end_date__gte=
                    booking_date,
            )
            .first()
        )


        if not ride_price:

            return (
                None,
                (
                    f"The price for {ride.name} "
                    f"is no longer valid for "
                    f"{booking_date.strftime('%d %b %Y')}."
                )
            )


        # =================================================
        # WEIGHT GROUPS
        # =================================================

        weight_groups_data = (
            item_data.get(
                "weight_groups",
                []
            )
            or
            []
        )


        if (
            not isinstance(
                weight_groups_data,
                list
            )
            or
            not weight_groups_data
        ):

            return (
                None,
                (
                    f"Participant weight information "
                    f"for {ride.name} is invalid."
                )
            )


        validated_weight_groups = []

        used_range_keys = set()

        item_quantity = 0


        # =================================================
        # VALIDATE WEIGHT GROUPS
        # =================================================

        for group in weight_groups_data:


            if not isinstance(
                group,
                dict
            ):

                return (
                    None,
                    (
                        f"Participant weight information "
                        f"for {ride.name} is invalid."
                    )
                )


            # =============================================
            # RANGE KEY
            # =============================================

            range_key = str(
                group.get(
                    "range_key",
                    ""
                )
                or
                ""
            ).strip()


            if not range_key:

                return (
                    None,
                    (
                        f"A participant weight range "
                        f"for {ride.name} is missing."
                    )
                )


            # =============================================
            # REBUILD RANGE FROM SERVER CONFIG
            # =============================================

            range_data = (
                WEIGHT_RANGES.get(
                    range_key
                )
            )


            if not range_data:

                return (
                    None,
                    (
                        f"One of the participant weight "
                        f"ranges for {ride.name} "
                        f"is no longer valid."
                    )
                )


            # =============================================
            # DUPLICATE RANGE
            # =============================================

            if range_key in used_range_keys:

                return (
                    None,
                    (
                        f"The same weight range cannot "
                        f"appear more than once for "
                        f"{ride.name}."
                    )
                )


            used_range_keys.add(
                range_key
            )


            # =============================================
            # PARTICIPANT COUNT
            # =============================================

            try:

                participant_count = int(
                    group.get(
                        "participant_count",
                        0
                    )
                )

            except (
                TypeError,
                ValueError,
            ):

                return (
                    None,
                    (
                        f"Participant quantity "
                        f"for {ride.name} is invalid."
                    )
                )


            if participant_count <= 0:

                return (
                    None,
                    (
                        f"Each selected weight range "
                        f"for {ride.name} must contain "
                        f"at least one rider."
                    )
                )


            item_quantity += (
                participant_count
            )


            # =============================================
            # SERVER-VALIDATED WEIGHT GROUP
            # =============================================

            validated_weight_groups.append(
                {

                    "range_key":
                        range_key,

                    "label":
                        range_data[
                            "label"
                        ],

                    "min_weight":
                        range_data[
                            "min_weight"
                        ],

                    "max_weight":
                        range_data[
                            "max_weight"
                        ],

                    "participant_count":
                        participant_count,
                }
            )


        # =================================================
        # QUANTITY LIMIT — PER RIDE
        # =================================================

        if (
            item_quantity < 1
            or
            item_quantity > 10
        ):

            return (
                None,
                (
                    f"{ride.name} must contain "
                    f"between 1 and 10 riders."
                )
            )


        # =================================================
        # VERIFY QUANTITY SAVED IN SESSION
        # =================================================

        try:

            session_item_quantity = int(
                item_data.get(
                    "quantity",
                    0
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            return (
                None,
                (
                    f"Participant quantity for "
                    f"{ride.name} is invalid."
                )
            )


        if (
            session_item_quantity
            !=
            item_quantity
        ):

            return (
                None,
                (
                    f"Participant quantity for "
                    f"{ride.name} has changed. "
                    f"Please review your booking again."
                )
            )


        # =================================================
        # SLOT REVALIDATION BEFORE PAYMENT
        # =================================================

        selected_start_raw = str(
            item_data.get(
                "selected_start",
                ""
            )
            or
            ""
        ).strip()


        if not selected_start_raw:

            return (
                None,
                (
                    f"No start time was found for "
                    f"{ride.name}. Please review "
                    f"your booking again."
                )
            )


        try:

            selected_start_time = (
                datetime.strptime(
                    selected_start_raw,
                    "%H:%M"
                ).time()
            )

        except (
            TypeError,
            ValueError,
        ):

            return (
                None,
                (
                    f"The selected start time for "
                    f"{ride.name} is invalid. "
                    f"Please review your booking again."
                )
            )


        allocation_result = (
            allocate_participants_from_start_slot(
                ride=ride,
                booking_date=booking_date,
                requested_quantity=item_quantity,
                selected_start_time=selected_start_time,
            )
        )


        if not allocation_result.get(
            "available",
            False,
        ):

            return (
                None,
                (
                    f"The selected start time "
                    f"{selected_start_time.strftime('%I:%M %p')} "
                    f"for {ride.name} is no longer available. "
                    f"Please select another time."
                )
            )


        validated_slot_allocations = []


        for allocation in (
            allocation_result.get(
                "allocations",
                []
            )
            or
            []
        ):

            validated_slot_allocations.append(
                {
                    "start_time":
                        allocation[
                            "start_time"
                        ].strftime(
                            "%H:%M"
                        ),

                    "end_time":
                        allocation[
                            "end_time"
                        ].strftime(
                            "%H:%M"
                        ),

                    "start_label":
                        allocation[
                            "start_time"
                        ].strftime(
                            "%I:%M %p"
                        ),

                    "end_label":
                        allocation[
                            "end_time"
                        ].strftime(
                            "%I:%M %p"
                        ),

                    "participant_count":
                        allocation[
                            "participant_count"
                        ],
                }
            )


        if not validated_slot_allocations:

            return (
                None,
                (
                    f"No valid slot allocation exists "
                    f"for {ride.name}."
                )
            )


        selected_start = (
            selected_start_time.strftime(
                "%H:%M"
            )
        )

        selected_start_label = (
            selected_start_time.strftime(
                "%I:%M %p"
            )
        )


        # =================================================
        # PRICE CALCULATION
        # =================================================

        price_per_person = Decimal(
            str(
                ride_price.price
            )
        )


        participant_subtotal = (
            price_per_person
            *
            Decimal(
                item_quantity
            )
        )


        item_subtotal = (
            participant_subtotal
        )


        # =================================================
        # OFFER
        # =================================================

        selected_offer = None

        item_discount = ZERO


        offer_id = (
            item_data.get(
                "offer_id"
            )
        )


        if (
            offer_id
            in
            {
                "",
                "0",
                0,
                "none",
                "null",
                None,
            }
        ):

            offer_id = None


        # =================================================
        # OFFER EXISTS
        # =================================================

        if offer_id:

            try:

                offer_id = int(
                    offer_id
                )

            except (
                TypeError,
                ValueError,
            ):

                return (
                    None,
                    (
                        f"The selected offer for "
                        f"{ride.name} is invalid."
                    )
                )


            selected_offer = (
              Offer.objects
             .filter(
             id=offer_id,
             rides=ride,
             is_active=True,
              start_date__lte=
              booking_date,
              end_date__gte=
               booking_date,
             )
             .first()
            )


            if not selected_offer:

                return (
                    None,
                    (
                        f"The selected offer for "
                        f"{ride.name} is no longer "
                        f"available."
                    )
                )


            # =================================================
            # COUPON
            # =================================================

            requires_coupon = (
                selected_offer.coupon_required
                or
                selected_offer.offer_type
                ==
                "coupon"
            )


            supplied_code = (
                item_data.get(
                    "coupon_code",
                    ""
                )
                or
                ""
            ).strip().upper()


            if requires_coupon:

                expected_code = (
                    selected_offer.coupon_code
                    or
                    ""
                ).strip().upper()


                if (
                    not supplied_code
                    or
                    not expected_code
                    or
                    supplied_code
                    !=
                    expected_code
                ):

                    return (
                        None,
                        (
                            f"The coupon for "
                            f"{ride.name} is invalid."
                        )
                    )


            # =================================================
            # FULL OFFER VALIDATION
            #
            # IMPORTANT:
            #
            # Now the review form has customer_phone.
            # Therefore NOW we check:
            #
            # - previous bookings
            # - first booking
            # - max uses per customer
            # - logged-in profile
            # - phone identity
            # =================================================

            (
                item_discount,
                offer_error,
            ) = _calculate_offer_discount(

                offer=
                    selected_offer,
                ride=
                    ride,    

                booking_date=
                    booking_date,

                quantity=
                    item_quantity,

                participant_subtotal=
                    participant_subtotal,

                subtotal_before_discount=
                    item_subtotal,

                user_profile=
                    user_profile,

                customer_phone=
                    customer_phone,

                strict_identity=
                    True,

                check_customer_history=
                    True,
            )


            if offer_error:

                return (
                    None,
                    (
                        f"{ride.name}: "
                        f"{offer_error}"
                    )
                )


        # =================================================
        # NORMALIZE DISCOUNT
        # =================================================

        item_discount = Decimal(
            str(
                item_discount
                or
                ZERO
            )
        )


        if item_discount < ZERO:

            item_discount = ZERO


        if (
            item_discount
            >
            item_subtotal
        ):

            item_discount = (
                item_subtotal
            )


        # =================================================
        # ITEM TOTAL
        # =================================================

        item_total = max(

            item_subtotal
            -
            item_discount,

            ZERO,
        )


        # =================================================
        # COMPARE WITH REVIEW SESSION
        #
        # This detects unexpected manipulation or changes.
        # =================================================

        try:

            session_price = Decimal(
                str(
                    item_data.get(
                        "price_per_person",
                        "0"
                    )
                )
            )


            session_subtotal = Decimal(
                str(
                    item_data.get(
                        "subtotal",
                        "0"
                    )
                )
            )


        except Exception:

            return (
                None,
                (
                    f"Price information for "
                    f"{ride.name} is invalid."
                )
            )


        if (
            session_price
            !=
            price_per_person
        ):

            return (
                None,
                (
                    f"The price for {ride.name} "
                    f"has changed. Please review "
                    f"your booking again."
                )
            )


        if (
            session_subtotal
            !=
            item_subtotal
        ):

            return (
                None,
                (
                    f"The subtotal for {ride.name} "
                    f"has changed. Please review "
                    f"your booking again."
                )
            )


        # =================================================
        # VALIDATED ITEM
        # =================================================

        validated_items.append(
            {

                "ride":
                    ride,

                "ride_id":
                    ride.id,

                "ride_price":
                    ride_price,

                "ride_price_id":
                    ride_price.id,

                "ride_name":
                    ride.name,

                "quantity":
                    item_quantity,

                "weight_groups":
                    validated_weight_groups,

                "selected_start":
                    selected_start,

                "selected_start_label":
                    selected_start_label,

                "slot_allocations":
                    validated_slot_allocations,

                "price_per_person":
                    price_per_person,

                "participant_subtotal":
                    participant_subtotal,

                "subtotal":
                    item_subtotal,

                "offer":
                    selected_offer,

                "offer_id":
                    (
                        selected_offer.id
                        if selected_offer
                        else
                        None
                    ),

                "offer_title":
                    (
                        selected_offer.title
                        if selected_offer
                        else
                        ""
                    ),

                "offer_label":
                    (
                        selected_offer.discount_label
                        if selected_offer
                        else
                        ""
                    ),

                "coupon_code":
                    (
                        supplied_code
                        if selected_offer
                        else
                        ""
                    ),

                "discount_amount":
                    item_discount,

                "total_amount":
                    item_total,
            }
        )


        # =================================================
        # BOOKING TOTALS
        # =================================================

        total_quantity += (
            item_quantity
        )


        booking_subtotal += (
            item_subtotal
        )


        booking_discount += (
            item_discount
        )


        booking_total += (
            item_total
        )


    # =====================================================
    # 7. FINAL BOOKING VALIDATION
    # =====================================================

    if not validated_items:

        return (
            None,
            "No valid rides remain in this booking."
        )


    if total_quantity <= 0:

        return (
            None,
            "The booking must contain at least one rider."
        )


    # =====================================================
    # VERIFY BOOKING-LEVEL SESSION TOTALS
    # =====================================================

    try:

        session_total_quantity = int(
            booking_data.get(
                "quantity",
                0
            )
        )


        session_subtotal = Decimal(
            str(
                booking_data.get(
                    "subtotal",
                    "0"
                )
            )
        )


    except Exception:

        return (
            None,
            "The booking totals are invalid. "
            "Please review your booking again."
        )


    if (
        session_total_quantity
        !=
        total_quantity
    ):

        return (
            None,
            (
                "The total number of participants "
                "has changed. Please review "
                "your booking again."
            )
        )


    if (
        session_subtotal
        !=
        booking_subtotal
    ):

        return (
            None,
            (
                "The booking subtotal has changed. "
                "Please review your booking again."
            )
        )


    # =====================================================
    # IMPORTANT:
    #
    # Discount can legitimately change here because
    # customer-history validation is performed NOW.
    #
    # Example:
    # Review preview showed First Booking discount,
    # but entered phone has already booked before.
    #
    # In that case _calculate_offer_discount() above
    # already returned an error, so payment is stopped.
    # =====================================================


    # =====================================================
    # 8. BUILD UPDATED SESSION DATA
    #
    # Store only JSON-serializable values in session.
    # =====================================================

    updated_session_items = []


    for item in validated_items:

        updated_session_items.append(
            {

                "ride_id":
                    item[
                        "ride_id"
                    ],

                "ride_price_id":
                    item[
                        "ride_price_id"
                    ],

                "ride_name":
                    item[
                        "ride_name"
                    ],

                "quantity":
                    item[
                        "quantity"
                    ],

                "weight_groups":
                    item[
                        "weight_groups"
                    ],

                "selected_start":
                    item[
                        "selected_start"
                    ],

                "selected_start_label":
                    item[
                        "selected_start_label"
                    ],

                "slot_allocations":
                    item[
                        "slot_allocations"
                    ],

                "price_per_person":
                    str(
                        item[
                            "price_per_person"
                        ]
                    ),

                "participant_subtotal":
                    str(
                        item[
                            "participant_subtotal"
                        ]
                    ),

                "subtotal":
                    str(
                        item[
                            "subtotal"
                        ]
                    ),

                "offer_id":
                    item[
                        "offer_id"
                    ],

                "offer_title":
                    item[
                        "offer_title"
                    ],

                "offer_label":
                    item[
                        "offer_label"
                    ],

                "coupon_code":
                    item[
                        "coupon_code"
                    ],

                "discount_amount":
                    str(
                        item[
                            "discount_amount"
                        ]
                    ),

                "total_amount":
                    str(
                        item[
                            "total_amount"
                        ]
                    ),
            }
        )


    updated_booking_data = {

        "booking_date":
            booking_date.isoformat(),

        "items":
            updated_session_items,

        "quantity":
            total_quantity,

        "subtotal":
            str(
                booking_subtotal
            ),

        "discount_amount":
            str(
                booking_discount
            ),

        "total_amount":
            str(
                booking_total
            ),
    }


    # =====================================================
    # UPDATE SESSION WITH FINAL SERVER CALCULATION
    # =====================================================

    request.session[
        "pending_booking"
    ] = updated_booking_data


    request.session.modified = True


    # =====================================================
    # DEBUG
    # =====================================================

    print("\n" + "=" * 70)

    print(
        "MULTI-RIDE PAYMENT VALIDATION SUCCESS"
    )

    print(
        "DATE:",
        booking_date
    )

    print(
        "RIDES:",
        len(
            validated_items
        )
    )

    print(
        "TOTAL RIDERS:",
        total_quantity
    )

    print(
        "SUBTOTAL:",
        booking_subtotal
    )

    print(
        "DISCOUNT:",
        booking_discount
    )

    print(
        "TOTAL:",
        booking_total
    )

    print("=" * 70 + "\n")


    # =====================================================
    # 9. FINAL RESULT
    # =====================================================

    return (
        {

            "booking_data":
                updated_booking_data,

            "booking_date":
                booking_date,

            "items":
                validated_items,

            "quantity":
                total_quantity,

            "subtotal":
                booking_subtotal,

            "discount_amount":
                booking_discount,

            "total_amount":
                booking_total,

            "user_profile":
                user_profile,

            "customer_phone":
                customer_phone,

            "customer_email":
                customer_email,
        },

        None,
    )



# =========================================================
# FIND OR CREATE CUSTOMER USER PROFILE DURING BOOKING
# =========================================================

def _get_or_create_booking_user_profile(
    request,
    *,
    customer_name,
    customer_email,
    customer_phone,
):

    # =====================================================
    # 1. FIND USER BY UNIQUE MOBILE NUMBER
    # =====================================================

    user_profile = (
        UserProfile.objects
        .filter(
            phone=customer_phone
        )
        .first()
    )


    # =====================================================
    # 2. CREATE USER IF MOBILE NUMBER DOES NOT EXIST
    #
    # The booking phone has already been OTP verified
    # before this function is called.
    # =====================================================

    if user_profile is None:

        user_profile = (
            UserProfile.objects.create(

                full_name=
                    customer_name,

                phone=
                    customer_phone,

                phone_verified=
                    True,
            )
        )

        return user_profile


    # =====================================================
    # 3. UPDATE EXISTING PROFILE
    # =====================================================

    changed_fields = []


    # =====================================================
    # NAME
    # =====================================================

    if (
        customer_name
        and
        user_profile.full_name
        !=
        customer_name
    ):

        user_profile.full_name = (
            customer_name
        )

        changed_fields.append(
            "full_name"
        )



    # =====================================================
    # PHONE VERIFIED
    #
    # This phone was verified through booking OTP.
    # =====================================================

    if not user_profile.phone_verified:

        user_profile.phone_verified = (
            True
        )

        changed_fields.append(
            "phone_verified"
        )


    # =====================================================
    # EMAIL
    # =====================================================

    if customer_email:

        email_belongs_to_other_user = (
            UserProfile.objects
            .filter(
                email__iexact=
                    customer_email
            )
            .exclude(
                pk=user_profile.pk
            )
            .exists()
        )


        if (
            not email_belongs_to_other_user
            and
            user_profile.email
            !=
            customer_email
        ):

            user_profile.email = (
                customer_email
            )

            changed_fields.append(
                "email"
            )


    # =====================================================
    # SAVE
    # =====================================================

    if changed_fields:

        changed_fields.append(
            "updated_at"
        )

        user_profile.save(
            update_fields=
                changed_fields
        )


    return user_profile


@transaction.atomic
def booking_confirm(request):

    # =====================================================
    # POST ONLY
    # =====================================================

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": "POST request required.",
            },
            status=405,
        )


    # =====================================================
    # CUSTOMER DETAILS
    # =====================================================

    customer_name = (
        request.POST.get(
            "customer_name",
            ""
        )
        .strip()
    )


    customer_email = (
        request.POST.get(
            "customer_email",
            ""
        )
        .strip()
    )


    customer_phone = (
        request.POST.get(
            "customer_phone",
            ""
        )
        .strip()
    )


    terms_accepted = (
        request.POST.get(
            "terms_accepted"
        )
        ==
        "1"
    )


    # =====================================================
    # CUSTOMER NAME
    # =====================================================

    if not customer_name:

        return JsonResponse(
            {
                "success": False,
                "message": "Please enter your full name.",
            },
            status=400,
        )


    # =====================================================
    # EMAIL
    # =====================================================

    try:

        validate_email(
            customer_email
        )

    except ValidationError:

        return JsonResponse(
            {
                "success": False,
                "message": "Please enter a valid email address.",
            },
            status=400,
        )


    # =====================================================
    # PHONE
    # =====================================================

    if not re.fullmatch(
        r"\+[1-9]\d{7,14}",
        customer_phone
    ):

        return JsonResponse(
            {
                "success": False,
                "message": "Please enter a valid mobile number.",
            },
            status=400,
        )

    # =====================================================
# MOBILE OTP VERIFICATION CHECK
# =====================================================

    verified_phone = (
        request.session.get(
        "booking_verified_phone",
        ""
    )
    or
    ""
    ).strip()


    if (
    not verified_phone
    or
    verified_phone != customer_phone
    ):

        return JsonResponse(
        {
            "success": False,
            "message": (
                "Please verify your mobile number "
                "with OTP before continuing."
            ),
        },
        status=400,
    )



    # =====================================================
    # TERMS
    # =====================================================

    if not terms_accepted:

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Please accept the terms "
                    "and conditions."
                ),
            },
            status=400,
        )


    # =====================================================
    # REVALIDATE COMPLETE MULTI-RIDE BOOKING
    #
    # This checks:
    #
    # - rides
    # - prices
    # - participants
    # - weight groups
    # - offers
    # - coupon
    # - customer history
    # - selected start time
    # - slot capacity
    # - final totals
    # =====================================================

    (
        validated,
        error_message,
    ) = _validate_pending_booking_before_payment(

        request,

        customer_phone=
            customer_phone,

        customer_email=
            customer_email,
    )


    if not validated:

        return JsonResponse(
            {
                "success": False,

                "message": (
                    error_message
                    or
                    "The booking could not be validated."
                ),
            },
            status=400,
        )


    # =====================================================
    # VALIDATED ITEMS
    # =====================================================

    validated_items = (
        validated.get(
            "items",
            []
        )
        or
        []
    )


    if not validated_items:

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "No valid rides were found "
                    "in this booking."
                ),
            },
            status=400,
        )


    # =====================================================
    # BOOKING DATE
    # =====================================================

    booking_date = (
        validated[
            "booking_date"
        ]
    )


    # =====================================================
    # FINAL TOTAL
    # =====================================================

    total_amount = (
        validated[
            "total_amount"
        ]
    )


    if (
        total_amount
        <=
        Decimal("0.00")
    ):

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "This booking has a zero payable "
                    "amount. Free bookings must be "
                    "handled separately."
                ),
            },
            status=400,
        )


    # =====================================================
    # RAZORPAY SETTINGS
    # =====================================================

    key_id = getattr(
        settings,
        "RAZORPAY_KEY_ID",
        ""
    )


    key_secret = getattr(
        settings,
        "RAZORPAY_KEY_SECRET",
        ""
    )


    if (
        not key_id
        or
        not key_secret
    ):

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Razorpay API keys "
                    "are not configured yet."
                ),
            },
            status=500,
        )


    # =====================================================
    # RAZORPAY CLIENT
    # =====================================================

    client = razorpay.Client(
        auth=(
            key_id,
            key_secret,
        )
    )


    # =====================================================
    # FINAL SESSION DATA
    # =====================================================

    booking_data = (
        validated[
            "booking_data"
        ]
    )


    # =====================================================
    # LOCK ALL SELECTED RIDES
    #
    # IMPORTANT:
    #
    # Availability checking alone is not enough.
    #
    # Two customers could select the last remaining seats
    # at almost the same moment.
    #
    # Lock every selected Ride row before doing the final
    # capacity calculation and creating held slots.
    #
    # Sort IDs to reduce deadlock risk for multi-ride
    # bookings.
    # =====================================================

    ride_ids = sorted(
        {
            int(
                item[
                    "ride_id"
                ]
            )
            for item
            in validated_items
        }
    )


    locked_rides = {
        ride.id: ride

        for ride in (
            Ride.objects
            .select_for_update()
            .filter(
                id__in=ride_ids,
                is_active=True,
            )
            .order_by(
                "id"
            )
        )
    }


    if (
        len(
            locked_rides
        )
        !=
        len(
            ride_ids
        )
    ):

        transaction.set_rollback(
            True
        )

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "One of the selected rides "
                    "is no longer available. "
                    "Please review your booking again."
                ),
            },
            status=409,
        )


    # =====================================================
    # FINAL SLOT CAPACITY CHECK WHILE RIDES ARE LOCKED
    #
    # Never trust slotAllocations stored in the browser
    # or even the previous session calculation.
    #
    # Recalculate from database NOW while the Ride rows
    # are locked.
    # =====================================================

    final_slot_allocations = {}


    for item in validated_items:

        ride = locked_rides[
            int(
                item[
                    "ride_id"
                ]
            )
        ]


        selected_start_raw = str(
            item.get(
                "selected_start",
                ""
            )
            or
            ""
        ).strip()


        if not selected_start_raw:

            transaction.set_rollback(
                True
            )

            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        f"No start time was found for "
                        f"{ride.name}. Please select "
                        f"the ride time again."
                    ),
                },
                status=409,
            )


        try:

            selected_start_time = (
                datetime.strptime(
                    selected_start_raw,
                    "%H:%M"
                ).time()
            )

        except (
            TypeError,
            ValueError,
        ):

            transaction.set_rollback(
                True
            )

            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        f"The selected start time "
                        f"for {ride.name} is invalid."
                    ),
                },
                status=409,
            )


        # =============================================
        # RECALCULATE CAPACITY
        # =============================================

        allocation_result = (
            allocate_participants_from_start_slot(
                ride=ride,
                booking_date=booking_date,
                requested_quantity=
                    item[
                        "quantity"
                    ],
                selected_start_time=
                    selected_start_time,
            )
        )


        if not allocation_result.get(
            "available",
            False,
        ):

            transaction.set_rollback(
                True
            )

            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        f"{ride.name} is no longer "
                        f"available at "
                        f"{selected_start_time.strftime('%I:%M %p')} "
                        f"for {item['quantity']} rider"
                        f"{'' if item['quantity'] == 1 else 's'}. "
                        f"Please choose another start time."
                    ),
                },
                status=409,
            )


        allocations = (
            allocation_result.get(
                "allocations",
                []
            )
            or
            []
        )


        if not allocations:

            transaction.set_rollback(
                True
            )

            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        f"No valid slot allocation "
                        f"could be created for "
                        f"{ride.name}."
                    ),
                },
                status=409,
            )


        # =============================================
        # EXTRA SAFETY:
        # Allocation quantity must equal ride quantity.
        # =============================================

        allocated_quantity = sum(
            int(
                allocation[
                    "participant_count"
                ]
            )
            for allocation
            in allocations
        )


        if (
            allocated_quantity
            !=
            int(
                item[
                    "quantity"
                ]
            )
        ):

            transaction.set_rollback(
                True
            )

            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        f"Unable to safely allocate "
                        f"all riders for {ride.name}. "
                        f"Please select the ride again."
                    ),
                },
                status=409,
            )


        final_slot_allocations[
            ride.id
        ] = allocations


        # Use the locked Ride object from this point.
        item[
            "ride"
        ] = ride


        print(
            "\n================================"
        )

        print(
            "FINAL SLOT CHECK SUCCESS"
        )

        print(
            "RIDE:",
            ride.name
        )

        print(
            "START:",
            selected_start_raw
        )

        print(
            "QUANTITY:",
            item[
                "quantity"
            ]
        )

        print(
            "ALLOCATIONS:",
            allocations
        )

        print(
            "================================\n"
        )


    # =====================================================
    # HOLD EXPIRY
    #
    # Customer gets 15 minutes to complete Razorpay.
    # =====================================================

    hold_expires_at = (
        timezone.now()
        +
        timedelta(
            minutes=15
        )
    )


    # =====================================================
    # FIND / CREATE CUSTOMER PROFILE
    # =====================================================

    try:

        user_profile = (
            _get_or_create_booking_user_profile(

                request,

                customer_name=
                    customer_name,

                customer_email=
                    customer_email,

                customer_phone=
                    customer_phone,
            )
        )

    except Exception as error:

        print(
            "\n================================"
        )

        print(
            "USER PROFILE ERROR"
        )

        print(
            "TYPE:",
            type(error).__name__
        )

        print(
            "ERROR:",
            repr(error)
        )

        print(
            "================================\n"
        )


        transaction.set_rollback(
            True
        )


        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Unable to prepare your customer "
                    "profile. Please try again."
                ),
            },
            status=500,
        )


    # =====================================================
    # FIRST ITEM
    #
    # TEMPORARY LEGACY COMPATIBILITY
    # =====================================================

    first_item = (
        validated_items[
            0
        ]
    )


    # =====================================================
    # CREATE PARENT BOOKING
    # =====================================================

    try:

        booking = Booking.objects.create(

            user=
                user_profile,

            customer_name=
                customer_name,

            customer_email=
                customer_email,

            customer_phone=
                customer_phone,


            # =============================================
            # ONE DATE FOR WHOLE BOOKING
            # =============================================

            booking_date=
                booking_date,


            # =============================================
            # TEMPORARY LEGACY TIME FIELD
            #
            # Store first ride selected start for older
            # code that may still display Booking.time_slot.
            # Per-ride slots remain source of truth.
            # =============================================

            time_slot=
                first_item.get(
                    "selected_start",
                    ""
                ),


            # =============================================
            # PARENT TOTALS
            # =============================================

            quantity=
                validated[
                    "quantity"
                ],

            subtotal=
                validated[
                    "subtotal"
                ],

            discount_amount=
                validated[
                    "discount_amount"
                ],

            total_amount=
                validated[
                    "total_amount"
                ],


            # =============================================
            # TEMPORARY LEGACY SINGLE-RIDE FIELDS
            # =============================================

            ride=
                first_item[
                    "ride"
                ],

            ride_price=
                first_item[
                    "ride_price"
                ],

            price_per_person=
                first_item[
                    "price_per_person"
                ],

            offer=
                first_item[
                    "offer"
                ],

            applied_coupon_code=
                first_item.get(
                    "coupon_code",
                    ""
                ),


            # =============================================
            # STATUS
            # =============================================

            status=
                "payment_pending",
        )


    except Exception as error:

        print(
            "\n================================"
        )

        print(
            "BOOKING CREATE ERROR"
        )

        print(
            "TYPE:",
            type(error).__name__
        )

        print(
            "ERROR:",
            repr(error)
        )

        print(
            "VALIDATED:",
            validated
        )

        print(
            "================================\n"
        )


        transaction.set_rollback(
            True
        )


        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Unable to create the booking. "
                    "Please try again."
                ),
            },
            status=500,
        )


    # =====================================================
    # CREATE BOOKING RIDE ITEMS
    #
    # AND CREATE TEMPORARY SLOT HOLDS.
    # =====================================================

    created_booking_items = []


    try:

        for item_index, item in enumerate(
            validated_items,
            start=1,
        ):

            ride = (
                item[
                    "ride"
                ]
            )


            # =============================================
            # CREATE BOOKING RIDE ITEM
            # =============================================

            booking_item = (
                BookingRideItem.objects.create(

                    booking=
                        booking,

                    ride=
                        ride,

                    ride_price=
                        item[
                            "ride_price"
                        ],

                    quantity=
                        item[
                            "quantity"
                        ],

                    price_per_person=
                        item[
                            "price_per_person"
                        ],

                    offer=
                        item[
                            "offer"
                        ],

                    applied_coupon_code=
                        item.get(
                            "coupon_code",
                            ""
                        ),

                    discount_amount=
                        item[
                            "discount_amount"
                        ],

                    subtotal=
                        item[
                            "subtotal"
                        ],

                    total_amount=
                        item[
                            "total_amount"
                        ],

                    status=
                        "booked",
                )
            )


            created_booking_items.append(
                booking_item
            )


            # =============================================
            # CREATE HELD SLOT ROWS
            #
            # IMPORTANT:
            # Use allocation_result generated on server
            # while Ride row was locked.
            # =============================================

            allocations = (
                final_slot_allocations.get(
                    ride.id,
                    []
                )
                or
                []
            )


            if not allocations:

                raise ValueError(
                    (
                        f"No final slot allocation "
                        f"exists for {ride.name}."
                    )
                )


            slot_objects = []


            for allocation in allocations:

                slot_objects.append(

                    BookingRideSlot(

                        booking_item=
                            booking_item,

                        slot_start_time=
                            allocation[
                                "start_time"
                            ],

                        slot_end_time=
                            allocation[
                                "end_time"
                            ],

                        participant_count=
                            allocation[
                                "participant_count"
                            ],

                        status=
                            "held",

                        hold_expires_at=
                            hold_expires_at,
                    )
                )


            BookingRideSlot.objects.bulk_create(
                slot_objects
            )


            # =============================================
            # VERIFY HELD QUANTITY
            # =============================================

            held_quantity = sum(
                slot.participant_count
                for slot
                in slot_objects
            )


            if (
                held_quantity
                !=
                booking_item.quantity
            ):

                raise ValueError(
                    (
                        f"Slot hold quantity mismatch "
                        f"for {ride.name}."
                    )
                )


            # =============================================
            # WEIGHT GROUPS FOR THIS RIDE
            # =============================================

            weight_group_objects = []


            for group in item[
                "weight_groups"
            ]:

                weight_group_objects.append(

                    BookingWeightGroup(

                        # =================================
                        # OLD PARENT RELATION
                        # =================================

                        booking=
                            booking,


                        # =================================
                        # NEW CORRECT RELATION
                        # =================================

                        booking_item=
                            booking_item,

                        range_key=
                            group[
                                "range_key"
                            ],

                        participant_count=
                            group[
                                "participant_count"
                            ],

                        min_weight=
                            group[
                                "min_weight"
                            ],

                        max_weight=
                            group[
                                "max_weight"
                            ],

                        label=
                            group[
                                "label"
                            ],
                    )
                )


            if weight_group_objects:

                BookingWeightGroup.objects.bulk_create(
                    weight_group_objects
                )


            print(
                (
                    f"BOOKING ITEM #{item_index} CREATED | "
                    f"Ride: {booking_item.ride.name} | "
                    f"Riders: {booking_item.quantity} | "
                    f"Slots: {len(slot_objects)} | "
                    f"Hold Until: {hold_expires_at} | "
                    f"Total: {booking_item.total_amount}"
                )
            )


    except Exception as error:

        print(
            "\n================================"
        )

        print(
            "BOOKING ITEM / SLOT HOLD CREATE ERROR"
        )

        print(
            "TYPE:",
            type(error).__name__
        )

        print(
            "ERROR:",
            repr(error)
        )

        print(
            "VALIDATED ITEMS:",
            validated_items
        )

        print(
            "================================\n"
        )


        transaction.set_rollback(
            True
        )


        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Unable to reserve the selected "
                    "ride times. Please choose your "
                    "rides again."
                ),
            },
            status=409,
        )


    # =====================================================
    # VERIFY CHILD ITEMS WERE CREATED
    # =====================================================

    if (
        len(
            created_booking_items
        )
        !=
        len(
            validated_items
        )
    ):

        transaction.set_rollback(
            True
        )


        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Not all selected rides could "
                    "be saved. Please try again."
                ),
            },
            status=500,
        )


    # =====================================================
    # VERIFY SLOT HOLDS EXIST FOR EVERY ITEM
    # =====================================================

    for booking_item in created_booking_items:

        held_count = (
            BookingRideSlot.objects
            .filter(
                booking_item=
                    booking_item,

                status=
                    "held",

                hold_expires_at__gt=
                    timezone.now(),
            )
            .count()
        )


        if held_count <= 0:

            transaction.set_rollback(
                True
            )

            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        f"Unable to reserve a time "
                        f"for {booking_item.ride.name}."
                    ),
                },
                status=409,
            )


    # =====================================================
    # RIDE NAMES
    # =====================================================

    ride_names = ", ".join(
        [
            item[
                "ride_name"
            ]

            for item
            in validated_items
        ]
    )


    if not ride_names:

        ride_names = (
            "Flying Fox Adventure Booking"
        )


    # =====================================================
    # RAZORPAY AMOUNT
    # =====================================================

    amount_paise = int(
        (
            validated[
                "total_amount"
            ]
            *
            Decimal(
                "100"
            )
        )
        .quantize(
            Decimal(
                "1"
            ),
            rounding=
                ROUND_HALF_UP,
        )
    )


    # =====================================================
    # AMOUNT VALIDATION
    # =====================================================

    if amount_paise <= 0:

        transaction.set_rollback(
            True
        )


        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Invalid payment amount."
                ),
            },
            status=400,
        )


    # =====================================================
    # RAZORPAY RECEIPT
    # =====================================================

    receipt = (
        f"ff-"
        f"{str(booking.booking_id).replace('-', '')[:24]}"
    )


    # =====================================================
    # CREATE RAZORPAY ORDER
    # =====================================================

    try:

        razorpay_order = (
            client.order.create(
                {
                    "amount":
                        amount_paise,

                    "currency":
                        "INR",

                    "receipt":
                        receipt,

                    "notes":
                        {
                            "booking_id":
                                str(
                                    booking.booking_id
                                ),

                            "rides":
                                ride_names[
                                    :250
                                ],

                            "ride_count":
                                str(
                                    len(
                                        validated_items
                                    )
                                ),

                            "total_riders":
                                str(
                                    validated[
                                        "quantity"
                                    ]
                                ),
                        },
                }
            )
        )


    except Exception as error:

        print(
            "\n================================"
        )

        print(
            "RAZORPAY ORDER CREATE ERROR"
        )

        print(
            "TYPE:",
            type(error).__name__
        )

        print(
            "ERROR:",
            repr(error)
        )

        print(
            "AMOUNT:",
            amount_paise
        )

        print(
            "RECEIPT:",
            receipt
        )

        print(
            "RIDES:",
            ride_names
        )

        print(
            "================================\n"
        )


        # Because the complete function is atomic,
        # Booking + BookingRideItem + slot holds
        # are rolled back too.

        transaction.set_rollback(
            True
        )


        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Unable to create the Razorpay "
                    "order. Please try again."
                ),
            },
            status=502,
        )


    # =====================================================
    # VERIFY RAZORPAY RESPONSE
    # =====================================================

    razorpay_order_id = (
        razorpay_order.get(
            "id"
        )
    )


    if not razorpay_order_id:

        transaction.set_rollback(
            True
        )


        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Invalid response received from "
                    "the payment service."
                ),
            },
            status=502,
        )


    # =====================================================
    # CREATE PAYMENT RECORD
    #
    # One payment for whole booking.
    # =====================================================

    try:

        payment = Payment.objects.create(

            booking=
                booking,

            gateway=
                "razorpay",

            gateway_order_id=
                razorpay_order_id,

            amount=
                validated[
                    "total_amount"
                ],

            status=
                "created",
        )


    except Exception as error:

        print(
            "\n================================"
        )

        print(
            "PAYMENT RECORD CREATE ERROR"
        )

        print(
            "TYPE:",
            type(error).__name__
        )

        print(
            "ERROR:",
            repr(error)
        )

        print(
            "================================\n"
        )


        transaction.set_rollback(
            True
        )


        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Payment order was prepared, "
                    "but the local payment record "
                    "could not be created."
                ),
            },
            status=500,
        )


    # =====================================================
    # SAVE CURRENT BOOKING TO SESSION
    # =====================================================

    request.session[
        "current_booking_id"
    ] = str(
        booking.booking_id
    )


    request.session.modified = True


    # =====================================================
    # DEBUG SUCCESS
    # =====================================================

    print(
        "\n================================"
    )

    print(
        "MULTI-RIDE BOOKING CREATED"
    )

    print(
        "BOOKING:",
        booking.booking_id
    )

    print(
        "RIDES:",
        ride_names
    )

    print(
        "RIDE COUNT:",
        len(
            validated_items
        )
    )

    print(
        "TOTAL RIDERS:",
        validated[
            "quantity"
        ]
    )

    print(
        "TOTAL:",
        validated[
            "total_amount"
        ]
    )

    print(
        "SLOT HOLD EXPIRES:",
        hold_expires_at
    )

    print(
        "RAZORPAY ORDER:",
        razorpay_order_id
    )

    print(
        "================================\n"
    )


    # =====================================================
    # SUCCESS JSON FOR RAZORPAY CHECKOUT
    # =====================================================

    return JsonResponse(
        {
            "success":
                True,

            "key_id":
                key_id,

            "order_id":
                payment.gateway_order_id,

            "amount":
                amount_paise,

            "currency":
                "INR",

            "booking_id":
                str(
                    booking.booking_id
                ),

            "description":
                ride_names,

            "ride_count":
                len(
                    validated_items
                ),

            "customer_name":
                customer_name,

            "customer_email":
                customer_email,

            "customer_phone":
                customer_phone,
        }
    )






def booking_payment_verify(request):

    """
    Final Razorpay payment verification
    for the multi-ride booking system.

    Flow:

    1. Receive Razorpay callback data.
    2. Find parent Booking + all BookingRideItems.
    3. Find local Payment.
    4. Verify browser order ID against local order ID.
    5. Verify Razorpay signature.
    6. Fetch payment directly from Razorpay.
    7. Verify Razorpay order ID.
    8. Verify paid amount.
    9. Verify payment status = captured.
    10. Atomically:
        - mark Payment = paid
        - mark Booking = confirmed
        - keep all BookingRideItems booked
        - convert BookingRideSlot held rows to confirmed
        - create/get one Ticket for whole booking
    11. Generate QR.
    12. Generate PDF.
    13. Send email/SMS/WhatsApp.
    14. Clear temporary booking session.
    15. Return success URL.

    IMPORTANT:

    A ticket, PDF or notification failure must NEVER
    roll back an already captured Razorpay payment.
    """


    # =====================================================
    # 1. POST ONLY
    # =====================================================

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "message": "POST request required.",
            },
            status=405,
        )


    # =====================================================
    # 2. RAZORPAY CALLBACK DATA
    # =====================================================

    booking_id = (
        request.POST.get(
            "booking_id",
            ""
        )
        .strip()
    )


    razorpay_payment_id = (
        request.POST.get(
            "razorpay_payment_id",
            ""
        )
        .strip()
    )


    browser_order_id = (
        request.POST.get(
            "razorpay_order_id",
            ""
        )
        .strip()
    )


    razorpay_signature = (
        request.POST.get(
            "razorpay_signature",
            ""
        )
        .strip()
    )


    # =====================================================
    # 3. REQUIRED DATA
    # =====================================================

    if not all(
        [
            booking_id,
            razorpay_payment_id,
            browser_order_id,
            razorpay_signature,
        ]
    ):

        print(
            "\n========================================"
        )

        print(
            "RAZORPAY VERIFY MISSING DATA"
        )

        print(
            {
                "booking_id":
                    bool(
                        booking_id
                    ),

                "payment_id":
                    bool(
                        razorpay_payment_id
                    ),

                "order_id":
                    bool(
                        browser_order_id
                    ),

                "signature":
                    bool(
                        razorpay_signature
                    ),
            }
        )

        print(
            "========================================\n"
        )


        return JsonResponse(
            {
                "success": False,

                "message": (
                    "Missing Razorpay payment "
                    "information."
                ),
            },
            status=400,
        )


    # =====================================================
    # 4. FIND PARENT BOOKING
    #
    # NEW:
    #
    # Load all BookingRideItem rows together with:
    #
    # ride
    # ride_price
    # offer
    # weight_groups
    #
    # Parent Booking.ride is only temporary legacy data.
    # =====================================================

    try:

        booking = (
            Booking.objects

            .select_related(
                "user",
            )

            .prefetch_related(
                "ride_items__ride",
                "ride_items__ride_price",
                "ride_items__offer",
                "ride_items__weight_groups",
                "ride_items__allocated_slots",
            )

            .get(
                booking_id=
                    booking_id
            )
        )


    except Booking.DoesNotExist:

        print(
            "PAYMENT VERIFY BOOKING NOT FOUND:",
            booking_id
        )


        return JsonResponse(
            {
                "success": False,

                "message": (
                    "Booking could not be found."
                ),
            },
            status=404,
        )


    # =====================================================
    # 5. VERIFY BOOKING HAS RIDE ITEMS
    # =====================================================

    booking_items = list(
        booking.ride_items.all()
    )


    if not booking_items:

        print(
            "\n========================================"
        )

        print(
            "PAYMENT VERIFY: NO BOOKING ITEMS"
        )

        print(
            "BOOKING:",
            booking.booking_id
        )

        print(
            "========================================\n"
        )


        return JsonResponse(
            {
                "success": False,

                "message": (
                    "No rides were found in this booking."
                ),
            },
            status=400,
        )


    # =====================================================
    # RIDE NAMES FOR LOGGING
    # =====================================================

    ride_names = ", ".join(
        [
            item.ride.name

            for item
            in booking_items

            if item.ride
        ]
    )


    # =====================================================
    # 6. FIND LOCAL PAYMENT
    # =====================================================

    try:

        payment = (
            Payment.objects
            .get(
                booking=
                    booking
            )
        )


    except Payment.DoesNotExist:

        print(
            "PAYMENT VERIFY PAYMENT RECORD NOT FOUND:",
            booking_id
        )


        return JsonResponse(
            {
                "success": False,

                "message": (
                    "Payment record could not be found."
                ),
            },
            status=404,
        )


    # =====================================================
    # 7. IDEMPOTENCY
    #
    # Razorpay/browser may call verification twice.
    # =====================================================

    if (
        booking.status
        in [
            "confirmed",
            "checked_in",
        ]
        and
        payment.status
        ==
        "paid"
    ):

        return JsonResponse(
            {
                "success": True,

                "redirect_url":
                    reverse(
                        "booking_success",
                        kwargs={
                            "booking_id":
                                str(
                                    booking.booking_id
                                )
                        },
                    ),
            }
        )


    # =====================================================
    # 8. VERIFY BROWSER ORDER AGAINST LOCAL ORDER
    #
    # Never use browser order ID as source of truth.
    # =====================================================

    if (
        browser_order_id
        !=
        payment.gateway_order_id
    ):

        print(
            "\n========================================"
        )

        print(
            "RAZORPAY LOCAL ORDER MISMATCH"
        )

        print(
            "BOOKING:",
            booking.booking_id
        )

        print(
            "RIDES:",
            ride_names
        )

        print(
            "LOCAL ORDER:",
            payment.gateway_order_id
        )

        print(
            "BROWSER ORDER:",
            browser_order_id
        )

        print(
            "PAYMENT ID:",
            razorpay_payment_id
        )

        print(
            "========================================\n"
        )


        # Do NOT modify a real booking/payment because
        # somebody supplied an incorrect callback.

        return JsonResponse(
            {
                "success": False,

                "message": (
                    "Payment order verification failed."
                ),
            },
            status=400,
        )


    # =====================================================
    # 9. RAZORPAY SETTINGS
    # =====================================================

    key_id = getattr(
        settings,
        "RAZORPAY_KEY_ID",
        ""
    )


    key_secret = getattr(
        settings,
        "RAZORPAY_KEY_SECRET",
        ""
    )


    if (
        not key_id
        or
        not key_secret
    ):

        print(
            "RAZORPAY KEYS NOT CONFIGURED"
        )


        return JsonResponse(
            {
                "success": False,

                "message": (
                    "Payment verification service "
                    "is not configured."
                ),
            },
            status=500,
        )


    # =====================================================
    # 10. RAZORPAY CLIENT
    # =====================================================

    client = razorpay.Client(
        auth=(
            key_id,
            key_secret,
        )
    )


    # =====================================================
    # 11. VERIFY PAYMENT SIGNATURE
    # =====================================================

    try:

        client.utility.verify_payment_signature(
            {
                # Always verify using our DATABASE
                # Razorpay order ID.

                "razorpay_order_id":
                    payment.gateway_order_id,

                "razorpay_payment_id":
                    razorpay_payment_id,

                "razorpay_signature":
                    razorpay_signature,
            }
        )


    except Exception as error:

        print(
            "\n========================================"
        )

        print(
            "RAZORPAY SIGNATURE ERROR"
        )

        print(
            "TYPE:",
            type(error).__name__
        )

        print(
            "ERROR:",
            repr(error)
        )

        print(
            "BOOKING:",
            booking.booking_id
        )

        print(
            "RIDES:",
            ride_names
        )

        print(
            "PAYMENT ID:",
            razorpay_payment_id
        )

        print(
            "LOCAL ORDER:",
            payment.gateway_order_id
        )

        print(
            "BROWSER ORDER:",
            browser_order_id
        )

        print(
            "========================================\n"
        )


        # Never change booking/payment status here.

        return JsonResponse(
            {
                "success": False,

                "message": (
                    "Payment signature "
                    "verification failed."
                ),
            },
            status=400,
        )


    # =====================================================
    # SIGNATURE IS VALID
    # =====================================================


    # =====================================================
    # 12. FETCH PAYMENT DIRECTLY FROM RAZORPAY
    # =====================================================

    try:

        remote_payment = (
            client.payment.fetch(
                razorpay_payment_id
            )
        )


    except Exception as error:

        print(
            "\n========================================"
        )

        print(
            "RAZORPAY FETCH ERROR"
        )

        print(
            "TYPE:",
            type(error).__name__
        )

        print(
            "ERROR:",
            repr(error)
        )

        print(
            "BOOKING:",
            booking.booking_id
        )

        print(
            "PAYMENT ID:",
            razorpay_payment_id
        )

        print(
            "ORDER ID:",
            payment.gateway_order_id
        )

        print(
            "========================================\n"
        )


        # =================================================
        # Signature is already valid.
        #
        # Save references so we don't lose them even if
        # Razorpay's fetch endpoint temporarily fails.
        # =================================================

        try:

            payment.gateway_payment_id = (
                razorpay_payment_id
            )

            payment.gateway_signature = (
                razorpay_signature
            )

            payment.save(
                update_fields=[
                    "gateway_payment_id",
                    "gateway_signature",
                    "updated_at",
                ]
            )


        except Exception as save_error:

            print(
                "RAZORPAY REFERENCE SAVE ERROR:",
                repr(
                    save_error
                )
            )


        return JsonResponse(
            {
                "success": False,

                "message": (
                    "Payment was received but its "
                    "status could not be confirmed yet. "
                    "Please do not make another payment."
                ),
            },
            status=502,
        )


    # =====================================================
    # 13. REMOTE PAYMENT DETAILS
    # =====================================================

    remote_order_id = (
        remote_payment.get(
            "order_id",
            ""
        )
    )


    remote_amount = (
        remote_payment.get(
            "amount"
        )
    )


    remote_status = (
        remote_payment.get(
            "status",
            ""
        )
    )


    # =====================================================
    # LOG REMOTE DATA
    # =====================================================

    print(
        "\n========================================"
    )

    print(
        "RAZORPAY PAYMENT FETCH SUCCESS"
    )

    print(
        "BOOKING:",
        booking.booking_id
    )

    print(
        "RIDES:",
        ride_names
    )

    print(
        "PAYMENT ID:",
        razorpay_payment_id
    )

    print(
        "LOCAL ORDER:",
        payment.gateway_order_id
    )

    print(
        "REMOTE ORDER:",
        remote_order_id
    )

    print(
        "REMOTE STATUS:",
        remote_status
    )

    print(
        "REMOTE AMOUNT:",
        remote_amount
    )

    print(
        "========================================\n"
    )


    # =====================================================
    # 14. VERIFY REMOTE ORDER
    # =====================================================

    if (
        remote_order_id
        !=
        payment.gateway_order_id
    ):

        print(
            "RAZORPAY REMOTE ORDER MISMATCH:",
            {
                "booking":
                    str(
                        booking.booking_id
                    ),

                "local_order":
                    payment.gateway_order_id,

                "remote_order":
                    remote_order_id,

                "payment_id":
                    razorpay_payment_id,
            }
        )


        return JsonResponse(
            {
                "success": False,

                "message": (
                    "Razorpay order "
                    "verification failed."
                ),
            },
            status=400,
        )


    # =====================================================
    # 15. VERIFY AMOUNT
    #
    # Payment.amount contains the combined multi-ride total.
    # =====================================================

    expected_amount_paise = int(
        (
            Decimal(
                str(
                    payment.amount
                )
            )
            *
            Decimal("100")
        )
        .quantize(
            Decimal("1"),
            rounding=
                ROUND_HALF_UP,
        )
    )


    if (
        remote_amount
        !=
        expected_amount_paise
    ):

        print(
            "RAZORPAY AMOUNT MISMATCH:",
            {
                "booking":
                    str(
                        booking.booking_id
                    ),

                "expected":
                    expected_amount_paise,

                "received":
                    remote_amount,

                "payment_id":
                    razorpay_payment_id,
            }
        )


        return JsonResponse(
            {
                "success": False,

                "message": (
                    "Payment amount "
                    "verification failed."
                ),
            },
            status=400,
        )


    # =====================================================
    # 16. SAVE VERIFIED RAZORPAY REFERENCES
    #
    # Store before ticket generation.
    # =====================================================

    try:

        payment.gateway_payment_id = (
            razorpay_payment_id
        )

        payment.gateway_signature = (
            razorpay_signature
        )

        payment.save(
            update_fields=[
                "gateway_payment_id",
                "gateway_signature",
                "updated_at",
            ]
        )


    except Exception as error:

        print(
            "\n========================================"
        )

        print(
            "RAZORPAY REFERENCE SAVE ERROR"
        )

        print(
            "TYPE:",
            type(error).__name__
        )

        print(
            "ERROR:",
            repr(error)
        )

        print(
            "========================================\n"
        )


        return JsonResponse(
            {
                "success": False,

                "message": (
                    "Payment was verified but could not "
                    "be recorded locally. "
                    "Please contact support and "
                    "do not pay again."
                ),
            },
            status=500,
        )


    # =====================================================
    # 17. PAYMENT MUST BE CAPTURED
    # =====================================================

    if remote_status != "captured":

        # Razorpay may sometimes temporarily return:
        # authorized

        if remote_status == "authorized":

            payment.status = (
                "authorized"
            )

        else:

            payment.status = (
                "created"
            )


        payment.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )


        print(
            "RAZORPAY PAYMENT NOT CAPTURED:",
            {
                "booking":
                    str(
                        booking.booking_id
                    ),

                "payment_id":
                    razorpay_payment_id,

                "remote_status":
                    remote_status,
            }
        )


        return JsonResponse(
            {
                "success": False,

                "message": (
                    "Payment is not captured yet. "
                    "Please do not make another payment."
                ),
            },
            status=409,
        )


    # =====================================================
    # 18. PAYMENT CAPTURED
    #
    # Only DB finalization is inside this transaction.
    # =====================================================

    try:

        with transaction.atomic():

            # =================================================
            # LOCK PAYMENT
            # =================================================

            locked_payment = (
                Payment.objects
                .select_for_update()
                .get(
                    pk=
                        payment.pk
                )
            )


            # =================================================
            # LOCK PARENT BOOKING
            # =================================================

            locked_booking = (
                Booking.objects
                .select_for_update()
                .get(
                    pk=
                        booking.pk
                )
            )


            # =================================================
            # LOCK RIDE ITEMS
            #
            # Makes payment finalization safe if callbacks
            # happen at the same time.
            # =================================================

            locked_booking_items = list(
                BookingRideItem.objects
               .select_for_update()
               .filter(
                booking=locked_booking
               )
              .select_related(
             "ride",
              "ride_price",
               )
            )


            if not locked_booking_items:

                raise ValueError(
                    (
                        "Booking has no "
                        "BookingRideItem records."
                    )
                )


            # =================================================
            # PAYMENT → PAID
            # =================================================

            locked_payment.gateway_payment_id = (
                razorpay_payment_id
            )

            locked_payment.gateway_signature = (
                razorpay_signature
            )

            locked_payment.status = (
                "paid"
            )


            if not locked_payment.paid_at:

                locked_payment.paid_at = (
                    timezone.now()
                )


            locked_payment.failure_reason = ""


            locked_payment.save(
                update_fields=[
                    "gateway_payment_id",
                    "gateway_signature",
                    "status",
                    "paid_at",
                    "failure_reason",
                    "updated_at",
                ]
            )


            # =================================================
            # PARENT BOOKING → CONFIRMED
            # =================================================

            locked_booking.status = (
                "confirmed"
            )


            locked_booking.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )


            # =================================================
            # BOOKING RIDE ITEMS
            #
            # booking_confirm() currently creates each item
            # with status="booked".
            #
            # Keep that state after successful payment.
            #
            # This section also repairs any item that somehow
            # still has another pre-payment status.
            # =================================================

            for booking_item in locked_booking_items:

                if (
                    booking_item.status
                    !=
                    "booked"
                ):

                    booking_item.status = (
                        "booked"
                    )

                    booking_item.save(
                        update_fields=[
                            "status",
                        ]
                    )


            # =================================================
            # BOOKING RIDE SLOTS → CONFIRMED
            #
            # The slots were created as status="held" when
            # booking_confirm() created the Razorpay order.
            #
            # Now Razorpay has returned status="captured", so
            # these temporary holds become permanent confirmed
            # allocations.
            #
            # Lock the slot rows as part of the same transaction
            # so concurrent payment callbacks cannot finalize
            # them inconsistently.
            # =================================================

            locked_slot_rows = list(
                BookingRideSlot.objects
                .select_for_update()
                .filter(
                    booking_item__booking=
                        locked_booking
                )
                .select_related(
                    "booking_item",
                    "booking_item__ride",
                )
                .order_by(
                    "booking_item_id",
                    "slot_start_time",
                )
            )


            if not locked_slot_rows:

                raise ValueError(
                    (
                        "Booking has no "
                        "BookingRideSlot records."
                    )
                )


            # =================================================
            # VERIFY EVERY BOOKING ITEM HAS THE CORRECT NUMBER
            # OF RIDERS ALLOCATED ACROSS ITS SLOT ROWS
            # =================================================

            slots_by_item = {}


            for slot_row in locked_slot_rows:

                slots_by_item.setdefault(
                    slot_row.booking_item_id,
                    []
                ).append(
                    slot_row
                )


            for booking_item in locked_booking_items:

                item_slot_rows = (
                    slots_by_item.get(
                        booking_item.id,
                        []
                    )
                )


                if not item_slot_rows:

                    raise ValueError(
                        (
                            f"No slot allocation exists for "
                            f"{booking_item.ride.name}."
                        )
                    )


                allocated_riders = sum(
                    slot_row.participant_count

                    for slot_row
                    in item_slot_rows
                )


                if (
                    allocated_riders
                    !=
                    booking_item.quantity
                ):

                    raise ValueError(
                        (
                            f"Slot allocation rider count "
                            f"does not match booking quantity "
                            f"for {booking_item.ride.name}."
                        )
                    )


            # =================================================
            # HELD → CONFIRMED
            #
            # Once confirmed, hold_expires_at is cleared.
            # Already-confirmed rows are left unchanged, which
            # also makes this safe if finalization is retried.
            # =================================================

            confirmed_slot_count = (
                BookingRideSlot.objects
                .filter(
                    booking_item__booking=
                        locked_booking,

                    status=
                        "held",
                )
                .update(
                    status=
                        "confirmed",

                    hold_expires_at=
                        None,
                )
            )


            # =================================================
            # FINAL SLOT STATUS SAFETY CHECK
            # =================================================

            remaining_unconfirmed_slots = (
                BookingRideSlot.objects
                .filter(
                    booking_item__booking=
                        locked_booking,
                )
                .exclude(
                    status=
                        "confirmed",
                )
                .exists()
            )


            if remaining_unconfirmed_slots:

                raise ValueError(
                    (
                        "One or more booking slot rows "
                        "could not be confirmed."
                    )
                )


            print(
                "\\n========================================"
            )

            print(
                "BOOKING RIDE SLOTS CONFIRMED"
            )

            print(
                "BOOKING:",
                locked_booking.booking_id
            )

            print(
                "SLOT ROWS CHANGED:",
                confirmed_slot_count
            )

            print(
                "TOTAL SLOT ROWS:",
                len(
                    locked_slot_rows
                )
            )

            print(
                "========================================\\n"
            )


            # =================================================
            # ONE TICKET FOR WHOLE PARENT BOOKING
            # =================================================

            ticket, created = (
                Ticket.objects
                .get_or_create(
                    booking=
                        locked_booking
                )
            )


            # =================================================
            # KEEP FINAL OBJECTS
            # =================================================

            payment = (
                locked_payment
            )

            booking = (
                locked_booking
            )


    except Exception as error:

        print(
            "\n========================================"
        )

        print(
            "PAYMENT DATABASE FINALIZATION ERROR"
        )

        print(
            "TYPE:",
            type(error).__name__
        )

        print(
            "ERROR:",
            repr(error)
        )

        print(
            "BOOKING:",
            booking.booking_id
        )

        print(
            "RIDES:",
            ride_names
        )

        print(
            "PAYMENT ID:",
            razorpay_payment_id
        )

        print(
            "ORDER:",
            payment.gateway_order_id
        )

        print(
            "========================================\n"
        )


        # Razorpay has already captured the money.
        # Never ask customer to pay again.

        return JsonResponse(
            {
                "success": False,

                "message": (
                    "Your payment was successfully captured, "
                    "but the booking could not be finalized. "
                    "Please contact support and do not make "
                    "another payment."
                ),
            },
            status=500,
        )


    # =====================================================
    # DATABASE IS NOW COMMITTED
    #
    # Payment             = paid
    # Booking             = confirmed
    # BookingRideItems    = booked
    # BookingRideSlots    = confirmed
    # Ticket row          = exists
    #
    # Everything below is non-critical.
    # =====================================================


    # =====================================================
    # 19. RELOAD BOOKING WITH MULTI-RIDE DETAILS
    #
    # Ticket PDF / notifications can access these.
    # =====================================================

    try:

        booking = (
            Booking.objects

            .select_related(
                "user",
            )

            .prefetch_related(
                "ride_items__ride",
                "ride_items__ride_price",
                "ride_items__offer",
                "ride_items__weight_groups",
            )

            .get(
                pk=
                    booking.pk
            )
        )

        ticket.booking = booking


    except Exception as error:

        print(
            "BOOKING MULTI-RIDE RELOAD ERROR:",
            repr(error)
        )


    # =====================================================
    # 20. GENERATE QR
    # =====================================================

    try:

        if not ticket.qr_image:

            generate_ticket_qr(
                request,
                ticket,
            )

            ticket.save()


    except Exception as error:

        print(
            "\n========================================"
        )

        print(
            "TICKET QR GENERATION ERROR"
        )

        print(
            "TYPE:",
            type(error).__name__
        )

        print(
            "ERROR:",
            repr(error)
        )

        print(
            "BOOKING:",
            booking.booking_id
        )

        print(
            "========================================\n"
        )


# =====================================================
# 21. GENERATE WHATSAPP TICKET IMAGE
# =====================================================

    try:

       if not ticket.whatsapp_ticket_image:

        generate_whatsapp_ticket_image(
            ticket
        )

        ticket.refresh_from_db()

    except Exception as error:

        print(
        "\n========================================"
       )

        print(
        "WHATSAPP TICKET IMAGE GENERATION ERROR"
       )

        print(
        "TYPE:",
        type(error).__name__
        )

        print(
        "ERROR:",
        repr(error)
      )

        print(
        "BOOKING:",
        booking.booking_id
    )

        print(
        "========================================\n"
    )



    # =====================================================
    # 21. GENERATE PDF
    #
    # NOTE:
    # generate_ticket_pdf() still needs its own
    # multi-ride update next.
    # =====================================================

    try:

        if not ticket.pdf_ticket:

            generate_ticket_pdf(
                ticket
            )

            ticket.save()


    except Exception as error:

        print(
            "\n========================================"
        )

        print(
            "TICKET PDF GENERATION ERROR"
        )

        print(
            "TYPE:",
            type(error).__name__
        )

        print(
            "ERROR:",
            repr(error)
        )

        print(
            "BOOKING:",
            booking.booking_id
        )

        print(
            "========================================\n"
        )


    # =====================================================
    # 22. EMAIL
    #
    # Notification functions will be updated separately
    # to list all rides.
    # =====================================================

    email_sent = False


    try:

        email_sent = (
            send_ticket_email(
                ticket
            )
        )


    except Exception as error:

        print(
            "\n========================================"
        )

        print(
            "TICKET EMAIL ERROR"
        )

        print(
            "TYPE:",
            type(error).__name__
        )

        print(
            "ERROR:",
            repr(error)
        )

        print(
            "BOOKING:",
            booking.booking_id
        )

        print(
            "========================================\n"
        )


    # =====================================================
    # 23. SMS
    # =====================================================

    sms_sent = False


    try:

        sms_sent = (
            send_ticket_sms(
                ticket
            )
        )


    except Exception as error:

        print(
            "\n========================================"
        )

        print(
            "TICKET SMS ERROR"
        )

        print(
            "TYPE:",
            type(error).__name__
        )

        print(
            "ERROR:",
            repr(error)
        )

        print(
            "BOOKING:",
            booking.booking_id
        )

        print(
            "========================================\n"
        )


    # =====================================================
    # 24. WHATSAPP
    # =====================================================

    whatsapp_sent = False


    try:

        whatsapp_sent = (
            send_ticket_whatsapp(
                request,
                ticket,
            )
        )


    except Exception as error:

        print(
            "\n========================================"
        )

        print(
            "TICKET WHATSAPP ERROR"
        )

        print(
            "TYPE:",
            type(error).__name__
        )

        print(
            "ERROR:",
            repr(error)
        )

        print(
            "BOOKING:",
            booking.booking_id
        )

        print(
            "========================================\n"
        )


    # =====================================================
    # 25. SAVE TICKET NOTIFICATION STATUS
    # =====================================================

    try:

        ticket.email_sent = (
            bool(
                email_sent
            )
        )


        ticket.whatsapp_sent = (
            bool(
                whatsapp_sent
            )
        )


        ticket.save(
            update_fields=[
                "email_sent",
                "whatsapp_sent",
            ]
        )


    except Exception as error:

        print(
            "TICKET DELIVERY STATUS SAVE ERROR:",
            repr(error)
        )


    # =====================================================
    # 26. BOOKING NOTIFICATION STATUS
    # =====================================================

    try:

        booking.notifications_sent = (
            bool(
                email_sent
                or
                sms_sent
                or
                whatsapp_sent
            )
        )


        booking.save(
            update_fields=[
                "notifications_sent",
                "updated_at",
            ]
        )


    except Exception as error:

        print(
            "BOOKING NOTIFICATION STATUS ERROR:",
            repr(error)
        )

# =====================================================
# 27. CLEAR TEMPORARY BOOKING SESSION
#
# Only clear after successful payment finalization.
# =====================================================

    try:

        request.session.pop(
        "pending_booking",
        None,
       )


        request.session.pop(
        "current_booking_id",
        None,
    )


    # =================================================
    # CLEAR BOOKING MOBILE OTP VERIFICATION
    # =================================================

        request.session.pop(
        "booking_verified_phone",
        None,
    )


        request.session.modified = True


    except Exception as error:

        print(
        "PAYMENT SESSION CLEANUP ERROR:",
        repr(error)
    )


    # =====================================================
    # 28. FINAL SUCCESS LOG
    # =====================================================

    print(
        "\n========================================"
    )

    print(
        "MULTI-RIDE PAYMENT VERIFIED SUCCESSFULLY"
    )

    print(
        "BOOKING:",
        booking.booking_id
    )

    print(
        "RIDES:",
        ride_names
    )

    print(
        "RIDE COUNT:",
        len(
            booking_items
        )
    )

    print(
        "PAYMENT ID:",
        payment.gateway_payment_id
    )

    print(
        "ORDER ID:",
        payment.gateway_order_id
    )

    print(
        "AMOUNT:",
        payment.amount
    )

    print(
        "PAYMENT STATUS:",
        payment.status
    )

    print(
        "BOOKING STATUS:",
        booking.status
    )

    print(
        "========================================\n"
    )


    # =====================================================
    # 29. SUCCESS
    # =====================================================

    return JsonResponse(
        {
            "success":
                True,

            "redirect_url":
                reverse(
                    "booking_success",
                    kwargs={
                        "booking_id":
                            str(
                                booking.booking_id
                            )
                    },
                ),
        }
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

    # IMPORTANT:
    # Convert QR from 1-bit grayscale to standard RGB PNG
    qr_image = qr_image.convert("RGB")

    buffer = BytesIO()

    qr_image.save(
        buffer,
        format="PNG",
    )

    ticket.qr_image.save(
        f"ticket-{ticket.ticket_id}.png",
        ContentFile(buffer.getvalue()),
        save=False,
    )



def generate_whatsapp_ticket_image(ticket):
    """
    Generate Flying Fox Adventure WhatsApp ticket image.

    Supports:
    - Multi-ride bookings
    - Maximum 3 rides
    - Confirmed ride slot schedules
    - Split participant allocations
    - Dynamic compact layout
    - Existing static Flying Fox ticket background
    - Existing QR area
    """

    # =====================================================
    # BOOKING
    # =====================================================

    booking = (
        Booking.objects
        .prefetch_related(
            "ride_items__ride",
            "ride_items__allocated_slots",
        )
        .get(
            pk=ticket.booking_id
        )
    )

    # =====================================================
    # COLORS
    # =====================================================

    RED = "#D71920"
    DARK = "#111111"
    GRAY = "#555555"
    LIGHT_GRAY = "#DDDDDD"
    DIVIDER = "#D8D8D8"
    WHITE = "#FFFFFF"

    # =====================================================
    # BACKGROUND
    # =====================================================

    background_path = os.path.join(
        settings.BASE_DIR,
        "static",
        "frontend",
        "assets",
        "img",
        "ticket",
        "flying_fox_ticket_background.png",
    )

    if not os.path.exists(background_path):

        raise FileNotFoundError(
            "WhatsApp ticket background not found: "
            f"{background_path}"
        )

    image = (
        Image.open(
            background_path
        )
        .convert("RGB")
    )

    # =====================================================
    # FINAL IMAGE SIZE
    # =====================================================

    width = 1600
    height = 900

    image = image.resize(
        (
            width,
            height,
        ),
        Image.Resampling.LANCZOS,
    )

    draw = ImageDraw.Draw(
        image
    )

    # =====================================================
    # FONT LOADER
    # =====================================================

    def load_font(
        size,
        bold=False,
    ):

        possible_fonts = []

        # -------------------------------------------------
        # PROJECT FONT
        # -------------------------------------------------

        if bold:

            possible_fonts.append(
                os.path.join(
                    settings.BASE_DIR,
                    "static",
                    "ticket",
                    "fonts",
                    "DejaVuSans-Bold.ttf",
                )
            )

        else:

            possible_fonts.append(
                os.path.join(
                    settings.BASE_DIR,
                    "static",
                    "ticket",
                    "fonts",
                    "DejaVuSans.ttf",
                )
            )

        # -------------------------------------------------
        # WINDOWS
        # -------------------------------------------------

        if bold:

            possible_fonts.append(
                r"C:\Windows\Fonts\arialbd.ttf"
            )

        else:

            possible_fonts.append(
                r"C:\Windows\Fonts\arial.ttf"
            )

        # -------------------------------------------------
        # UBUNTU
        # -------------------------------------------------

        if bold:

            possible_fonts.append(
                "/usr/share/fonts/truetype/"
                "dejavu/DejaVuSans-Bold.ttf"
            )

        else:

            possible_fonts.append(
                "/usr/share/fonts/truetype/"
                "dejavu/DejaVuSans.ttf"
            )

        # -------------------------------------------------
        # LOAD FIRST AVAILABLE
        # -------------------------------------------------

        for font_path in possible_fonts:

            if os.path.exists(
                font_path
            ):

                return ImageFont.truetype(
                    font_path,
                    size,
                )

        raise FileNotFoundError(
            "No suitable font was found for "
            "WhatsApp ticket generation."
        )

    # =====================================================
    # FIT FONT
    # =====================================================

    def fit_font(
        text,
        max_width,
        start_size=24,
        minimum_size=10,
        bold=True,
    ):

        text = str(
            text or ""
        )

        size = start_size

        while size >= minimum_size:

            font = load_font(
                size,
                bold=bold,
            )

            bbox = draw.textbbox(
                (
                    0,
                    0,
                ),
                text,
                font=font,
            )

            text_width = (
                bbox[2]
                -
                bbox[0]
            )

            if text_width <= max_width:

                return font

            size -= 1

        return load_font(
            minimum_size,
            bold=bold,
        )

    # =====================================================
    # SAFE TEXT
    # =====================================================

    def safe_text(value):

        if value is None:
            return ""

        return str(
            value
        ).strip()

    # =====================================================
    # FORMAT SLOT TIME
    # =====================================================

    def format_slot_time(value):

        if not value:
            return ""

        formatted = value.strftime(
            "%I:%M %p"
        )

        # 08:30 AM -> 8:30 AM
        return formatted.lstrip("0")

    # =====================================================
    # BASIC BOOKING DATA
    # =====================================================

    customer_name = safe_text(
        booking.customer_name
    )

    ticket_number = safe_text(
        ticket.ticket_number
    )

    # =====================================================
    # DISPLAY TICKET NUMBER
    # =====================================================

    if (
        ticket_number
        and
        not ticket_number.upper().startswith(
            "TKT-"
        )
    ):

        display_ticket_number = (
            f"TKT-{ticket_number}"
        )

    else:

        display_ticket_number = (
            ticket_number
        )

    # =====================================================
    # COMPACT BOOKING ID
    # =====================================================

    full_booking_id = safe_text(
        booking.booking_id
    )

    if full_booking_id:

        compact_booking_id = (
            "FFX-"
            +
            full_booking_id[
                :8
            ].upper()
        )

    else:

        compact_booking_id = ""

    # =====================================================
    # VISIT DATE
    # =====================================================

    if booking.booking_date:

        visit_date = (
            booking.booking_date.strftime(
                "%d %B %Y"
            )
        )

    else:

        visit_date = ""

    # =====================================================
    # TOTAL AMOUNT
    # =====================================================

    total_amount = (
        booking.total_amount
        or
        0
    )

    try:

        amount_text = (
            f"Rs. "
            f"{float(total_amount):,.2f}"
        )

    except (
        TypeError,
        ValueError,
    ):

        amount_text = (
            f"Rs. {total_amount}"
        )

    # =====================================================
    # RIDES
    # =====================================================

    ride_items = list(
        booking.ride_items.all()
    )

    valid_ride_items = [

        item

        for item in ride_items

        if item.ride
    ]

    ride_count = len(
        valid_ride_items
    )

    # =====================================================
    # LIMIT WARNING
    # =====================================================

    if ride_count > 3:

        print(
            "WHATSAPP TICKET WARNING: "
            "More than 3 rides detected. "
            "Image layout is optimized for maximum 3 rides."
        )

    # =====================================================
    # TOTAL PARTICIPANTS
    # =====================================================

    total_participants = sum(

        int(
            item.quantity
            or
            0
        )

        for item
        in valid_ride_items
    )

    participant_word = (
        "Participant"
        if total_participants == 1
        else "Participants"
    )

    total_participant_text = (
        f"{total_participants} "
        f"{participant_word}"
    )

    # =====================================================
    # BUILD CONFIRMED SLOT DATA
    # =====================================================

    ride_schedule_data = []

    total_confirmed_slots = 0

    for item in valid_ride_items:

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

        total_confirmed_slots += len(
            confirmed_slots
        )

        ride_schedule_data.append(
            {
                "item": item,
                "ride_name": safe_text(
                    item.ride.name
                ),
                "quantity": int(
                    item.quantity
                    or
                    0
                ),
                "slots": confirmed_slots,
            }
        )

    # =====================================================
    # STATIC FONTS
    # =====================================================

    font_label = load_font(
        16,
        bold=False,
    )

    # =====================================================
    # BOOKING INFORMATION CARD
    # =====================================================

    info_left = 70
    info_right = 1090

    info_top = 285
    info_bottom = 510

    draw.rounded_rectangle(
        (
            info_left,
            info_top,
            info_right,
            info_bottom,
        ),
        radius=20,
        fill=WHITE,
        outline=LIGHT_GRAY,
        width=2,
    )

    # =====================================================
    # CENTER DIVIDER
    # =====================================================

    center_x = 585

    draw.line(
        (
            center_x,
            info_top + 16,
            center_x,
            info_bottom - 16,
        ),
        fill=DIVIDER,
        width=1,
    )

    # =====================================================
    # HORIZONTAL DIVIDERS
    # =====================================================

    first_divider_y = 358
    second_divider_y = 432

    draw.line(
        (
            info_left + 30,
            first_divider_y,
            info_right - 30,
            first_divider_y,
        ),
        fill=DIVIDER,
        width=1,
    )

    draw.line(
        (
            info_left + 30,
            second_divider_y,
            info_right - 30,
            second_divider_y,
        ),
        fill=DIVIDER,
        width=1,
    )

    # =====================================================
    # COLUMN POSITIONS
    # =====================================================

    left_x = 165
    right_x = 680

    # =====================================================
    # ROW 1 - GUEST / TICKET
    # =====================================================

    row1_label_y = 296
    row1_value_y = 321

    draw.text(
        (
            left_x,
            row1_label_y,
        ),
        "GUEST NAME",
        fill=GRAY,
        font=font_label,
    )

    guest_font = fit_font(
        customer_name,
        max_width=340,
        start_size=23,
        minimum_size=14,
        bold=True,
    )

    draw.text(
        (
            left_x,
            row1_value_y,
        ),
        customer_name,
        fill=DARK,
        font=guest_font,
    )

    draw.text(
        (
            right_x,
            row1_label_y,
        ),
        "TICKET NO.",
        fill=GRAY,
        font=font_label,
    )

    ticket_font = fit_font(
        display_ticket_number,
        max_width=330,
        start_size=23,
        minimum_size=14,
        bold=True,
    )

    draw.text(
        (
            right_x,
            row1_value_y,
        ),
        display_ticket_number,
        fill=DARK,
        font=ticket_font,
    )

    # =====================================================
    # ROW 2 - DATE / PARTICIPANTS
    # =====================================================

    row2_label_y = 370
    row2_value_y = 395

    draw.text(
        (
            left_x,
            row2_label_y,
        ),
        "VISIT DATE",
        fill=GRAY,
        font=font_label,
    )

    visit_font = fit_font(
        visit_date,
        max_width=340,
        start_size=21,
        minimum_size=13,
        bold=True,
    )

    draw.text(
        (
            left_x,
            row2_value_y,
        ),
        visit_date,
        fill=DARK,
        font=visit_font,
    )

    draw.text(
        (
            right_x,
            row2_label_y,
        ),
        "TOTAL PARTICIPANTS",
        fill=GRAY,
        font=font_label,
    )

    participant_font = fit_font(
        total_participant_text,
        max_width=330,
        start_size=21,
        minimum_size=13,
        bold=True,
    )

    draw.text(
        (
            right_x,
            row2_value_y,
        ),
        total_participant_text,
        fill=DARK,
        font=participant_font,
    )

    # =====================================================
    # ROW 3 - BOOKING / AMOUNT
    # =====================================================

    row3_label_y = 444
    row3_value_y = 469

    draw.text(
        (
            left_x,
            row3_label_y,
        ),
        "BOOKING ID",
        fill=GRAY,
        font=font_label,
    )

    booking_font = fit_font(
        compact_booking_id,
        max_width=340,
        start_size=21,
        minimum_size=13,
        bold=True,
    )

    draw.text(
        (
            left_x,
            row3_value_y,
        ),
        compact_booking_id,
        fill=DARK,
        font=booking_font,
    )

    draw.text(
        (
            right_x,
            row3_label_y,
        ),
        "TOTAL AMOUNT",
        fill=GRAY,
        font=font_label,
    )

    amount_font = fit_font(
        amount_text,
        max_width=330,
        start_size=24,
        minimum_size=14,
        bold=True,
    )

    draw.text(
        (
            right_x,
            row3_value_y,
        ),
        amount_text,
        fill=RED,
        font=amount_font,
    )

    # =====================================================
    # ADVENTURE & RIDE SCHEDULE
    # =====================================================

    schedule_left = 70
    schedule_right = 1090

    schedule_top = 525

    # IMPORTANT:
    # Keep everything above footer icons.
    schedule_max_bottom = 690

    schedule_header_height = 31

    # =====================================================
    # DECIDE DISPLAY MODE
    # =====================================================
    #
    # Detailed:
    # 1-2 rides with manageable slot count.
    #
    # Compact:
    # 3 rides or many slot allocations.
    #
    # =====================================================

    compact_mode = (
        ride_count >= 3
        or
        total_confirmed_slots > 5
    )

    # =====================================================
    # CALCULATE TABLE HEIGHT
    # =====================================================

    available_body_height = (
        schedule_max_bottom
        -
        schedule_top
        -
        schedule_header_height
    )

    if compact_mode:

        # Two rows per ride:
        # Ride heading
        # Compact schedule
        required_rows = max(
            ride_count * 2,
            1,
        )

    else:

        required_rows = 0

        for ride_data in ride_schedule_data:

            slot_count = len(
                ride_data["slots"]
            )

            # 1 ride heading + each slot.
            # At least one slot/info line.
            required_rows += (
                1
                +
                max(
                    slot_count,
                    1,
                )
            )

        required_rows = max(
            required_rows,
            1,
        )

    row_height = (
        available_body_height
        //
        required_rows
    )

    # Prevent excessive row height.
    if compact_mode:

        row_height = min(
            row_height,
            23,
        )

        row_height = max(
            row_height,
            17,
        )

    else:

        row_height = min(
            row_height,
            25,
        )

        row_height = max(
            row_height,
            16,
        )

    schedule_bottom = (
        schedule_top
        +
        schedule_header_height
        +
        (
            required_rows
            *
            row_height
        )
    )

    schedule_bottom = min(
        schedule_bottom,
        schedule_max_bottom,
    )

    # =====================================================
    # SCHEDULE CARD
    # =====================================================

    draw.rounded_rectangle(
        (
            schedule_left,
            schedule_top,
            schedule_right,
            schedule_bottom,
        ),
        radius=14,
        fill=WHITE,
        outline=RED,
        width=2,
    )

    # =====================================================
    # RED HEADER
    # =====================================================

    draw.rounded_rectangle(
        (
            schedule_left,
            schedule_top,
            schedule_right,
            schedule_top
            +
            schedule_header_height,
        ),
        radius=14,
        fill=RED,
    )

    # Square lower corners of header.
    draw.rectangle(
        (
            schedule_left,
            schedule_top + 14,
            schedule_right,
            schedule_top
            +
            schedule_header_height,
        ),
        fill=RED,
    )

    schedule_header_font = load_font(
        15,
        bold=True,
    )

    header_text = (
        "ADVENTURE & RIDE SCHEDULE"
    )

    header_bbox = draw.textbbox(
        (
            0,
            0,
        ),
        header_text,
        font=schedule_header_font,
    )

    header_width = (
        header_bbox[2]
        -
        header_bbox[0]
    )

    draw.text(
        (
            schedule_left
            +
            (
                (
                    schedule_right
                    -
                    schedule_left
                )
                -
                header_width
            )
            // 2,

            schedule_top + 5,
        ),
        header_text,
        fill=WHITE,
        font=schedule_header_font,
    )

    # =====================================================
    # SCHEDULE CONTENT
    # =====================================================

    current_y = (
        schedule_top
        +
        schedule_header_height
    )

    # =====================================================
    # NO RIDES
    # =====================================================

    if not ride_schedule_data:

        empty_font = load_font(
            14,
            bold=False,
        )

        draw.text(
            (
                100,
                current_y + 8,
            ),
            "No adventure schedule available.",
            fill=GRAY,
            font=empty_font,
        )

    # =====================================================
    # COMPACT MODE
    # Used primarily for 3 rides
    # =====================================================

    elif compact_mode:

        for ride_index, ride_data in enumerate(
            ride_schedule_data[:3]
        ):

            ride_name = (
                ride_data["ride_name"]
            )

            quantity = (
                ride_data["quantity"]
            )

            confirmed_slots = (
                ride_data["slots"]
            )

            quantity_word = (
                "Rider"
                if quantity == 1
                else "Riders"
            )

            quantity_text = (
                f"{quantity} "
                f"{quantity_word}"
            )

            # ---------------------------------------------
            # RIDE HEADER LINE
            # ---------------------------------------------

            ride_name_font = fit_font(
                ride_name.upper(),
                max_width=680,
                start_size=14,
                minimum_size=10,
                bold=True,
            )

            quantity_font = fit_font(
                quantity_text,
                max_width=180,
                start_size=13,
                minimum_size=10,
                bold=True,
            )

            bullet_size = 6

            bullet_y = (
                current_y
                +
                max(
                    5,
                    (
                        row_height
                        -
                        bullet_size
                    )
                    // 2
                )
            )

            draw.ellipse(
                (
                    105,
                    bullet_y,
                    105 + bullet_size,
                    bullet_y + bullet_size,
                ),
                fill=RED,
            )

            draw.text(
                (
                    130,
                    current_y + 2,
                ),
                ride_name.upper(),
                fill=DARK,
                font=ride_name_font,
            )

            draw.text(
                (
                    910,
                    current_y + 2,
                ),
                quantity_text,
                fill=RED,
                font=quantity_font,
            )

            current_y += (
                row_height
            )

            # ---------------------------------------------
            # COMPACT SLOT LINE
            # ---------------------------------------------

            if confirmed_slots:

                schedule_parts = []

                for slot in confirmed_slots:

                    start_label = format_slot_time(
                        slot.slot_start_time
                    )

                    end_label = format_slot_time(
                        slot.slot_end_time
                    )

                    riders = int(
                        slot.participant_count
                        or
                        0
                    )

                    schedule_parts.append(
                        f"{start_label}-{end_label} "
                        f"({riders})"
                    )

                schedule_text = (
                    "   |   ".join(
                        schedule_parts
                    )
                )

            else:

                schedule_text = (
                    "Confirmed ride schedule "
                    "not available"
                )

            schedule_font = fit_font(
                schedule_text,
                max_width=900,
                start_size=12,
                minimum_size=9,
                bold=False,
            )

            draw.text(
                (
                    130,
                    current_y + 2,
                ),
                schedule_text,
                fill=GRAY,
                font=schedule_font,
            )

            current_y += (
                row_height
            )

            # ---------------------------------------------
            # DIVIDER BETWEEN RIDES
            # ---------------------------------------------

            if (
                ride_index
                <
                min(
                    len(ride_schedule_data),
                    3,
                )
                - 1
            ):

                divider_y = (
                    current_y - 1
                )

                if (
                    divider_y
                    <
                    schedule_bottom
                ):

                    draw.line(
                        (
                            95,
                            divider_y,
                            1065,
                            divider_y,
                        ),
                        fill=DIVIDER,
                        width=1,
                    )

    # =====================================================
    # DETAILED MODE
    # Mainly for 1-2 rides
    # =====================================================

    else:

        for ride_index, ride_data in enumerate(
            ride_schedule_data
        ):

            ride_name = (
                ride_data["ride_name"]
            )

            quantity = (
                ride_data["quantity"]
            )

            confirmed_slots = (
                ride_data["slots"]
            )

            quantity_word = (
                "Rider"
                if quantity == 1
                else "Riders"
            )

            quantity_text = (
                f"{quantity} "
                f"{quantity_word}"
            )

            # ---------------------------------------------
            # RIDE HEADING
            # ---------------------------------------------

            ride_font = fit_font(
                ride_name.upper(),
                max_width=650,
                start_size=15,
                minimum_size=10,
                bold=True,
            )

            ride_quantity_font = fit_font(
                quantity_text,
                max_width=180,
                start_size=14,
                minimum_size=10,
                bold=True,
            )

            bullet_size = 7

            bullet_y = (
                current_y
                +
                max(
                    4,
                    (
                        row_height
                        -
                        bullet_size
                    )
                    // 2
                )
            )

            draw.ellipse(
                (
                    105,
                    bullet_y,
                    105 + bullet_size,
                    bullet_y + bullet_size,
                ),
                fill=RED,
            )

            draw.text(
                (
                    130,
                    current_y + 2,
                ),
                ride_name.upper(),
                fill=DARK,
                font=ride_font,
            )

            draw.text(
                (
                    900,
                    current_y + 2,
                ),
                quantity_text,
                fill=RED,
                font=ride_quantity_font,
            )

            current_y += (
                row_height
            )

            # ---------------------------------------------
            # CONFIRMED SLOT ROWS
            # ---------------------------------------------

            if confirmed_slots:

                for slot_index, slot in enumerate(
                    confirmed_slots
                ):

                    if (
                        current_y
                        +
                        row_height
                        >
                        schedule_bottom
                    ):

                        break

                    start_label = format_slot_time(
                        slot.slot_start_time
                    )

                    end_label = format_slot_time(
                        slot.slot_end_time
                    )

                    slot_time_text = (
                        f"{start_label}"
                        f" - "
                        f"{end_label}"
                    )

                    slot_riders = int(
                        slot.participant_count
                        or
                        0
                    )

                    slot_rider_word = (
                        "Rider"
                        if slot_riders == 1
                        else "Riders"
                    )

                    slot_rider_text = (
                        f"{slot_riders} "
                        f"{slot_rider_word}"
                    )

                    time_font = fit_font(
                        slot_time_text,
                        max_width=500,
                        start_size=13,
                        minimum_size=9,
                        bold=False,
                    )

                    slot_quantity_font = fit_font(
                        slot_rider_text,
                        max_width=180,
                        start_size=13,
                        minimum_size=9,
                        bold=False,
                    )

                    # Small schedule bullet.
                    draw.ellipse(
                        (
                            145,
                            current_y
                            +
                            max(
                                6,
                                row_height // 2 - 2,
                            ),
                            149,
                            current_y
                            +
                            max(
                                6,
                                row_height // 2 - 2,
                            )
                            +
                            4,
                        ),
                        fill=GRAY,
                    )

                    draw.text(
                        (
                            170,
                            current_y + 2,
                        ),
                        slot_time_text,
                        fill=GRAY,
                        font=time_font,
                    )

                    draw.text(
                        (
                            900,
                            current_y + 2,
                        ),
                        slot_rider_text,
                        fill=DARK,
                        font=slot_quantity_font,
                    )

                    current_y += (
                        row_height
                    )

            else:

                no_schedule_font = load_font(
                    11,
                    bold=False,
                )

                draw.text(
                    (
                        170,
                        current_y + 2,
                    ),
                    "Confirmed ride schedule "
                    "not available",
                    fill=GRAY,
                    font=no_schedule_font,
                )

                current_y += (
                    row_height
                )

            # ---------------------------------------------
            # DIVIDER BETWEEN RIDES
            # ---------------------------------------------

            if (
                ride_index
                <
                len(ride_schedule_data) - 1
            ):

                divider_y = (
                    current_y - 1
                )

                if (
                    divider_y
                    <
                    schedule_bottom
                ):

                    draw.line(
                        (
                            95,
                            divider_y,
                            1065,
                            divider_y,
                        ),
                        fill=DIVIDER,
                        width=1,
                    )

    # =====================================================
    # QR CODE
    # =====================================================
    #
    # QR border already exists in static background.
    # Do not draw another border.
    #
    # =====================================================

    if not ticket.qr_image:

        raise ValueError(
            "Ticket QR image does not exist."
        )

    qr_path = (
        ticket.qr_image.path
    )

    if not os.path.exists(
        qr_path
    ):

        raise FileNotFoundError(
            f"Ticket QR file not found: {qr_path}"
        )

    qr = (
        Image.open(
            qr_path
        )
        .convert("RGB")
    )

    # =====================================================
    # QR SIZE
    # =====================================================

    qr_size = 230

    qr = qr.resize(
        (
            qr_size,
            qr_size,
        ),
        Image.Resampling.NEAREST,
    )

    # =====================================================
    # QR POSITION
    # =====================================================

    qr_x = 1285
    qr_y = 220

    image.paste(
        qr,
        (
            qr_x,
            qr_y,
        ),
    )

    # =====================================================
    # SAVE FINAL PNG
    # =====================================================

    buffer = BytesIO()

    if image.mode != "RGB":
       image = image.convert("RGB")

    image.save(
    buffer,
    format="JPEG",
    quality=90,
    optimize=True,
)

    buffer.seek(0)

    # =====================================================
    # OUTPUT FILE NAME
    # =====================================================

    filename = (
        f"whatsapp-ticket-"
        f"{ticket.ticket_id}.png"
    )

    # =====================================================
    # DELETE OLD GENERATED IMAGE
    # =====================================================

    if ticket.whatsapp_ticket_image:

        try:

            ticket.whatsapp_ticket_image.delete(
                save=False
            )

        except Exception as delete_error:

            print(
                "OLD WHATSAPP TICKET "
                "DELETE ERROR:",
                repr(
                    delete_error
                ),
            )

    # =====================================================
    # SAVE NEW IMAGE
    # =====================================================

    ticket.whatsapp_ticket_image.save(
        filename,
        ContentFile(
            buffer.getvalue()
        ),
        save=False,
    )

    ticket.save(
        update_fields=[
            "whatsapp_ticket_image",
        ]
    )

    # =====================================================
    # DEBUG
    # =====================================================

    print(
        "\n========================================"
    )

    print(
        "HORIZONTAL WHATSAPP TICKET GENERATED"
    )

    print(
        "BOOKING:",
        booking.booking_id,
    )

    print(
        "TICKET:",
        ticket.ticket_number,
    )

    print(
        "RIDES:",
        ride_count,
    )

    print(
        "TOTAL PARTICIPANTS:",
        total_participants,
    )

    print(
        "CONFIRMED SLOT ROWS:",
        total_confirmed_slots,
    )

    print(
        "SCHEDULE MODE:",
        (
            "COMPACT"
            if compact_mode
            else "DETAILED"
        ),
    )

    print(
        "BOOKING CARD:",
        info_top,
        "->",
        info_bottom,
    )

    print(
        "SCHEDULE:",
        schedule_top,
        "->",
        schedule_bottom,
    )

    print(
        "FOOTER PROTECTION:",
        schedule_max_bottom,
    )

    # =====================================================
    # PRINT SCHEDULE DETAILS
    # =====================================================

    print(
        "RIDE SCHEDULE:"
    )

    for ride_data in ride_schedule_data:

        print(
            " -",
            ride_data["ride_name"],
            f"({ride_data['quantity']} riders)"
        )

        if ride_data["slots"]:

            for slot in ride_data["slots"]:

                print(
                    "    ",
                    format_slot_time(
                        slot.slot_start_time
                    ),
                    "-",
                    format_slot_time(
                        slot.slot_end_time
                    ),
                    "=",
                    slot.participant_count,
                    "rider(s)",
                )

        else:

            print(
                "     NO CONFIRMED SLOTS"
            )

    print(
        "QR:",
        f"{qr_x},{qr_y}",
        f"{qr_size}x{qr_size}",
    )

    print(
        "IMAGE:",
        ticket.whatsapp_ticket_image.name,
    )

    print(
        "========================================\n"
    )

    return True



def generate_ticket_pdf(ticket):

    """
    Generate the PDF ticket using the same designed
    ticket image used for WhatsApp.

    Result:
        Designed ticket image
                ↓
        One-page landscape PDF
                ↓
        ticket.pdf_ticket
    """

    # =====================================================
    # IMPORTS
    # =====================================================

    from io import BytesIO

    from django.core.files.base import ContentFile

    from PIL import Image

    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader


    # =====================================================
    # 1. MAKE SURE DESIGNED TICKET IMAGE EXISTS
    # =====================================================

    if not ticket.whatsapp_ticket_image:

        generate_whatsapp_ticket_image(
            ticket
        )

        ticket.refresh_from_db()


    # =====================================================
    # 2. VALIDATE IMAGE
    # =====================================================

    if not ticket.whatsapp_ticket_image:

        raise ValueError(
            "WhatsApp ticket image could not be generated."
        )


    image_path = (
        ticket.whatsapp_ticket_image.path
    )


    # =====================================================
    # 3. READ IMAGE SIZE
    # =====================================================

    with Image.open(
        image_path
    ) as ticket_image:

        image_width, image_height = (
            ticket_image.size
        )


    if (
        image_width <= 0
        or
        image_height <= 0
    ):

        raise ValueError(
            "Invalid ticket image dimensions."
        )


    # =====================================================
    # 4. CREATE PDF BUFFER
    # =====================================================

    buffer = BytesIO()


    # =====================================================
    # 5. CREATE PDF WITH SAME ASPECT RATIO
    #
    # The designed ticket is 1600 x 900.
    #
    # Instead of forcing it into portrait A4,
    # make the PDF page use the same ratio.
    # =====================================================

    pdf_width = float(
        image_width
    )

    pdf_height = float(
        image_height
    )


    pdf = canvas.Canvas(
        buffer,
        pagesize=(
            pdf_width,
            pdf_height,
        ),
    )


    pdf.setTitle(
        f"Flying Fox Ticket "
        f"{ticket.ticket_number}"
    )


    # =====================================================
    # 6. DRAW DESIGNED TICKET IMAGE
    # =====================================================

    pdf.drawImage(
        ImageReader(
            image_path
        ),

        0,
        0,

        width=
            pdf_width,

        height=
            pdf_height,

        preserveAspectRatio=
            True,

        mask=
            "auto",
    )


    # =====================================================
    # 7. FINISH PDF
    # =====================================================

    pdf.showPage()

    pdf.save()

    buffer.seek(
        0
    )


    # =====================================================
    # 8. SAVE PDF TO TICKET MODEL
    # =====================================================

    ticket.pdf_ticket.save(

        (
            f"ticket-"
            f"{ticket.ticket_number}.pdf"
        ),

        ContentFile(
            buffer.getvalue()
        ),

        save=False,
    )


    # =====================================================
    # 9. SAVE TICKET
    # =====================================================

    ticket.save(
        update_fields=[
            "pdf_ticket",
        ]
    )


    print()
    print(
        "=========================================="
    )
    print(
        "DESIGNED TICKET PDF GENERATED"
    )
    print(
        "=========================================="
    )
    print(
        "TICKET:",
        ticket.ticket_number,
    )
    print(
        "IMAGE:",
        ticket.whatsapp_ticket_image.name,
    )
    print(
        "PDF:",
        ticket.pdf_ticket.name,
    )
    print(
        "SIZE:",
        f"{image_width}x{image_height}",
    )
    print(
        "=========================================="
    )
    print()


    return ticket.pdf_ticket




def send_ticket_email(ticket):
    """
    Send the confirmed Flying Fox booking ticket by email.

    Multi-ride + time-slot version:
    - One email per booking
    - One ticket number
    - One visit date
    - Lists every selected ride
    - Lists confirmed scheduled ride slots
    - Lists weight groups for each ride
    - Shows offer/discount per ride
    - Attaches the generated PDF ticket
    """

    # =====================================================
    # BOOKING WITH ALL MULTI-RIDE + SLOT DATA
    # =====================================================

    try:

        booking = (
            Booking.objects
            .prefetch_related(
                "ride_items__ride",
                "ride_items__ride_price",
                "ride_items__offer",
                "ride_items__weight_groups",
                "ride_items__allocated_slots",
            )
            .get(
                pk=ticket.booking_id
            )
        )

    except Booking.DoesNotExist:

        print(
            "TICKET EMAIL ERROR: "
            "Booking does not exist."
        )

        return False


    # =====================================================
    # DO NOT SEND ACTIVE TICKET FOR CANCELLED BOOKING
    # =====================================================

    if booking.status == "cancelled":

        print(
            "TICKET EMAIL SKIPPED: "
            "Booking is cancelled."
        )

        return False


    # =====================================================
    # CUSTOMER EMAIL
    # =====================================================

    customer_email = (
        booking.customer_email
        or
        ""
    ).strip()


    if not customer_email:

        print(
            "TICKET EMAIL SKIPPED: "
            "Customer email is empty."
        )

        return False


    # =====================================================
    # RIDE ITEMS
    # =====================================================

    ride_items = list(
        booking.ride_items.all()
    )


    if not ride_items:

        print(
            "TICKET EMAIL ERROR: "
            "Booking has no ride items."
        )

        return False


    # =====================================================
    # EMAIL SUBJECT
    # =====================================================

    subject = (
        f"Flying Fox Adventure Ticket "
        f"#{ticket.ticket_number}"
    )


    # =====================================================
    # BUILD EMAIL BODY
    # =====================================================

    lines = []


    lines.append(
        f"Hi {booking.customer_name},"
    )


    lines.append("")


    lines.append(
        "Your Flying Fox Adventure booking "
        "has been confirmed successfully."
    )


    lines.append("")


    # =====================================================
    # BOOKING DETAILS
    # =====================================================

    lines.append(
        "BOOKING DETAILS"
    )


    lines.append(
        "----------------------------------------"
    )


    lines.append(
        f"Ticket Number: "
        f"{ticket.ticket_number}"
    )


    lines.append(
        f"Booking ID: "
        f"{booking.booking_id}"
    )


    lines.append(
        f"Visit Date: "
        f"{booking.booking_date.strftime('%d %B %Y')}"
    )


    lines.append(
        f"Total Adventures: "
        f"{len(ride_items)}"
    )


    lines.append(
        f"Total Riders: "
        f"{booking.quantity}"
    )


    lines.append("")


    # =====================================================
    # SELECTED ADVENTURES
    # =====================================================

    lines.append(
        "SELECTED ADVENTURES"
    )


    lines.append(
        "----------------------------------------"
    )


    for index, item in enumerate(
        ride_items,
        start=1,
    ):

        # =============================================
        # RIDE
        # =============================================

        lines.append("")


        lines.append(
            f"{index}. {item.ride.name}"
        )


        lines.append(
            f"   Riders: "
            f"{item.quantity}"
        )


        lines.append(
            f"   Price per rider: "
            f"INR {item.price_per_person}"
        )


        lines.append(
            f"   Subtotal: "
            f"INR {item.subtotal}"
        )


        # =============================================
        # OFFER
        # =============================================

        if item.offer:

            lines.append(
                f"   Offer: "
                f"{item.offer.title}"
            )


            if item.applied_coupon_code:

                lines.append(
                    f"   Coupon: "
                    f"{item.applied_coupon_code}"
                )


            lines.append(
                f"   Discount: "
                f"INR {item.discount_amount}"
            )


        # =============================================
        # RIDE TOTAL
        # =============================================

        lines.append(
            f"   Ride Total: "
            f"INR {item.total_amount}"
        )


        # =============================================
        # CONFIRMED SCHEDULED RIDE TIMES
        # =============================================

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


        if confirmed_slots:

            lines.append("")

            lines.append(
                "   Scheduled Ride Time:"
            )


            total_scheduled_riders = 0


            for slot in confirmed_slots:

                start_label = (
                    slot
                    .slot_start_time
                    .strftime(
                        "%I:%M %p"
                    )
                )


                end_label = (
                    slot
                    .slot_end_time
                    .strftime(
                        "%I:%M %p"
                    )
                )


                participant_count = (
                    slot.participant_count
                )


                total_scheduled_riders += (
                    participant_count
                )


                rider_word = (
                    "rider"
                    if participant_count == 1
                    else "riders"
                )


                lines.append(
                    (
                        f"      - "
                        f"{start_label} - "
                        f"{end_label}: "
                        f"{participant_count} "
                        f"{rider_word}"
                    )
                )


            lines.append(
                (
                    f"   Total Scheduled Riders: "
                    f"{total_scheduled_riders}"
                )
            )


        else:

            # This should normally never happen for a
            # confirmed booking, but keep the email safe.

            lines.append("")

            lines.append(
                "   Scheduled Ride Time: "
                "Not available"
            )


        # =============================================
        # WEIGHT GROUPS
        # =============================================

        weight_groups = list(
            item.weight_groups.all()
        )


        if weight_groups:

            lines.append("")

            lines.append(
                "   Participant Weight Groups:"
            )


            for group in weight_groups:

                lines.append(
                    (
                        f"      - "
                        f"{group.label}: "
                        f"{group.participant_count} "
                        f"rider(s)"
                    )
                )


        # =============================================
        # RIDE SEPARATOR
        # =============================================

        if index < len(
            ride_items
        ):

            lines.append("")

            lines.append(
                "   ------------------------------------"
            )


    # =====================================================
    # PAYMENT SUMMARY
    # =====================================================

    lines.append("")


    lines.append(
        "PAYMENT SUMMARY"
    )


    lines.append(
        "----------------------------------------"
    )


    lines.append(
        f"Subtotal: "
        f"INR {booking.subtotal}"
    )


    lines.append(
        f"Total Discount: "
        f"INR {booking.discount_amount}"
    )


    lines.append(
        f"Total Paid: "
        f"INR {booking.total_amount}"
    )


    lines.append("")


    # =====================================================
    # IMPORTANT INFORMATION
    # =====================================================

    lines.append(
        "IMPORTANT INFORMATION"
    )


    lines.append(
        "----------------------------------------"
    )


    lines.append(
        "• Your QR ticket is valid for all "
        "adventures listed in this booking."
    )


    lines.append(
        "• Please follow the scheduled ride times "
        "shown above."
    )


    lines.append(
        "• Please show the QR ticket at the "
        "Flying Fox Adventure counter."
    )


    lines.append(
        "• Please arrive at least 30 minutes "
        "before your visit."
    )


    lines.append(
        "• Please follow all safety instructions "
        "provided by our adventure staff."
    )


    lines.append(
        "• Participant eligibility is subject "
        "to the applicable safety and weight requirements."
    )


    lines.append("")


    lines.append(
        "Your PDF ticket is attached to this email."
    )


    lines.append("")


    lines.append(
        "Thank you for choosing "
        "Flying Fox Adventure Munnar!"
    )


    lines.append("")


    lines.append(
        "Flying Fox Adventure"
    )


    lines.append(
        "Munnar, Kerala"
    )


    # =====================================================
    # FINAL BODY
    # =====================================================

    message_body = "\n".join(
        lines
    )


    # =====================================================
    # FROM EMAIL
    # =====================================================

    from_email = getattr(
        settings,
        "DEFAULT_FROM_EMAIL",
        None,
    )


    if not from_email:

        from_email = getattr(
            settings,
            "EMAIL_HOST_USER",
            None,
        )


    if not from_email:

        print(
            "TICKET EMAIL ERROR: "
            "DEFAULT_FROM_EMAIL / EMAIL_HOST_USER "
            "is not configured."
        )

        return False


    # =====================================================
    # CREATE EMAIL
    # =====================================================

    email = EmailMessage(

        subject=
            subject,

        body=
            message_body,

        from_email=
            from_email,

        to=[
            customer_email
        ],
    )


    # =====================================================
    # ATTACH PDF TICKET
    # =====================================================

    try:

        if ticket.pdf_ticket:

            # =============================================
            # OPEN STORAGE FILE
            #
            # This works with local storage and is also
            # safer if remote storage is used later.
            # =============================================

            ticket.pdf_ticket.open(
                "rb"
            )


            pdf_content = (
                ticket.pdf_ticket.read()
            )


            ticket.pdf_ticket.close()


            email.attach(

                (
                    f"Flying-Fox-Ticket-"
                    f"{ticket.ticket_number}.pdf"
                ),

                pdf_content,

                "application/pdf",
            )


        else:

            print(
                "TICKET EMAIL WARNING: "
                "PDF ticket is not available."
            )


    except Exception as error:

        print(
            "\n========================================"
        )


        print(
            "TICKET EMAIL PDF ATTACH ERROR"
        )


        print(
            "TYPE:",
            type(error).__name__
        )


        print(
            "ERROR:",
            repr(error)
        )


        print(
            "TICKET:",
            ticket.ticket_number
        )


        print(
            "========================================\n"
        )

        # Do not stop the email just because
        # PDF attachment failed.


    # =====================================================
    # SEND EMAIL
    # =====================================================

    try:

        sent_count = email.send(
            fail_silently=False
        )


        email_sent = (
            sent_count > 0
        )


        # =================================================
        # DEBUG
        # =================================================

        print(
            "\n========================================"
        )


        print(
            "TICKET EMAIL RESULT"
        )


        print(
            "TICKET:",
            ticket.ticket_number
        )


        print(
            "BOOKING:",
            booking.booking_id
        )


        print(
            "CUSTOMER:",
            booking.customer_name
        )


        print(
            "EMAIL:",
            customer_email
        )


        print(
            "RIDES:",
            ", ".join(
                [
                    item.ride.name

                    for item
                    in ride_items
                ]
            )
        )


        print(
            "RIDE COUNT:",
            len(
                ride_items
            )
        )


        print(
            "TOTAL RIDERS:",
            booking.quantity
        )


        print(
            "TOTAL:",
            booking.total_amount
        )


        # =============================================
        # SLOT DEBUG
        # =============================================

        slot_debug = []


        for item in ride_items:

            for slot in (
                item.allocated_slots.all()
            ):

                if (
                    slot.status
                    !=
                    "confirmed"
                ):

                    continue


                slot_debug.append(
                    (
                        f"{item.ride.name}: "
                        f"{slot.slot_start_time.strftime('%I:%M %p')}"
                        f" - "
                        f"{slot.slot_end_time.strftime('%I:%M %p')}"
                        f" = "
                        f"{slot.participant_count} rider(s)"
                    )
                )


        print(
            "SCHEDULE:"
        )


        if slot_debug:

            for schedule_line in slot_debug:

                print(
                    " -",
                    schedule_line
                )

        else:

            print(
                " - No confirmed slots found."
            )


        print(
            "SENT:",
            email_sent
        )


        print(
            "========================================\n"
        )


        return email_sent


    except Exception as error:

        print(
            "\n========================================"
        )


        print(
            "TICKET EMAIL SEND ERROR"
        )


        print(
            "TYPE:",
            type(error).__name__
        )


        print(
            "ERROR:",
            repr(error)
        )


        print(
            "TICKET:",
            ticket.ticket_number
        )


        print(
            "BOOKING:",
            booking.booking_id
        )


        print(
            "EMAIL:",
            customer_email
        )


        print(
            "========================================\n"
        )


        return False


def booking_success(
    request,
    booking_id,
):

    # =====================================================
    # BOOKING
    #
    # Load:
    # - parent booking
    # - rides
    # - prices
    # - offers
    # - weight groups
    # - confirmed ride slot allocations
    # =====================================================

    booking = get_object_or_404(

        Booking.objects

        .select_related(
            "user",
        )

        .prefetch_related(
            "ride_items__ride",
            "ride_items__ride_price",
            "ride_items__offer",
            "ride_items__weight_groups",

            # =============================================
            # NEW:
            # Scheduled ride slots
            # =============================================
            "ride_items__allocated_slots",
        ),

        booking_id=
            booking_id,

        status__in=[
            "confirmed",
            "checked_in",
        ],
    )


    # =====================================================
    # TICKET
    # =====================================================

    ticket = get_object_or_404(
        Ticket,
        booking=
            booking,
    )


    # =====================================================
    # RIDE ITEMS
    # =====================================================

    ride_items = list(
        booking.ride_items.all()
    )


    # =====================================================
    # PREPARE CONFIRMED SLOT SCHEDULE
    #
    # Attach a simple display-safe list to each
    # BookingRideItem.
    #
    # Example:
    #
    # 01:30 PM - 02:30 PM → 5 riders
    # 02:30 PM - 03:30 PM → 5 riders
    # =====================================================

    for item in ride_items:

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


        item.confirmed_slots = (
            confirmed_slots
        )


    # =====================================================
    # RIDE NAMES
    # =====================================================

    ride_names = ", ".join(
        [
            item.ride.name

            for item
            in ride_items

            if item.ride
        ]
    )


    # =====================================================
    # TOTAL RIDE COUNT
    # =====================================================

    ride_count = len(
        ride_items
    )


    # =====================================================
    # CONTEXT
    # =====================================================

    return render(
        request,
        "frontend/booking_success.html",
        {
            "booking":
                booking,

            "ticket":
                ticket,

            "ride_items":
                ride_items,

            "ride_names":
                ride_names,

            "ride_count":
                ride_count,

            # Automatically open QR modal
            "show_ticket_modal":
                True,
        }
    )




def send_ticket_sms(ticket):

    """
    Send payment confirmation SMS through Telinfy
    after successful Razorpay payment and ticket creation.
    """

    booking = ticket.booking

    # =====================================================
    # 1. CUSTOMER PHONE
    # =====================================================

    if not booking.customer_phone:

        print(
            "PAYMENT SMS ERROR: "
            "Customer phone is empty."
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

    phone_number = (
        booking.customer_phone
        .strip()
    )

    # =====================================================
    # 2. BOOKING ID
    # =====================================================

    full_booking_id = str(
        booking.booking_id
    )

    booking_id = (
        "FFX-"
        +
        full_booking_id[:8].upper()
    )

    # =====================================================
    # 3. AMOUNT
    # =====================================================

    total_amount = (
        booking.total_amount
        or
        0
    )

    amount = (
        f"{total_amount:.2f}"
        .rstrip("0")
        .rstrip(".")
    )

    # =====================================================
    # 4. VISIT DATE
    # =====================================================

    if booking.booking_date:

        visit_date = (
            booking.booking_date.strftime(
                "%d-%m-%Y"
            )
        )

    else:

        visit_date = ""

    # =====================================================
    # 5. SEND TELINFY PAYMENT CONFIRMATION
    # =====================================================

    try:

        response = (
            send_payment_confirmation_sms(
                phone_number=phone_number,
                booking_id=booking_id,
                amount=amount,
                visit_date=visit_date,
            )
        )

        # =================================================
        # 6. CHECK TELINFY RESPONSE
        # =================================================

        responses = []

        if isinstance(
            response,
            dict,
        ):

            responses = (
                response.get(
                    "responses",
                    []
                )
            )

        if not responses:

            ticket.sms_sent = False
            ticket.sms_status = "failed"

            ticket.save(
                update_fields=[
                    "sms_sent",
                    "sms_status",
                ]
            )

            print(
                "PAYMENT SMS ERROR: "
                "No Telinfy response."
            )

            return False

        first_response = (
            responses[0]
        )

        status = str(
            first_response.get(
                "status",
                ""
            )
        ).strip().lower()

        if status != "success":

            ticket.sms_sent = False
            ticket.sms_status = "failed"

            ticket.save(
                update_fields=[
                    "sms_sent",
                    "sms_status",
                ]
            )

            print(
                "PAYMENT SMS ERROR:",
                response,
            )

            return False

        # =================================================
        # 7. SUCCESS
        # =================================================

        ticket.sms_sent = True
        ticket.sms_status = "sent"

        ticket.save(
            update_fields=[
                "sms_sent",
                "sms_status",
            ]
        )

        print()
        print(
            "========== PAYMENT SMS SENT =========="
        )
        print(
            "TO:",
            phone_number,
        )
        print(
            "BOOKING:",
            booking_id,
        )
        print(
            "AMOUNT:",
            amount,
        )
        print(
            "VISIT DATE:",
            visit_date,
        )
        print(
            "======================================"
        )
        print()

        return True

    except Exception as error:

        ticket.sms_sent = False
        ticket.sms_status = "error"

        ticket.save(
            update_fields=[
                "sms_sent",
                "sms_status",
            ]
        )

        print()
        print(
            "======= PAYMENT SMS FAILED ======="
        )
        print(
            "TO:",
            phone_number,
        )
        print(
            "ERROR:",
            repr(error),
        )
        print(
            "=================================="
        )
        print()

        return False



def download_ticket(
    request,
    ticket_id,
):

    # =====================================================
    # GET TICKET
    #
    # No login is required.
    #
    # ticket_id is a UUID and is used as the private
    # download identifier.
    # =====================================================

    ticket = get_object_or_404(

        Ticket.objects
        .select_related(
            "booking",
            "booking__user",
        ),

        ticket_id=ticket_id,
    )


    # =====================================================
    # CANCELLED BOOKING
    #
    # A cancelled/refunded booking must never allow
    # downloading an old valid-looking ticket.
    # =====================================================

    if (
        ticket.booking.status
        ==
        "cancelled"
    ):

        messages.error(
            request,
            (
                "This ticket has been cancelled "
                "and is no longer valid."
            )
        )

        # Customer may not be logged in, so don't send
        # them to user_tickets.
        return redirect(
            "booking_success",
            booking_id=
                ticket.booking.booking_id,
        )


    # =====================================================
    # TICKET PDF MUST EXIST
    # =====================================================

    if not ticket.pdf_ticket:

        messages.error(
            request,
            "Ticket PDF is not available."
        )

        return redirect(
            "booking_success",
            booking_id=
                ticket.booking.booking_id,
        )


    # =====================================================
    # OPEN PDF FILE
    # =====================================================

    try:

        pdf_file = (
            ticket.pdf_ticket.open(
                "rb"
            )
        )

    except (
        FileNotFoundError,
        OSError,
        ValueError,
    ):

        raise Http404(
            "Ticket PDF could not be found."
        )


    # =====================================================
    # DOWNLOAD FILE
    # =====================================================

    filename = (
        f"flying-fox-ticket-"
        f"{ticket.ticket_number}.pdf"
    )


    return FileResponse(
        pdf_file,
        as_attachment=True,
        filename=filename,
        content_type="application/pdf",
    )


# ==========================================
# STATIC FRONTEND PAGES
# ==========================================

def about(request):

    testimonials = (
        Testimonial.objects
        .all()
        .order_by("-created_at")[:10]
    )

    mission_gallery_images = (
        GalleryItem.objects
        .filter(image__isnull=False)
        .exclude(image="")
        .select_related("category")
        .order_by("-uploaded_at")[:10]
    )

    return render(request, "frontend/about.html", {"testimonials": testimonials,   "mission_gallery_images": mission_gallery_images,})


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


from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect

from .forms import ContactEnquiryForm


def contact(request):

    if request.method == "POST":

        form = ContactEnquiryForm(
            request.POST
        )

        if form.is_valid():

            # ==================================
            # SAVE TO DATABASE FIRST
            # ==================================

            enquiry = form.save(
                commit=False
            )

            enquiry.email_sent = False

            enquiry.save()


            try:

                # ==================================
                # EMAIL 1:
                # SEND ENQUIRY TO FLYING FOX
                # ==================================

                admin_email = EmailMessage(

                    subject=(
                        f"Flying Fox Enquiry: "
                        f"{enquiry.subject}"
                    ),

                    body=f"""
New Contact Enquiry

Name:
{enquiry.name}

Email:
{enquiry.email}

Subject:
{enquiry.subject}

Message:
{enquiry.message}

Enquiry ID:
#{enquiry.id}
""",

                    from_email=settings.DEFAULT_FROM_EMAIL,

                    to=[
                        settings.CONTACT_RECEIVER_EMAIL
                    ],

                    # Clicking Reply in Gmail
                    # replies directly to customer
                    reply_to=[
                        enquiry.email
                    ],

                )


                admin_email.send(
                    fail_silently=False
                )


                # ==================================
                # EMAIL 2:
                # CONFIRMATION TO CUSTOMER
                # ==================================

                customer_email = EmailMessage(

                    subject=(
                        "We received your Flying Fox enquiry"
                    ),

                    body=f"""
Hi {enquiry.name},

Thank you for contacting Flying Fox Adventure.

We have received your enquiry regarding:

{enquiry.subject}

Our adventure team will review your message
and get back to you as soon as possible.

Your Enquiry ID:
#{enquiry.id}

Regards,

Flying Fox Adventure
Munnar, Kerala
""",

                    from_email=settings.DEFAULT_FROM_EMAIL,

                    to=[
                        enquiry.email
                    ],

                )


                customer_email.send(
                    fail_silently=False
                )


                # ==================================
                # BOTH EMAILS SENT
                # ==================================

                enquiry.email_sent = True

                enquiry.save(
                    update_fields=[
                        "email_sent"
                    ]
                )


                messages.success(
                    request,
                    (
                        "Thank you! Your enquiry "
                        "has been submitted successfully."
                    )
                )


            except Exception as error:

                print(
                    "CONTACT EMAIL ERROR:",
                    repr(error)
                )

                # The database enquiry remains saved
                # even when email fails.

                messages.warning(
                    request,
                    (
                        "Your enquiry has been saved. "
                        "Our team will contact you shortly."
                    )
                )


            return redirect(
                "contact"
            )


    else:

        form = ContactEnquiryForm()


    return render(
        request,
        "frontend/contact.html",
        {
            "form": form,
        }
    )



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


def page_404(request, exception=None):
    return render(
        request,
        "frontend/404.html",
        status=404
    )



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

# =========================================================
# CHATBOT SUPPORTED LANGUAGES
# =========================================================

SUPPORTED_CHAT_LANGUAGES = {
    "en": "English",
    "ml": "Malayalam",
    "hi": "Hindi",
    "ta": "Tamil",
}    


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
        onboarding_step="language",
        language="en",
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


def is_valid_multilingual_name(name):
    """
    Validate names written in English, Malayalam,
    Hindi and Tamil.

    Unicode:
    L = Letter
    M = Combining mark
    """

    name = str(name or "").strip()

    if len(name) < 2:
        return False

    has_letter = False

    allowed_characters = {
        " ",
        ".",
        "'",
        "-",
    }

    for char in name:

        if char in allowed_characters:
            continue

        category = unicodedata.category(char)

        # Normal Unicode letters
        if category.startswith("L"):
            has_letter = True
            continue

        # Combining marks are required for
        # Malayalam / Hindi / Tamil vowel signs.
        if category.startswith("M"):
            continue

        return False

    return has_letter


# =========================================================
# CHATBOT EMAIL SKIP VALUES
# =========================================================

CHATBOT_EMAIL_SKIP_VALUES = {

    "en": {
        "skip",
        "no",
        "no thanks",
        "not now",
        "later",
    },

    "ml": {
        "skip",
        "വേണ്ട",
        "ഇല്ല",
        "പിന്നീട്",
        "ഇപ്പോൾ വേണ്ട",
        "നന്ദി വേണ്ട",
    },

    "hi": {
        "skip",
        "नहीं",
        "नही",
        "अभी नहीं",
        "बाद में",
    },

    "ta": {
        "skip",
        "வேண்டாம்",
        "இல்லை",
        "பிறகு",
        "இப்போது வேண்டாம்",
    },
}


def is_chatbot_email_skip(
    message,
    language,
):

    normalized_message = (
        str(message or "")
        .strip()
        .casefold()
    )


    language_values = (
        CHATBOT_EMAIL_SKIP_VALUES.get(
            language,
            CHATBOT_EMAIL_SKIP_VALUES["en"],
        )
    )


    return (
        normalized_message
        in language_values
    )



@require_POST
def chatbot_message(request):

    # =====================================================
    # 1. READ JSON REQUEST
    # =====================================================

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


    user_message = str(
        payload.get("message", "")
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


    # =====================================================
    # 2. GET / CREATE CHAT SESSION
    # =====================================================

    chat_session = get_or_create_chat_session(
        request
    )


    # =====================================================
    # 3. LANGUAGE SELECTION
    # =====================================================

    if chat_session.onboarding_step == "language":

        selected_language = str(
            payload.get("language")
            or user_message
        ).strip().lower()


        if (
            selected_language
            not in SUPPORTED_CHAT_LANGUAGES
        ):

            return JsonResponse(
                {
                    "success": True,

                    "response": (
                        "Please choose your "
                        "preferred language."
                    ),

                    "response_type": "language",

                    "onboarding_step": "language",

                    "show_language_options": True,

                    "languages": [
                        {
                            "code": "en",
                            "name": "English",
                        },
                        {
                            "code": "ml",
                            "name": "മലയാളം",
                        },
                        {
                            "code": "hi",
                            "name": "हिंदी",
                        },
                        {
                            "code": "ta",
                            "name": "தமிழ்",
                        },
                    ],

                    "show_quick_replies": False,
                }
            )


        # Save language
        chat_session.language = selected_language
        chat_session.onboarding_step = "name"

        chat_session.save(
            update_fields=[
                "language",
                "onboarding_step",
                "updated_at",
            ]
        )


        ChatMessage.objects.create(
            session=chat_session,
            sender="user",
            message=SUPPORTED_CHAT_LANGUAGES[
                selected_language
            ],
            language=selected_language,
            intent="language_selected",
        )


        # IMPORTANT:
        # Direct local multilingual response.
        # NO TRANSLATOR.

        bot_response = get_response(
            "ask_name",
            selected_language,
        )


        ChatMessage.objects.create(
            session=chat_session,
            sender="bot",
            message=bot_response,
            translated_message="",
            language=selected_language,
            intent="collect_name",
        )


        return JsonResponse(
            {
                "success": True,
                "response": bot_response,
                "response_type": "text",
                "onboarding_step": "name",
                "language": selected_language,
                "show_language_options": False,
                "show_quick_replies": False,
            }
        )


    # =====================================================
    # 4. STORE USER MESSAGE
    # =====================================================

    user_chat_message = ChatMessage.objects.create(
        session=chat_session,
        sender="user",
        message=user_message,
        translated_message="",
        language=chat_session.language,
    )


    # =====================================================
    # 5. ONBOARDING — NAME
    # =====================================================

    if chat_session.onboarding_step == "name":

        full_name = user_message.strip()


        # Minimum length
        if len(full_name) < 2:

            bot_response = get_response(
                "invalid_name",
                chat_session.language,
            )


            ChatMessage.objects.create(
                session=chat_session,
                sender="bot",
                message=bot_response,
                translated_message="",
                language=chat_session.language,
                intent="collect_name",
            )


            return JsonResponse(
                {
                    "success": True,
                    "response": bot_response,
                    "response_type": "text",
                    "onboarding_step": "name",
                    "language": chat_session.language,
                    "show_quick_replies": False,
                }
            )


        # Multilingual validation
        if not is_valid_multilingual_name(
            full_name
        ):

            bot_response = get_response(
                "invalid_name",
                chat_session.language,
            )


            ChatMessage.objects.create(
                session=chat_session,
                sender="bot",
                message=bot_response,
                translated_message="",
                language=chat_session.language,
                intent="collect_name",
            )


            return JsonResponse(
                {
                    "success": True,
                    "response": bot_response,
                    "response_type": "text",
                    "onboarding_step": "name",
                    "language": chat_session.language,
                    "show_quick_replies": False,
                }
            )


        # Save name
        chat_session.customer_name = full_name
        chat_session.onboarding_step = "phone"

        chat_session.save(
            update_fields=[
                "customer_name",
                "onboarding_step",
                "updated_at",
            ]
        )


        bot_response = get_response(
            "ask_phone",
            chat_session.language,
            name=full_name,
        )


        ChatMessage.objects.create(
            session=chat_session,
            sender="bot",
            message=bot_response,
            translated_message="",
            language=chat_session.language,
            intent="collect_phone",
        )


        return JsonResponse(
            {
                "success": True,
                "response": bot_response,
                "response_type": "text",
                "onboarding_step": "phone",
                "language": chat_session.language,
                "show_quick_replies": False,
            }
        )


    # =====================================================
    # 6. ONBOARDING — PHONE
    # =====================================================

    if chat_session.onboarding_step == "phone":

        phone = clean_indian_phone(
            user_message
        )


        if not phone:

            bot_response = get_response(
                "invalid_phone",
                chat_session.language,
            )


            ChatMessage.objects.create(
                session=chat_session,
                sender="bot",
                message=bot_response,
                translated_message="",
                language=chat_session.language,
                intent="collect_phone",
            )


            return JsonResponse(
                {
                    "success": True,
                    "response": bot_response,
                    "response_type": "text",
                    "onboarding_step": "phone",
                    "language": chat_session.language,
                    "show_quick_replies": False,
                }
            )


        # Save phone
        chat_session.customer_phone = phone
        chat_session.onboarding_step = "email"

        chat_session.save(
            update_fields=[
                "customer_phone",
                "onboarding_step",
                "updated_at",
            ]
        )


        bot_response = get_response(
            "ask_email",
            chat_session.language,
        )


        ChatMessage.objects.create(
            session=chat_session,
            sender="bot",
            message=bot_response,
            translated_message="",
            language=chat_session.language,
            intent="collect_email",
        )


        return JsonResponse(
            {
                "success": True,
                "response": bot_response,
                "response_type": "text",
                "onboarding_step": "email",
                "language": chat_session.language,
                "show_quick_replies": False,
            }
        )


    # =====================================================
    # 7. ONBOARDING — EMAIL
    # =====================================================

    if chat_session.onboarding_step == "email":

        submitted_email = user_message.strip()

        normalized_value = (
            submitted_email
            .strip()
            .lower()
        )


        # -------------------------------------------------
        # Local multilingual skip values
        # -------------------------------------------------

        skip_values = {

            # English
            "skip",
            "no",
            "no thanks",
            "not now",
            "later",

            # Malayalam
            "വേണ്ട",
            "ഇല്ല",
            "പിന്നെ",
            "ഇപ്പോൾ വേണ്ട",

            # Hindi
            "नहीं",
            "छोड़ें",
            "बाद में",
            "अभी नहीं",

            # Tamil
            "வேண்டாம்",
            "இல்லை",
            "பிறகு",
            "இப்போது வேண்டாம்",
        }


        if normalized_value in skip_values:

            chat_session.customer_email = ""

        else:

            try:
                validate_email(
                    submitted_email
                )

            except ValidationError:

                bot_response = get_response(
                    "invalid_email",
                    chat_session.language,
                )


                ChatMessage.objects.create(
                    session=chat_session,
                    sender="bot",
                    message=bot_response,
                    translated_message="",
                    language=chat_session.language,
                    intent="collect_email",
                )


                return JsonResponse(
                    {
                        "success": True,
                        "response": bot_response,
                        "response_type": "text",
                        "onboarding_step": "email",
                        "language": chat_session.language,
                        "show_quick_replies": False,
                    }
                )


            chat_session.customer_email = (
                submitted_email
            )


        # Complete onboarding
        chat_session.onboarding_step = "completed"

        chat_session.save(
            update_fields=[
                "customer_email",
                "onboarding_step",
                "updated_at",
            ]
        )


        bot_response = get_response(
    "onboarding_complete",
    chat_session.language,
    name=chat_session.customer_name or "",
)


        ChatMessage.objects.create(
            session=chat_session,
            sender="bot",
            message=bot_response,
            translated_message="",
            language=chat_session.language,
            intent="onboarding_completed",
        )


        return JsonResponse(
            {
                "success": True,
                "response": bot_response,
                "response_type": "menu",
                "onboarding_step": "completed",
                "language": chat_session.language,
                "show_quick_replies": True,
                "session_id": str(
                    chat_session.session_id
                ),
            }
        )


    # =====================================================
    # 8. NORMAL CHATBOT CONVERSATION
    # =====================================================
    #
    # NO GoogleTranslator
    # NO translation API
    #
    # process_message() understands the selected
    # language directly.
    # =====================================================

    result = process_message(
        chat_session=chat_session,
        user_message=user_message,
    )


    # =====================================================
    # 9. GET ENGINE RESULT
    # =====================================================

    bot_response = result.get(
        "response",
        ""
    )

    intent = result.get(
        "intent",
        "fallback"
    )

    response_type = result.get(
        "response_type",
        "text"
    )

    show_quick_replies = result.get(
        "show_quick_replies",
        True
    )


    # =====================================================
    # 10. UPDATE USER MESSAGE
    # =====================================================

    user_chat_message.intent = intent
    user_chat_message.translated_message = ""

    user_chat_message.save(
        update_fields=[
            "intent",
            "translated_message",
        ]
    )


    # =====================================================
    # 11. SAVE BOT MESSAGE
    # =====================================================

    ChatMessage.objects.create(
        session=chat_session,
        sender="bot",
        message=bot_response,
        translated_message="",
        language=chat_session.language,
        intent=intent,
    )


    # =====================================================
    # 12. OPTIONAL ACTION BUTTON
    # =====================================================

    action = None

    action_text = result.get(
        "action_text",
        ""
    )

    action_url = result.get(
        "action_url",
        ""
    )


    if action_text and action_url:

        action = {
            "text": action_text,
            "url": action_url,
        }


    # =====================================================
    # 13. RETURN RESPONSE
    # =====================================================

    return JsonResponse(
        {
            "success": True,

            "response": bot_response,

            "response_type": response_type,

            "session_id": str(
                chat_session.session_id
            ),

            "language": chat_session.language,

            "onboarding_step": (
                chat_session.onboarding_step
            ),

            "action": action,

            "show_language_options": False,

            "show_quick_replies": (
                show_quick_replies
            ),

            "customer_name": (
                chat_session.customer_name
            ),
        }
    )



def chatbot_initialize(request):

    chat_session = (
        get_or_create_chat_session(
            request
        )
    )


    # =====================================================
    # LANGUAGE SELECTION
    # =====================================================

    if (
        chat_session.onboarding_step
        ==
        "language"
    ):

        return JsonResponse(
            {
                "success": True,

                "response": (
                    "Welcome to Flying Fox Adventure! "
                    "Please choose your preferred language."
                ),

                "response_type":
                    "language",

                "onboarding_step":
                    "language",

                "show_language_options":
                    True,

                "languages": [

                    {
                        "code": "en",
                        "name": "English",
                    },

                    {
                        "code": "ml",
                        "name": "മലയാളം",
                    },

                    {
                        "code": "hi",
                        "name": "हिंदी",
                    },

                    {
                        "code": "ta",
                        "name": "தமிழ்",
                    },

                ],

                "show_quick_replies":
                    False,

                "customer_name":
                    chat_session.customer_name,
            }
        )


    # =====================================================
    # NAME
    # =====================================================

    if (
        chat_session.onboarding_step
        ==
        "name"
    ):

        response = get_response(
            "ask_name",
            chat_session.language,
        )


    # =====================================================
    # PHONE
    # =====================================================

    elif (
        chat_session.onboarding_step
        ==
        "phone"
    ):

        response = get_response(

            "ask_phone",

            chat_session.language,

            name=(
                chat_session.customer_name
                or ""
            ),
        )


    # =====================================================
    # EMAIL
    # =====================================================

    elif (
        chat_session.onboarding_step
        ==
        "email"
    ):

        response = get_response(
            "ask_email",
            chat_session.language,
        )


    # =====================================================
    # COMPLETED
    # =====================================================

    else:

        response = get_response(

            "welcome_back",

            chat_session.language,

            name=(
                chat_session.customer_name
                or ""
            ),
        )


    # =====================================================
    # RESPONSE
    # =====================================================

    return JsonResponse(
        {
            "success": True,

            "response":
                response,

            "response_type":
                "text",

            "onboarding_step":
                chat_session.onboarding_step,

            "language":
                chat_session.language,

            "show_language_options":
                False,

            "show_quick_replies":
                (
                    chat_session.onboarding_step
                    ==
                    "completed"
                ),

            "customer_name":
                chat_session.customer_name,
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

    # -----------------------------------------
    # CURRENT BLOG
    # -----------------------------------------

    blog = get_object_or_404(
        Blog,
        slug=slug,
    )


    # -----------------------------------------
    # RECENT BLOGS
    # Exclude the article currently being read
    # -----------------------------------------

    recent_blogs = (
        Blog.objects
        .exclude(
            pk=blog.pk
        )
        .order_by(
            "-created_at"
        )[:4]
    )


    return render(
        request,
        "frontend/blog_detail.html",
        {
            "blog": blog,
            "recent_blogs": recent_blogs,
        },
    )


from .forms import OfferForm


# ==========================================
# OFFER CRUD
# ==========================================

# ==========================================
# OFFER CRUD
# ==========================================

@_admin_required
def offer_list(request):

    today = timezone.localdate()

    offers_qs = (
    Offer.objects
    .prefetch_related("rides")
    .all()
    .order_by("-created_at")
     )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    status = request.GET.get(
        "status",
        ""
    ).strip()


    # =====================================================
    # SEARCH
    # =====================================================

    if search:

        offers_qs = offers_qs.filter(
            Q(title__icontains=search)
            |
            Q(coupon_code__icontains=search)
            |
            Q(rides__name__icontains=search)
        )


    # =====================================================
    # STATUS FILTER
    # =====================================================

    if status == "active":

        offers_qs = offers_qs.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        )

    elif status == "inactive":

        offers_qs = offers_qs.filter(
            is_active=False
        )

    elif status == "upcoming":

        offers_qs = offers_qs.filter(
            is_active=True,
            start_date__gt=today,
        )

    elif status == "expired":

        offers_qs = offers_qs.filter(
            end_date__lt=today
        )


    # =====================================================
    # PAGINATION
    # =====================================================

    paginator = Paginator(
        offers_qs,
        10
    )

    offers = paginator.get_page(
        request.GET.get("page")
    )


    status_choices = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("upcoming", "Upcoming"),
        ("expired", "Expired"),
    ]


    return render(
        request,
        "admin_pages/offer_list.html",
        {
            "offers": offers,
            "search": search,
            "selected_status": status,
            "status_choices": status_choices,
        }
    )



@_admin_required
def offer_create(request):

    if request.method == "POST":

        form = OfferForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            offer = form.save()

            messages.success(
                request,
                f'Offer "{offer.title}" created successfully.'
            )

            return redirect(
                "offer_list"
            )

        messages.error(
            request,
            "Please correct the errors below."
        )

    else:

        form = OfferForm()


    return render(
        request,
        "admin_pages/offer_form.html",
        {
            "form": form,
            "page_title": "Create Offer",
            "button_text": "Create Offer",
            "all_rides": Ride.objects.filter(
                is_active=True
            ).order_by("name"),
        }
    )





@_admin_required
def offer_update(request, slug):

    offer = get_object_or_404(
        Offer,
        slug=slug
    )

    if request.method == "POST":

        form = OfferForm(
            request.POST,
            request.FILES,
            instance=offer
        )

        if form.is_valid():

            offer = form.save()

            messages.success(
                request,
                f'Offer "{offer.title}" updated successfully.'
            )

            return redirect(
                "offer_list"
            )

        messages.error(
            request,
            "Please correct the errors below."
        )

    else:

        form = OfferForm(
            instance=offer
        )


    return render(
        request,
        "admin_pages/offer_form.html",
        {
        "form": form,
        "offer": offer,
        "page_title": "Edit Offer",
        "button_text": "Update Offer",
         "all_rides": Ride.objects.filter(
            is_active=True
        ).order_by("name"),
        }
    )


@_admin_required
def offer_detail(request, slug):

    offer = get_object_or_404(
        Offer.objects.prefetch_related("rides"),
        slug=slug
    )

    return render(
        request,
        "admin_pages/offer_detail.html",
        {
            "offer": offer,
        }
    )



@_admin_required
def offer_delete(request, slug):

    offer = get_object_or_404(
        Offer,
        slug=slug
    )

    if request.method == "POST":

        title = offer.title

        offer.delete()

        messages.success(
            request,
            f'Offer "{title}" deleted successfully.'
        )

    return redirect(
        "offer_list"
    )







    # offers management
from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone

from .models import Offer


def offers(request):

    today = timezone.localdate()

    # =========================================================
    # GET ALL OFFERS
    # =========================================================

    offers_qs = (
        Offer.objects
        .prefetch_related("rides")
        .all()
        .order_by("-created_at")
    )


    # =========================================================
    # SEARCH
    # =========================================================

    search = request.GET.get(
        "search",
        ""
    ).strip()


    if search:

        offers_qs = offers_qs.filter(

            Q(
                title__icontains=search
            )

            |

            Q(
                description__icontains=search
            )

            |

            Q(
                coupon_code__icontains=search
            )

            |

            Q(
                rides__name__icontains=search
            )

            |

            Q(
                offer_type__icontains=search
            )

        ).distinct()


    # =========================================================
    # PREPARE DISPLAY STATUS
    # =========================================================

    active_count = 0
    upcoming_count = 0
    expired_count = 0
    inactive_count = 0


    for offer in offers_qs:

        # Your model already calculates the status
        status = offer.computed_status

        offer.display_status = status


        if status == "active":

            offer.display_status_label = "Active"

            active_count += 1


        elif status == "upcoming":

            offer.display_status_label = "Upcoming"

            upcoming_count += 1


        elif status == "expired":

            offer.display_status_label = "Expired"

            expired_count += 1


        else:

            offer.display_status_label = "Inactive"

            inactive_count += 1


    # =========================================================
    # PAGE STATISTICS
    # =========================================================

    total_count = offers_qs.count()


    # =========================================================
    # CONTEXT
    # =========================================================

    context = {

        "offers": offers_qs,

        "today": today,

        "search": search,

        "total_count": total_count,

        "active_count": active_count,

        "upcoming_count": upcoming_count,

        "expired_count": expired_count,

        "inactive_count": inactive_count,
    }


    return render(
        request,
        "frontend/offers.html",
        context
    )



from .models import Offer
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .models import Offer


def frontend_offer_detail(request, slug):

    today = timezone.localdate()

    # =====================================================
    # CURRENT OFFER
    # =====================================================

    offer = get_object_or_404(
    Offer.objects.prefetch_related("rides"),
    slug=slug,
    )

    # No refresh_status() needed.
    # Your model's computed_status property automatically
    # calculates:
    #
    # inactive
    # upcoming
    # expired
    # active


    # =====================================================
    # RELATED ACTIVE OFFERS
    # =====================================================

    related_offers = (
        Offer.objects
        .prefetch_related("rides")
        .filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
        )
        .exclude(pk=offer.pk)
        .exclude(banner_image="")
        .filter(banner_image__isnull=False)
    )

    # -----------------------------------------------------
    # Prefer offers for the same ride
    # -----------------------------------------------------

    if offer.rides.exists():
        same_ride_offers = related_offers.filter( rides__in=offer.rides.all()).distinct()[:3]

        # Convert to list because we'll possibly add
        # other offers below.
        related_offers = list(same_ride_offers)

        # If fewer than 3 offers exist for this ride,
        # fill the remaining positions with other offers.
        if len(related_offers) < 3:

            existing_ids = [item.pk for item in related_offers]

            extra_offers = (
    Offer.objects
    .prefetch_related("rides")
    .filter(
        is_active=True,
        start_date__lte=today,
        end_date__gte=today,
    )
    .exclude(pk=offer.pk)
    .exclude(pk__in=existing_ids)
    .exclude(banner_image="")
    .filter(banner_image__isnull=False)
    .order_by("-created_at")[
        :3 - len(related_offers)
    ]
)

            related_offers.extend(extra_offers)

    else:
        related_offers = list(
            related_offers.order_by("-created_at")[:3]
        )


    # =====================================================
    # TEMPLATE
    # =====================================================

    context = {
        "offer": offer,
        "related_offers": related_offers,
        "today": today,
    }

    return render(
        request,
        "frontend/offer_detail.html",
        context,
    )




# staff view ticket 

# =========================================================
# TICKET VERIFIER STAFF LOGIN
# =========================================================

def ticket_staff_login(request):

    # Already logged in and has permission
    if request.user.is_authenticated:

        if request.user.has_perm(
            "flyingfox_app.verify_ticket"
        ):

            return redirect(
         "ticket_staff_dashboard"
        )


    if request.method == "POST":

        username = (
            request.POST.get(
                "username",
                ""
            )
            .strip()
        )

        password = (
            request.POST.get(
                "password",
                ""
            )
        )


        if not username or not password:

            messages.error(
                request,
                "Please enter username and password."
            )

            return render(
                request,
                "staff/ticket_login.html",
            )


        user = authenticate(
            request,
            username=username,
            password=password,
        )


        if user is None:

            messages.error(
                request,
                "Invalid username or password."
            )

            return render(
                request,
                "staff/ticket_login.html",
            )


        # -------------------------------------------------
        # USER MUST BE ACTIVE
        # -------------------------------------------------

        if not user.is_active:

            messages.error(
                request,
                "This staff account is inactive."
            )

            return render(
                request,
                "staff/ticket_login.html",
            )


        # -------------------------------------------------
        # USER MUST HAVE VERIFY PERMISSION
        # -------------------------------------------------

        if not user.has_perm(
            "flyingfox_app.verify_ticket"
        ):

            messages.error(
                request,
                (
                    "You do not have permission "
                    "to verify tickets."
                )
            )

            return render(
                request,
                "staff/ticket_login.html",
            )


        # -------------------------------------------------
        # LOGIN
        # -------------------------------------------------

        login(
            request,
            user
        )


        return redirect(
            "ticket_staff_dashboard"
        )


    return render(
        request,
        "staff/ticket_login.html",
    )



# =========================================================
# TICKET VERIFIER LOGOUT
# =========================================================

def ticket_staff_logout(request):

    logout(
        request
    )

    messages.success(
        request,
        "You have been logged out."
    )

    return redirect(
        "ticket_staff_login"
    )





# =========================================================
# VERIFY QR TICKET
# =========================================================
@permission_required(
    "flyingfox_app.verify_ticket",
    login_url="ticket_staff_login",
)
def verify_ticket(
    request,
    qr_token,
):

    # =====================================================
    # CONFIRMED SLOT PREFETCH
    # =====================================================

    confirmed_slot_prefetch = Prefetch(

        "booking__ride_items__allocated_slots",

        queryset=(
            BookingRideSlot.objects
            .filter(
                status="confirmed"
            )
            .order_by(
                "slot_start_time"
            )
        ),

        to_attr="confirmed_slots",
    )

    # =====================================================
    # LOAD TICKET + FULL MULTI-RIDE BOOKING
    # =====================================================

    ticket = get_object_or_404(

        Ticket.objects
        .select_related(
            "booking",
            "booking__payment",
        )
        .prefetch_related(
            "booking__ride_items__ride",
            "booking__ride_items__ride_price",
            "booking__ride_items__offer",
            "booking__ride_items__weight_groups",

            confirmed_slot_prefetch,
        ),

        qr_token=qr_token,
    )

    booking = (
        ticket.booking
    )

    # =====================================================
    # RIDE ITEMS
    # =====================================================

    ride_items = list(
        booking.ride_items.all()
    )

    # =====================================================
    # PAYMENT VALIDITY
    # =====================================================

    is_payment_valid = (
        hasattr(
            booking,
            "payment"
        )
        and
        booking.payment.status
        ==
        "paid"
    )

    # =====================================================
    # BOOKING VALIDITY
    # =====================================================

    is_booking_valid = (
        booking.status
        in [
            "confirmed",
            "checked_in",
        ]
    )

    # =====================================================
    # RIDE ITEM VALIDITY
    # =====================================================

    has_rides = bool(
        ride_items
    )

    # =====================================================
    # OVERALL VALIDITY
    # =====================================================

    is_valid = (
        is_payment_valid
        and
        is_booking_valid
        and
        has_rides
    )

    # =====================================================
    # CHECK-IN COUNTS
    # =====================================================

    total_ride_count = len(
        ride_items
    )

    checked_in_ride_count = sum(

        1

        for item
        in ride_items

        if item.status
        ==
        "checked_in"
    )

    pending_ride_count = (
        total_ride_count
        -
        checked_in_ride_count
    )

    all_rides_checked_in = (
        total_ride_count > 0
        and
        checked_in_ride_count
        ==
        total_ride_count
    )

    some_rides_checked_in = (
        checked_in_ride_count > 0
        and
        not all_rides_checked_in
    )

    # =====================================================
    # SYNC LEGACY TICKET USED STATE
    #
    # Ticket becomes fully used only when every ride
    # in this booking has been checked in.
    # =====================================================

    if (
        all_rides_checked_in
        and
        not ticket.is_used
    ):

        ticket.is_used = True

        if not ticket.checked_in_at:

            ticket.checked_in_at = (
                timezone.now()
            )

        ticket.save(
            update_fields=[
                "is_used",
                "checked_in_at",
            ]
        )

    # =====================================================
    # CONTEXT
    # =====================================================

    return render(
        request,
        "staff/ticket_verify.html",
        {
            "ticket":
                ticket,

            "booking":
                booking,

            "ride_items":
                ride_items,

            "is_valid":
                is_valid,

            "total_ride_count":
                total_ride_count,

            "checked_in_ride_count":
                checked_in_ride_count,

            "pending_ride_count":
                pending_ride_count,

            "all_rides_checked_in":
                all_rides_checked_in,

            "some_rides_checked_in":
                some_rides_checked_in,
        },
    )







# =========================================================
# CHECK IN ONE BOOKING RIDE ITEM
# =========================================================

@permission_required(
    "flyingfox_app.verify_ticket",
    login_url="ticket_staff_login",
)
@transaction.atomic
def ticket_check_in(
    request,
    booking_item_id,
):

    # =====================================================
    # POST ONLY
    # =====================================================

    if request.method != "POST":

        return redirect(
            "ticket_scanner"
        )


    # =====================================================
    # LOCK RIDE ITEM
    # =====================================================

    booking_item = get_object_or_404(

        BookingRideItem.objects
        .select_for_update()
        .select_related(
            "booking",
            "ride",
        ),

        pk=booking_item_id,
    )


    booking = (
        booking_item.booking
    )


    # =====================================================
    # LOCK TICKET
    # =====================================================

    ticket = get_object_or_404(

        Ticket.objects
        .select_for_update(),

        booking=booking,
    )


    # =====================================================
    # PAYMENT
    # =====================================================

    payment = (
        Payment.objects
        .filter(
            booking=booking
        )
        .first()
    )


    if (
        payment is None
        or
        payment.status
        !=
        "paid"
    ):

        messages.error(
            request,
            (
                "This adventure cannot be checked in "
                "because payment is not confirmed."
            )
        )

        return redirect(
            "verify_ticket",
            qr_token=
                ticket.qr_token,
        )


    # =====================================================
    # BOOKING STATUS
    # =====================================================

    if booking.status not in [
        "confirmed",
        "checked_in",
    ]:

        messages.error(
            request,
            (
                "This booking is not valid "
                "for check-in."
            )
        )

        return redirect(
            "verify_ticket",
            qr_token=
                ticket.qr_token,
        )


    # =====================================================
    # ALREADY CHECKED IN
    # =====================================================

    if (
        booking_item.status
        ==
        "checked_in"
    ):

        messages.warning(
            request,
            (
                f"{booking_item.ride.name} "
                "has already been checked in."
            )
        )

        return redirect(
            "verify_ticket",
            qr_token=
                ticket.qr_token,
        )


    # =====================================================
    # CHECK IN THIS RIDE
    # =====================================================

    booking_item.status = (
        "checked_in"
    )


    booking_item.save(
        update_fields=[
            "status",
        ]
    )


    # =====================================================
    # CHECK ALL RIDE ITEMS
    # =====================================================

    all_booking_items = list(

        BookingRideItem.objects
        .select_for_update()
        .filter(
            booking=booking
        )
    )


    all_checked_in = (
        bool(
            all_booking_items
        )
        and
        all(
            item.status
            ==
            "checked_in"

            for item
            in all_booking_items
        )
    )


    # =====================================================
    # ALL RIDES CHECKED IN
    # =====================================================

    if all_checked_in:

        # Parent booking
        booking.status = (
            "checked_in"
        )

        booking.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )


        # Parent ticket
        ticket.is_used = True

        ticket.checked_in_at = (
            timezone.now()
        )

        ticket.save(
            update_fields=[
                "is_used",
                "checked_in_at",
            ]
        )


        messages.success(
            request,
            (
                f"{booking_item.ride.name} checked in. "
                "All adventures in this ticket "
                "are now checked in."
            )
        )


    # =====================================================
    # SOME RIDES STILL PENDING
    # =====================================================

    else:

        # Keep parent booking confirmed until
        # every ride is checked in.

        if (
            booking.status
            ==
            "checked_in"
        ):

            booking.status = (
                "confirmed"
            )

            booking.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )


        # Ticket must remain usable
        ticket.is_used = False

        ticket.checked_in_at = None

        ticket.save(
            update_fields=[
                "is_used",
                "checked_in_at",
            ]
        )


        messages.success(
            request,
            (
                f"{booking_item.ride.name} "
                "checked in successfully."
            )
        )


    # =====================================================
    # RETURN TO SAME TICKET
    # =====================================================

    return redirect(
        "verify_ticket",
        qr_token=
            ticket.qr_token,
    )






# =========================================================
# STAFF TICKET DASHBOARD
# =========================================================


@permission_required(
    "flyingfox_app.verify_ticket",
    login_url="ticket_staff_login",
)
def ticket_staff_dashboard(request):

    # =====================================================
    # TODAY
    # =====================================================

    today = timezone.localdate()

    # =====================================================
    # SELECTED DATE
    # =====================================================

    selected_date_raw = (
        request.GET.get(
            "date",
            ""
        )
        .strip()
    )

    selected_date = (
        parse_date(
            selected_date_raw
        )
        if selected_date_raw
        else None
    )

    # Default selected date = tomorrow
    if selected_date is None:

        selected_date = (
            today
            +
            timedelta(
                days=1
            )
        )

    # =====================================================
    # CONFIRMED SLOT PREFETCH
    #
    # Only confirmed ride slots are shown to staff.
    #
    # Example:
    #
    # Superman Zipline
    # 10:30 AM - 11:30 AM -> 1 rider
    # 11:30 AM - 12:30 PM -> 5 riders
    # 12:30 PM - 01:30 PM -> 1 rider
    # =====================================================

    confirmed_slot_prefetch = Prefetch(
        "ride_items__allocated_slots",

        queryset=(
            BookingRideSlot.objects
            .filter(
                status="confirmed"
            )
            .order_by(
                "slot_start_time"
            )
        ),

        to_attr="confirmed_slots",
    )

    # =====================================================
    # COMMON BOOKING QUERY
    # =====================================================

    base_bookings = (
        Booking.objects

        .filter(
            status__in=[
                "confirmed",
                "checked_in",
            ],
        )

        .select_related(
            "payment",
            "ticket",
        )

        .prefetch_related(
            "ride_items__ride",
            "ride_items__ride_price",
            "ride_items__offer",
            "ride_items__weight_groups",

            confirmed_slot_prefetch,
        )
    )

    # =====================================================
    # TODAY BOOKINGS
    # =====================================================

    today_bookings = (
        base_bookings

        .filter(
            booking_date=today
        )

        .order_by(
            "created_at"
        )
    )

    # =====================================================
    # SELECTED DATE BOOKINGS
    # =====================================================

    selected_date_bookings = (
        base_bookings

        .filter(
            booking_date=
                selected_date
        )

        .order_by(
            "created_at"
        )
    )

    # =====================================================
    # TODAY BOOKING COUNT
    # =====================================================

    today_booking_count = (
        today_bookings.count()
    )

    # =====================================================
    # FULLY VERIFIED TICKETS TODAY
    # =====================================================

    verified_today_count = (
        Ticket.objects
        .filter(
            is_used=True,
            booking__booking_date=today,
        )
        .count()
    )

    # =====================================================
    # BOOKINGS WITH AT LEAST ONE PENDING RIDE
    # =====================================================

    pending_today_count = sum(

        1

        for booking
        in today_bookings

        if any(

            item.status
            !=
            "checked_in"

            for item
            in booking.ride_items.all()
        )
    )

    # =====================================================
    # TOTAL PARTICIPANTS TODAY
    # =====================================================

    total_participants = (
        today_bookings

        .aggregate(
            total=Sum(
                "quantity"
            )
        )

        .get(
            "total"
        )

        or
        0
    )

    # =====================================================
    # TOTAL ADVENTURES TODAY
    # =====================================================

    today_adventure_count = (
        BookingRideItem.objects

        .filter(
            booking__booking_date=today,

            booking__status__in=[
                "confirmed",
                "checked_in",
            ],
        )

        .count()
    )

    # =====================================================
    # CHECKED-IN ADVENTURES TODAY
    # =====================================================

    checked_in_adventure_count = (
        BookingRideItem.objects

        .filter(
            booking__booking_date=today,

            booking__status__in=[
                "confirmed",
                "checked_in",
            ],

            status="checked_in",
        )

        .count()
    )

    # =====================================================
    # PENDING ADVENTURES TODAY
    # =====================================================

    pending_adventure_count = (
        BookingRideItem.objects

        .filter(
            booking__booking_date=today,

            booking__status__in=[
                "confirmed",
                "checked_in",
            ],
        )

        .exclude(
            status="checked_in"
        )

        .count()
    )

    # =====================================================
    # RECENT FULLY VERIFIED TICKETS
    # =====================================================

    recent_verified = (
        Ticket.objects

        .filter(
            is_used=True,
            checked_in_at__date=today,
        )

        .select_related(
            "booking",
        )

        .prefetch_related(
            "booking__ride_items__ride",
        )

        .order_by(
            "-checked_in_at"
        )[:5]
    )

    # =====================================================
    # CONTEXT
    # =====================================================

    return render(
        request,
        "staff/dashboard.html",
        {
            "today":
                today,

            "selected_date":
                selected_date,

            "today_bookings":
                today_bookings,

            "selected_date_bookings":
                selected_date_bookings,

            "today_booking_count":
                today_booking_count,

            "verified_today_count":
                verified_today_count,

            "pending_today_count":
                pending_today_count,

            "total_participants":
                total_participants,

            "today_adventure_count":
                today_adventure_count,

            "checked_in_adventure_count":
                checked_in_adventure_count,

            "pending_adventure_count":
                pending_adventure_count,

            "recent_verified":
                recent_verified,
        },
    )




# =========================================================
# STAFF RIDE SCHEDULE / CAPACITY BOARD
# =========================================================

@permission_required(
    "flyingfox_app.verify_ticket",
    login_url="ticket_staff_login",
)
def staff_ride_schedule(request):

    # =====================================================
    # TODAY
    # =====================================================

    today = timezone.localdate()

    # =====================================================
    # SELECTED DATE
    # =====================================================

    selected_date_raw = (
        request.GET.get(
            "date",
            ""
        )
        .strip()
    )

    selected_date = (
        parse_date(
            selected_date_raw
        )
        if selected_date_raw
        else None
    )

    # Invalid / empty date -> today
    if selected_date is None:

        selected_date = today

    # =====================================================
    # CURRENT TIME
    #
    # Used only for highlighting today's current slot.
    # =====================================================

    now = timezone.localtime()

    current_time = (
        now.time()
        if selected_date == today
        else None
    )

    # =====================================================
    # ACTIVE RIDES
    # =====================================================

    rides = (
        Ride.objects
        .filter(
            is_active=True
        )
        .order_by(
            "name"
        )
    )

    # =====================================================
    # PAGE DATA
    # =====================================================

    ride_schedule = []

    # Page totals
    total_capacity = 0
    total_occupied = 0
    total_confirmed = 0
    total_held = 0
    total_remaining = 0

    # =====================================================
    # BUILD SCHEDULE FOR EACH RIDE
    # =====================================================

    for ride in rides:

        # =================================================
        # USE EXISTING BOOKING SLOT SERVICE
        #
        # This keeps staff capacity calculations consistent
        # with customer booking availability.
        # =================================================

        available_slots = get_available_slots(
            ride=ride,
            booking_date=selected_date,
        )

        # =================================================
        # CONFIRMED RIDERS BY SLOT
        # =================================================

        confirmed_rows = (
            BookingRideSlot.objects

            .filter(
                booking_item__ride=ride,

                booking_item__booking__booking_date=
                    selected_date,

                status="confirmed",
            )

            .values(
                "slot_start_time"
            )

            .annotate(
                total=Sum(
                    "participant_count"
                )
            )
        )

        confirmed_by_start = {

            row["slot_start_time"]:
                row["total"] or 0

            for row
            in confirmed_rows
        }

        # =================================================
        # ACTIVE HELD RIDERS BY SLOT
        #
        # Only holds that have NOT expired reduce capacity.
        # =================================================

        held_rows = (
            BookingRideSlot.objects

            .filter(
                booking_item__ride=ride,

                booking_item__booking__booking_date=
                    selected_date,

                status="held",

                hold_expires_at__gt=
                    timezone.now(),
            )

            .values(
                "slot_start_time"
            )

            .annotate(
                total=Sum(
                    "participant_count"
                )
            )
        )

        held_by_start = {

            row["slot_start_time"]:
                row["total"] or 0

            for row
            in held_rows
        }

        # =================================================
        # PREPARE DISPLAY SLOT ROWS
        # =================================================

        display_slots = []

        ride_total_confirmed = 0
        ride_total_held = 0
        ride_total_occupied = 0
        ride_total_remaining = 0
        ride_total_capacity = 0

        for slot in available_slots:

            start_time = (
                slot["start_time"]
            )

            end_time = (
                slot["end_time"]
            )

            capacity = int(
                slot["capacity"]
            )

            occupied = int(
                slot["booked"]
            )

            remaining = int(
                slot["remaining"]
            )

            confirmed = int(
                confirmed_by_start.get(
                    start_time,
                    0
                )
            )

            held = int(
                held_by_start.get(
                    start_time,
                    0
                )
            )

            # =================================================
            # SAFETY
            #
            # Service "booked" is the source of truth for
            # occupied capacity. Confirmed/held are only the
            # breakdown shown to staff.
            # =================================================

            if capacity > 0:

                usage_percent = round(
                    (
                        occupied
                        /
                        capacity
                    )
                    *
                    100
                )

            else:

                usage_percent = 0

            usage_percent = max(
                0,
                min(
                    usage_percent,
                    100
                )
            )

            # =================================================
            # SLOT STATUS
            # =================================================

            if remaining <= 0:

                status_key = "full"
                status_label = "FULL"

            elif occupied <= 0:

                status_key = "available"
                status_label = "AVAILABLE"

            elif remaining <= max(
                1,
                capacity // 4
            ):

                status_key = "low"
                status_label = "ALMOST FULL"

            else:

                status_key = "partial"
                status_label = "AVAILABLE"

            # =================================================
            # CURRENT SLOT
            # =================================================

            is_current = False

            if current_time is not None:

                is_current = (
                    start_time
                    <=
                    current_time
                    <
                    end_time
                )

            display_slots.append(
                {
                    "start_time":
                        start_time,

                    "end_time":
                        end_time,

                    "start_label":
                        start_time.strftime(
                            "%I:%M %p"
                        ),

                    "end_label":
                        end_time.strftime(
                            "%I:%M %p"
                        ),

                    "capacity":
                        capacity,

                    "confirmed":
                        confirmed,

                    "held":
                        held,

                    "occupied":
                        occupied,

                    "remaining":
                        remaining,

                    "usage_percent":
                        usage_percent,

                    "status_key":
                        status_key,

                    "status_label":
                        status_label,

                    "is_current":
                        is_current,
                }
            )

            # =================================================
            # RIDE TOTALS
            # =================================================

            ride_total_capacity += (
                capacity
            )

            ride_total_confirmed += (
                confirmed
            )

            ride_total_held += (
                held
            )

            ride_total_occupied += (
                occupied
            )

            ride_total_remaining += (
                remaining
            )

        # =====================================================
        # RIDE SUMMARY
        # =====================================================

        ride_schedule.append(
            {
                "ride":
                    ride,

                "slots":
                    display_slots,

                "slot_count":
                    len(
                        display_slots
                    ),

                "total_capacity":
                    ride_total_capacity,

                "total_confirmed":
                    ride_total_confirmed,

                "total_held":
                    ride_total_held,

                "total_occupied":
                    ride_total_occupied,

                "total_remaining":
                    ride_total_remaining,
            }
        )

        # =====================================================
        # PAGE TOTALS
        # =====================================================

        total_capacity += (
            ride_total_capacity
        )

        total_confirmed += (
            ride_total_confirmed
        )

        total_held += (
            ride_total_held
        )

        total_occupied += (
            ride_total_occupied
        )

        total_remaining += (
            ride_total_remaining
        )

    # =====================================================
    # CONTEXT
    # =====================================================

    return render(
        request,
        "staff/ride_schedule.html",
        {
            "today":
                today,

            "selected_date":
                selected_date,

            "ride_schedule":
                ride_schedule,

            "total_rides":
                len(
                    ride_schedule
                ),

            "total_capacity":
                total_capacity,

            "total_confirmed":
                total_confirmed,

            "total_held":
                total_held,

            "total_occupied":
                total_occupied,

            "total_remaining":
                total_remaining,
        },
    )

# =========================================================
# VERIFIED TICKET HISTORY
# =========================================================

@permission_required(
    "flyingfox_app.verify_ticket",
    login_url="ticket_staff_login",
)
def verified_ticket_list(request):


    # =====================================================
    # BASE QUERY
    # =====================================================

    tickets_qs = (
        Ticket.objects

        .filter(
            is_used=True
        )

        .select_related(
            "booking",
            "booking__payment",
        )

        .prefetch_related(
            "booking__ride_items__ride",
            "booking__ride_items__ride_price",
            "booking__ride_items__offer",
            "booking__ride_items__weight_groups",
        )

        .order_by(
            "-checked_in_at"
        )
    )


    # =====================================================
    # SEARCH
    # =====================================================

    search = (
        request.GET.get(
            "search",
            ""
        )
        .strip()
    )


    if search:

        tickets_qs = (
            tickets_qs.filter(

                # -----------------------------------------
                # TICKET NUMBER
                # -----------------------------------------

                Q(
                    ticket_number__icontains=
                        search
                )

                |

                # -----------------------------------------
                # CUSTOMER NAME
                # -----------------------------------------

                Q(
                    booking__customer_name__icontains=
                        search
                )

                |

                # -----------------------------------------
                # CUSTOMER PHONE
                # -----------------------------------------

                Q(
                    booking__customer_phone__icontains=
                        search
                )

                |

                # -----------------------------------------
                # BOOKING ID
                # -----------------------------------------

                Q(
                    booking__booking_id__icontains=
                        search
                )

                |

                # -----------------------------------------
                # ANY RIDE IN THE BOOKING
                # -----------------------------------------

                Q(
                    booking__ride_items__ride__name__icontains=
                        search
                )

            )

            .distinct()
        )


    # =====================================================
    # DATE FILTER
    # =====================================================

    date_raw = (
        request.GET.get(
            "date",
            ""
        )
        .strip()
    )


    selected_date = (
        parse_date(
            date_raw
        )
        if date_raw
        else None
    )


    if selected_date:

        tickets_qs = (
            tickets_qs.filter(
                checked_in_at__date=
                    selected_date
            )
        )


    # =====================================================
    # PAGINATION
    # =====================================================

    paginator = Paginator(
        tickets_qs,
        15,
    )


    tickets = (
        paginator.get_page(
            request.GET.get(
                "page"
            )
        )
    )


    # =====================================================
    # CONTEXT
    # =====================================================

    return render(
        request,
        "staff/verified_tickets.html",
        {
            "tickets":
                tickets,

            "search":
                search,

            "selected_date":
                selected_date,
        },
    )

    
# =========================================================
# QR SCANNER PAGE
# =========================================================

@permission_required(
    "flyingfox_app.verify_ticket",
    login_url="ticket_staff_login",
)
def ticket_scanner(request):

    return render(
        request,
        "staff/ticket_scanner.html",
    )



# =========================================================
# VERIFY TICKET USING 6-DIGIT TICKET NUMBER
# =========================================================

@permission_required(
    "flyingfox_app.verify_ticket",
    login_url="ticket_staff_login",
)
def verify_ticket_number(
    request,
):

    # =====================================================
    # POST ONLY
    # =====================================================

    if request.method != "POST":

        return redirect(
            "ticket_scanner"
        )


    # =====================================================
    # GET TICKET NUMBER
    # =====================================================

    ticket_number = (
        request.POST.get(
            "ticket_number",
            ""
        )
        .strip()
    )


    # =====================================================
    # VALIDATION
    # =====================================================

    if (
        not ticket_number.isdigit()
        or
        len(ticket_number) != 6
    ):

        messages.error(
            request,
            "Please enter a valid 6-digit Ticket ID."
        )

        return redirect(
            "ticket_scanner"
        )


    # =====================================================
    # FIND TICKET
    # =====================================================

    ticket = (
        Ticket.objects
        .filter(
            ticket_number=
                ticket_number
        )
        .first()
    )


    if ticket is None:

        messages.error(
            request,
            (
                f"No ticket was found with "
                f"Ticket ID {ticket_number}."
            )
        )

        return redirect(
            "ticket_scanner"
        )


    # =====================================================
    # USE SECURE QR VERIFICATION VIEW
    # =====================================================

    return redirect(
        "verify_ticket",
        qr_token=
            ticket.qr_token,
    )






# =========================================================
# LEGAL PAGES
# =========================================================


def terms_conditions(request):
    return render(
        request,
        "frontend/terms_conditions.html",
    )


def privacy_policy(request):
    return render(
        request,
        "frontend/privacy_policy.html",
    )










# =========================================================
# REFUND SETTINGS
# =========================================================

REFUND_WINDOW_HOURS = 1

REFUND_DEDUCTION_PERCENTAGE = Decimal(
    "10.00"
)


def _calculate_booking_refund(
    booking,
    payment,
):

    # =====================================================
    # PAYMENT MUST EXIST
    # =====================================================

    if not payment:

        return {
            "eligible": False,
            "message": "Payment information was not found.",
        }


    # =====================================================
    # PAYMENT MUST BE SUCCESSFUL
    # =====================================================

    if payment.status != "paid":

        return {
            "eligible": False,
            "message": (
                "Only successfully paid bookings "
                "are eligible for a refund."
            ),
        }


    # =====================================================
    # RAZORPAY PAYMENT ID REQUIRED
    # =====================================================

    if not payment.gateway_payment_id:

        return {
            "eligible": False,
            "message": (
                "Razorpay payment information "
                "is unavailable."
            ),
        }


    # =====================================================
    # PAID TIME REQUIRED
    # =====================================================

    if not payment.paid_at:

        return {
            "eligible": False,
            "message": (
                "Payment confirmation time "
                "is unavailable."
            ),
        }


    # =====================================================
    # DO NOT REFUND USED TICKET
    # =====================================================

    ticket = getattr(
        booking,
        "ticket",
        None,
    )


    if (
        ticket
        and
        ticket.is_used
    ):

        return {
            "eligible": False,
            "message": (
                "This booking has already been "
                "checked in and cannot be refunded."
            ),
        }


    # =====================================================
    # ALREADY CANCELLED
    # =====================================================

    if booking.status == "cancelled":

        return {
            "eligible": False,
            "message": (
                "This booking has already been cancelled."
            ),
        }


    # =====================================================
    # ONE-HOUR WINDOW
    # =====================================================

    refund_deadline = (
        payment.paid_at
        +
        timedelta(
            hours=REFUND_WINDOW_HOURS
        )
    )


    now = timezone.now()


    if now > refund_deadline:

        return {
            "eligible": False,

            "message": (
                "The 1-hour cancellation period "
                "has expired."
            ),

            "deadline":
                refund_deadline,
        }


    # =====================================================
    # CALCULATE 10% DEDUCTION
    # =====================================================

    original_amount = (
        Decimal(
            payment.amount
        )
    )


    deduction_amount = (
        original_amount
        *
        REFUND_DEDUCTION_PERCENTAGE
        /
        Decimal("100")
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


    # =====================================================
    # CUSTOMER RECEIVES 90%
    # =====================================================

    refund_amount = (
        original_amount
        -
        deduction_amount
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


    return {

        "eligible":
            True,

        "original_amount":
            original_amount,

        "deduction_percentage":
            REFUND_DEDUCTION_PERCENTAGE,

        "deduction_amount":
            deduction_amount,

        "refund_amount":
            refund_amount,

        "refund_deadline":
            refund_deadline,

        "remaining_seconds":
            max(
                0,
                int(
                    (
                        refund_deadline
                        -
                        now
                    ).total_seconds()
                ),
            ),
    }




# =========================================================
# CUSTOMER CANCELLATION / REFUND REQUEST
# =========================================================

@require_POST
def booking_refund_request(
    request,
    booking_id,
):

    # =====================================================
    # LOGIN CHECK
    # =====================================================

    user_id = request.session.get(
        "user_id"
    )


    if not user_id:

        messages.error(
            request,
            "Please login to request a cancellation."
        )

        return redirect(
            "user_signin"
        )


    # =====================================================
    # USER
    # =====================================================

    profile = get_object_or_404(
        UserProfile,
        id=user_id,
    )


    # =====================================================
    # BOOKING
    #
    # IMPORTANT:
    # Only this customer's booking can be accessed.
    # =====================================================

    booking = get_object_or_404(

        Booking.objects
        .select_related(
            "payment",
            "ticket",
        ),

        booking_id=
            booking_id,

        user=
            profile,
    )


    # =====================================================
    # PAYMENT
    # =====================================================

    payment = getattr(
        booking,
        "payment",
        None,
    )


    if not payment:

        messages.error(
            request,
            "Payment information could not be found."
        )

        return redirect(
            "user_bookings"
        )


    # =====================================================
    # PREVENT DUPLICATE REFUND REQUEST
    # =====================================================

    existing_refund = (
        Refund.objects
        .filter(
            booking=booking,
            status__in=[
                "requested",
                "approved",
                "processing",
                "processed",
            ],
        )
        .first()
    )


    if existing_refund:

        messages.info(
            request,
            "A refund request already exists for this booking."
        )

        return redirect(
            "user_bookings"
        )


    # =====================================================
    # RECHECK ELIGIBILITY ON SERVER
    #
    # NEVER TRUST THE BUTTON/UI.
    # =====================================================

    refund_info = (
        _calculate_booking_refund(
            booking,
            payment,
        )
    )


    if not refund_info.get(
        "eligible"
    ):

        messages.error(
            request,
            refund_info.get(
                "message",
                (
                    "This booking is no longer "
                    "eligible for cancellation."
                )
            )
        )

        return redirect(
            "user_bookings"
        )


    # =====================================================
    # REASON
    # =====================================================

    reason = (
        request.POST.get(
            "reason",
            ""
        )
        .strip()
    )


    if not reason:

        messages.error(
            request,
            "Please enter a reason for cancellation."
        )

        return redirect(
            "user_bookings"
        )


    # =====================================================
    # CREATE REFUND REQUEST
    #
    # 10% retained
    # 90% refund
    # =====================================================

    Refund.objects.create(

        booking=
            booking,

        payment=
            payment,

        original_amount=
            refund_info[
                "original_amount"
            ],

        deduction_percentage=
            refund_info[
                "deduction_percentage"
            ],

        deduction_amount=
            refund_info[
                "deduction_amount"
            ],

        refund_amount=
            refund_info[
                "refund_amount"
            ],

        razorpay_payment_id=
            payment.gateway_payment_id,

        reason=
            reason,

        status=
            "requested",
    )


    # =====================================================
    # IMPORTANT:
    #
    # DON'T CANCEL BOOKING YET.
    #
    # Admin must approve first.
    # Razorpay refund must then succeed.
    # =====================================================


    messages.success(
        request,
        (
            "Your cancellation request has been submitted. "
            "If approved, 90% of the amount paid will be "
            "refunded to the original payment method."
        )
    )


    return redirect(
        "user_bookings"
    )







# =========================================================
# ADMIN REFUND LIST
# =========================================================

@_admin_required
def refund_list(request):

    refunds_qs = (
        Refund.objects
        .select_related(
            "booking",
            "booking__user",
            "booking__ride",
            "payment",
        )
        .order_by(
            "-requested_at"
        )
    )


    # =====================================================
    # SEARCH
    # =====================================================

    search = (
        request.GET.get(
            "search",
            ""
        )
        .strip()
    )


    if search:

        refunds_qs = (
            refunds_qs.filter(

                Q(
                    booking__customer_name__icontains=
                        search
                )

                |

                Q(
                    booking__customer_email__icontains=
                        search
                )

                |

                Q(
                    booking__customer_phone__icontains=
                        search
                )

                |

                Q(
                    booking__booking_id__icontains=
                        search
                )

                |

                Q(
                    razorpay_payment_id__icontains=
                        search
                )

            )
        )


    # =====================================================
    # STATUS FILTER
    # =====================================================

    selected_status = (
        request.GET.get(
            "status",
            ""
        )
        .strip()
    )


    if selected_status:

        refunds_qs = (
            refunds_qs.filter(
                status=
                    selected_status
            )
        )


    # =====================================================
    # PAGINATION
    # =====================================================

    paginator = Paginator(
        refunds_qs,
        15,
    )


    refunds = (
        paginator.get_page(
            request.GET.get(
                "page"
            )
        )
    )


    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        "admin_pages/refund_list.html",
        {
            "refunds":
                refunds,

            "search":
                search,

            "selected_status":
                selected_status,

            "status_choices":
                Refund.STATUS_CHOICES,
        },
    )





# =========================================================
# ADMIN REFUND DETAIL
# =========================================================

@_admin_required
def refund_detail(
    request,
    refund_id,
):

    refund = get_object_or_404(

        Refund.objects
        .select_related(
            "booking",
            "booking__user",
            "booking__ride",
            "booking__ride_price",
            "payment",
        ),

        refund_id=
            refund_id,
    )


    return render(
        request,
        "admin_pages/refund_detail.html",
        {
            "refund":
                refund,

            "booking":
                refund.booking,

            "payment":
                refund.payment,
        },
    )




# =========================================================
# ADMIN REJECT REFUND
# =========================================================

@_admin_required
@require_POST
def refund_reject(
    request,
    refund_id,
):

    refund = get_object_or_404(
        Refund,
        refund_id=
            refund_id,
    )


    # Only requested refunds can be rejected
    if refund.status != "requested":

        messages.error(
            request,
            "This refund request cannot be rejected."
        )

        return redirect(
            "refund_detail",
            refund_id=
                refund.refund_id,
        )


    admin_note = (
        request.POST.get(
            "admin_note",
            ""
        )
        .strip()
    )


    if not admin_note:

        messages.error(
            request,
            "Please enter a reason for rejecting the refund."
        )

        return redirect(
            "refund_detail",
            refund_id=
                refund.refund_id,
        )


    refund.status = "rejected"

    refund.admin_note = (
        admin_note
    )


    refund.save(
        update_fields=[
            "status",
            "admin_note",
            "updated_at",
        ]
    )


    messages.success(
        request,
        "Refund request rejected."
    )


    return redirect(
        "refund_detail",
        refund_id=
            refund.refund_id,
    )   




# =========================================================
# ADMIN APPROVE REFUND
#
# Razorpay refund processing will be implemented
# in the next step.
# =========================================================

# =========================================================
# ADMIN APPROVE REFUND
# =========================================================

@_admin_required
@require_POST
def refund_approve(
    request,
    refund_id,
):

    # =====================================================
    # LOCK REFUND ROW
    #
    # Prevent two admins/processes from approving
    # the same refund simultaneously.
    # =====================================================

    with transaction.atomic():

        refund = get_object_or_404(

            Refund.objects
            .select_for_update()
            .select_related(
                "booking",
                "payment",
            ),

            refund_id=
                refund_id,
        )


        booking = (
            refund.booking
        )


        payment = (
            refund.payment
        )


        # =================================================
        # STATUS CHECK
        # =================================================

        if refund.status != "requested":

            messages.error(
                request,
                (
                    "This refund request has already "
                    "been processed or cannot be approved."
                )
            )

            return redirect(
                "refund_detail",
                refund_id=
                    refund.refund_id,
            )


        # =================================================
        # PAYMENT CHECK
        # =================================================

        if payment.status != "paid":

            messages.error(
                request,
                (
                    "This payment is not in a valid "
                    "state for refund."
                )
            )

            return redirect(
                "refund_detail",
                refund_id=
                    refund.refund_id,
            )


        # =================================================
        # RAZORPAY PAYMENT ID
        # =================================================

        if not payment.gateway_payment_id:

            messages.error(
                request,
                (
                    "Razorpay payment ID is missing. "
                    "Refund cannot be processed."
                )
            )

            return redirect(
                "refund_detail",
                refund_id=
                    refund.refund_id,
            )


        # =================================================
        # REFUND AMOUNT
        # =================================================

        refund_amount = (
            Decimal(
                str(
                    refund.refund_amount
                )
            )
        )


        if refund_amount <= Decimal("0.00"):

            messages.error(
                request,
                "Invalid refund amount."
            )

            return redirect(
                "refund_detail",
                refund_id=
                    refund.refund_id,
            )


        if refund_amount > payment.amount:

            messages.error(
                request,
                (
                    "Refund amount cannot exceed "
                    "the original payment amount."
                )
            )

            return redirect(
                "refund_detail",
                refund_id=
                    refund.refund_id,
            )


        # =================================================
        # MARK PROCESSING BEFORE API CALL
        # =================================================

        refund.status = "processing"

        refund.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )


    # =====================================================
    # CALL RAZORPAY
    #
    # Outside DB transaction so we don't keep a database
    # lock while waiting for an external API.
    # =====================================================

    try:

        razorpay_refund = (
            create_razorpay_refund(

                payment_id=
                    payment.gateway_payment_id,

                refund_amount=
                    refund_amount,

                booking_id=
                    booking.booking_id,

                refund_id=
                    refund.refund_id,
            )
        )


    except Exception as error:

        print(
            "RAZORPAY REFUND ERROR:",
            repr(error)
        )


        refund.status = "failed"

        refund.gateway_status = "failed"

        refund.admin_note = (
            f"Razorpay refund error: {str(error)}"
        )[:1000]


        refund.save(
            update_fields=[
                "status",
                "gateway_status",
                "admin_note",
                "updated_at",
            ]
        )


        messages.error(
            request,
            (
                "Razorpay could not process the refund. "
                "No successful refund was recorded."
            )
        )


        return redirect(
            "refund_detail",
            refund_id=
                refund.refund_id,
        )


    # =====================================================
    # READ RAZORPAY RESPONSE
    # =====================================================

    razorpay_refund_id = (
        razorpay_refund.get(
            "id",
            ""
        )
    )


    gateway_status = (
        razorpay_refund.get(
            "status",
            ""
        )
        or
        ""
    )


    refund.razorpay_refund_id = (
        razorpay_refund_id
    )

    refund.gateway_status = (
        gateway_status
    )


    # =====================================================
    # RAZORPAY ALREADY PROCESSED
    # =====================================================

    # =====================================================
# FIRST SAVE RAZORPAY RESPONSE
# =====================================================

    refund.razorpay_refund_id = (
    razorpay_refund_id
    )

    refund.gateway_status = (
    gateway_status
    )


    if gateway_status == "processed":

    # Keep it processing temporarily.
    # mark_refund_processed() will perform the complete
    # finalization in one place.

        refund.status = "processing"


    else:

        refund.status = "processing"


    refund.save(
       update_fields=[
        "razorpay_refund_id",
        "gateway_status",
        "status",
        "updated_at",
       ]
    )


# =====================================================
# RAZORPAY ALREADY COMPLETED THE REFUND
# =====================================================

    if gateway_status == "processed":

        mark_refund_processed(
           razorpay_refund_id=
            razorpay_refund_id,

            gateway_status=
            gateway_status,
        )


    # Refresh because helper changed status
        refund.refresh_from_db()


    # =====================================================
    # SUCCESS MESSAGE
    # =====================================================

    if refund.status == "processed":

        messages.success(
            request,
            (
                f"Refund of ₹{refund.refund_amount} "
                "has been processed successfully."
            )
        )

    else:

        messages.success(
            request,
            (
                f"Refund of ₹{refund.refund_amount} "
                "has been submitted to Razorpay "
                "and is being processed."
            )
        )


    return redirect(
        "refund_detail",
        refund_id=
            refund.refund_id,
    )



import json
import hmac
import hashlib

from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from flyingfox_app.models import Refund


@csrf_exempt
@require_POST
def razorpay_refund_webhook(request):

    # =====================================================
    # RAW BODY
    #
    # IMPORTANT:
    # Signature must be verified using the ORIGINAL
    # unmodified request body.
    # =====================================================

    raw_body = request.body


    # =====================================================
    # RAZORPAY SIGNATURE
    # =====================================================

    received_signature = (
        request.headers.get(
            "X-Razorpay-Signature",
            "",
        )
        or
        ""
    )


    if not received_signature:

        print(
            "RAZORPAY REFUND WEBHOOK: "
            "Missing X-Razorpay-Signature"
        )

        return JsonResponse(
            {
                "success": False,
                "message": "Webhook signature missing.",
            },
            status=400,
        )


    # =====================================================
    # WEBHOOK SECRET
    # =====================================================

    webhook_secret = getattr(
        settings,
        "RAZORPAY_REFUND_WEBHOOK_SECRET",
        "",
    )


    if not webhook_secret:

        print(
            "RAZORPAY REFUND WEBHOOK: "
            "Webhook secret is not configured."
        )

        return JsonResponse(
            {
                "success": False,
                "message": "Webhook is not configured.",
            },
            status=500,
        )


    # =====================================================
    # VERIFY SIGNATURE
    #
    # Razorpay:
    # HMAC SHA256(raw request body, webhook secret)
    # =====================================================

    expected_signature = hmac.new(
        webhook_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()


    if not hmac.compare_digest(
        expected_signature,
        received_signature,
    ):

        print(
            "RAZORPAY REFUND WEBHOOK: "
            "Invalid signature."
        )

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid webhook signature.",
            },
            status=400,
        )


    # =====================================================
    # PARSE JSON ONLY AFTER SIGNATURE VERIFICATION
    # =====================================================

    try:

        payload = json.loads(
            raw_body.decode("utf-8")
        )

    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as error:

        print(
            "RAZORPAY REFUND WEBHOOK JSON ERROR:",
            repr(error),
        )

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid JSON payload.",
            },
            status=400,
        )


    # =====================================================
    # EVENT
    # =====================================================

    event = (
        payload.get(
            "event",
            "",
        )
        or
        ""
    )


    print(
        "============================================="
    )
    print(
        "RAZORPAY REFUND WEBHOOK RECEIVED"
    )
    print(
        "EVENT:",
        event,
    )


    # =====================================================
    # WE ONLY CARE ABOUT REFUND EVENTS
    # =====================================================

    supported_events = {
        "refund.created",
        "refund.processed",
        "refund.failed",
        "refund.speed_changed",
    }


    if event not in supported_events:

        print(
            "IGNORED EVENT:",
            event,
        )

        return JsonResponse(
            {
                "success": True,
                "message": "Event ignored.",
            },
            status=200,
        )


    # =====================================================
    # REFUND ENTITY
    # =====================================================

    refund_entity = (
        payload
        .get(
            "payload",
            {},
        )
        .get(
            "refund",
            {},
        )
        .get(
            "entity",
            {},
        )
    )


    if not refund_entity:

        print(
            "RAZORPAY REFUND WEBHOOK: "
            "Refund entity missing."
        )

        return JsonResponse(
            {
                "success": False,
                "message": "Refund entity missing.",
            },
            status=400,
        )


    # =====================================================
    # RAZORPAY DATA
    # =====================================================

    razorpay_refund_id = (
        refund_entity.get(
            "id",
            "",
        )
        or
        ""
    )


    razorpay_payment_id = (
        refund_entity.get(
            "payment_id",
            "",
        )
        or
        ""
    )


    gateway_status = (
        refund_entity.get(
            "status",
            "",
        )
        or
        ""
    )


    amount_paise = (
        refund_entity.get(
            "amount",
            0,
        )
        or
        0
    )


    # =====================================================
    # NOTES
    #
    # We added refund_id when creating the Razorpay refund.
    # This gives us a very useful fallback.
    # =====================================================

    notes = (
        refund_entity.get(
            "notes",
            {},
        )
        or
        {}
    )


    local_refund_id = (
        notes.get(
            "refund_id",
            "",
        )
        or
        ""
    )


    # =====================================================
    # ARN
    # =====================================================

    acquirer_data = (
        refund_entity.get(
            "acquirer_data",
            {},
        )
        or
        {}
    )


    arn = (
        acquirer_data.get(
            "arn",
            "",
        )
        or
        ""
    )


    print(
        "RAZORPAY REFUND ID:",
        razorpay_refund_id,
    )

    print(
        "RAZORPAY PAYMENT ID:",
        razorpay_payment_id,
    )

    print(
        "GATEWAY STATUS:",
        gateway_status,
    )

    print(
        "LOCAL REFUND ID:",
        local_refund_id,
    )


    # =====================================================
    # PAYMENT/REFUND ID REQUIRED
    # =====================================================

    if not razorpay_refund_id:

        return JsonResponse(
            {
                "success": False,
                "message": "Razorpay refund ID missing.",
            },
            status=400,
        )


    # =====================================================
    # FIND LOCAL REFUND
    #
    # First try Razorpay refund ID.
    #
    # IMPORTANT:
    # There is a tiny race condition where Razorpay could
    # send the webhook before refund_approve() has saved
    # razorpay_refund_id locally.
    #
    # Therefore we fall back to our UUID stored in notes.
    # =====================================================

    refund = (
        Refund.objects
        .select_related(
            "booking",
            "payment",
        )
        .filter(
            razorpay_refund_id=
                razorpay_refund_id
        )
        .first()
    )


    if (
        not refund
        and
        local_refund_id
    ):

        refund = (
            Refund.objects
            .select_related(
                "booking",
                "payment",
            )
            .filter(
                refund_id=
                    local_refund_id
            )
            .first()
        )


    # =====================================================
    # UNKNOWN REFUND
    # =====================================================

    if not refund:

        print(
            "RAZORPAY REFUND WEBHOOK: "
            "Local refund not found.",
            razorpay_refund_id,
        )

        # Signature is valid, but this refund does not
        # belong to a local refund record we can identify.
        #
        # Return 200 so Razorpay does not repeatedly retry
        # an event that we cannot use.

        return JsonResponse(
            {
                "success": True,
                "message": "Refund not found locally.",
            },
            status=200,
        )


    # =====================================================
    # SAVE RAZORPAY REFUND ID IF WEBHOOK ARRIVED FIRST
    # =====================================================

    if not refund.razorpay_refund_id:

        refund.razorpay_refund_id = (
            razorpay_refund_id
        )

        refund.save(
            update_fields=[
                "razorpay_refund_id",
                "updated_at",
            ]
        )


    # =====================================================
    # SECURITY / DATA CONSISTENCY CHECK:
    # PAYMENT ID
    # =====================================================

    expected_payment_id = (
        refund.razorpay_payment_id
        or
        refund.payment.gateway_payment_id
        or
        ""
    )


    if (
        expected_payment_id
        and
        razorpay_payment_id
        and
        expected_payment_id
        !=
        razorpay_payment_id
    ):

        print(
            "RAZORPAY REFUND PAYMENT ID MISMATCH"
        )

        print(
            "LOCAL:",
            expected_payment_id,
        )

        print(
            "RAZORPAY:",
            razorpay_payment_id,
        )

        return JsonResponse(
            {
                "success": False,
                "message": "Payment ID mismatch.",
            },
            status=400,
        )


    # =====================================================
    # AMOUNT CHECK
    # =====================================================

    expected_amount_paise = int(
        (
            Decimal(
                str(
                    refund.refund_amount
                )
            )
            *
            Decimal("100")
        ).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )


    if (
        amount_paise
        and
        int(amount_paise)
        !=
        expected_amount_paise
    ):

        print(
            "RAZORPAY REFUND AMOUNT MISMATCH"
        )

        print(
            "LOCAL:",
            expected_amount_paise,
        )

        print(
            "RAZORPAY:",
            amount_paise,
        )

        return JsonResponse(
            {
                "success": False,
                "message": "Refund amount mismatch.",
            },
            status=400,
        )


    # =====================================================
    # REFUND PROCESSED
    # =====================================================

    if event == "refund.processed":

        result = mark_refund_processed(
            razorpay_refund_id=
                razorpay_refund_id,

            gateway_status=
                gateway_status
                or
                "processed",

            arn=
                arn,
        )


        if not result:

            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        "Refund could not be "
                        "processed locally."
                    ),
                },
                status=500,
            )


        print(
            "REFUND MARKED PROCESSED:",
            refund.refund_id,
        )


    # =====================================================
    # REFUND FAILED
    # =====================================================

    elif event == "refund.failed":

        result = mark_refund_failed(
            razorpay_refund_id=
                razorpay_refund_id,

            gateway_status=
                gateway_status
                or
                "failed",
        )


        if not result:

            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        "Refund failure could not "
                        "be recorded locally."
                    ),
                },
                status=500,
            )


        print(
            "REFUND MARKED FAILED:",
            refund.refund_id,
        )


    # =====================================================
    # CREATED / SPEED CHANGED
    # =====================================================

    else:

        if (
            refund.status
            not in [
                "processed",
                "failed",
            ]
        ):

            refund.status = (
                "processing"
            )

            refund.gateway_status = (
                gateway_status
            )

            if arn:

                refund.arn = arn


            refund.save(
                update_fields=[
                    "status",
                    "gateway_status",
                    "arn",
                    "updated_at",
                ]
            )


    print(
        "WEBHOOK COMPLETED"
    )

    print(
        "============================================="
    )


    return JsonResponse(
        {
            "success": True,
        },
        status=200,
    )