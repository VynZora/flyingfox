from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.hashers import make_password, check_password

from .models import (
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
    Coupon
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

    paginator = Paginator(
        blogs_qs,
        10
    )

    page_number = request.GET.get("page")

    blogs = paginator.get_page(
        page_number
    )

    return render(
        request,
        "admin_pages/blog_list.html",
        {
            "blogs": blogs
        }
    )


@_admin_required
def blog_create(request):

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        short_description = request.POST.get(
            "short_description",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        image = request.FILES.get(
            "image"
        )

        is_published = (
            request.POST.get("is_published")
            == "on"
        )


        if not title:

            messages.error(
                request,
                "Blog title is required."
            )

            return render(
                request,
                "admin_pages/create_blog.html"
            )


        if not description:

            messages.error(
                request,
                "Blog description is required."
            )

            return render(
                request,
                "admin_pages/create_blog.html"
            )


        if not image:

            messages.error(
                request,
                "Blog image is required."
            )

            return render(
                request,
                "admin_pages/create_blog.html"
            )


        Blog.objects.create(
            title=title,
            short_description=short_description,
            description=description,
            image=image,
            is_published=is_published,
        )


        messages.success(
            request,
            "Blog created successfully."
        )


        return redirect(
            "admin_blog_list"
        )


    return render(
        request,
        "admin_pages/create_blog.html"
    )


@_admin_required
def blog_update(request, pk):

    blog = get_object_or_404(
        Blog,
        pk=pk
    )


    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        short_description = request.POST.get(
            "short_description",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()


        if not title:

            messages.error(
                request,
                "Blog title is required."
            )

            return render(
                request,
                "admin_pages/create_blog.html",
                {
                    "blog": blog
                }
            )


        if not description:

            messages.error(
                request,
                "Blog description is required."
            )

            return render(
                request,
                "admin_pages/create_blog.html",
                {
                    "blog": blog
                }
            )


        blog.title = title

        blog.short_description = (
            short_description
        )

        blog.description = description

        blog.is_published = (
            request.POST.get("is_published")
            == "on"
        )


        if request.FILES.get("image"):

            blog.image = request.FILES.get(
                "image"
            )


        blog.save()


        messages.success(
            request,
            "Blog updated successfully."
        )


        return redirect(
            "admin_blog_list"
        )


    return render(
        request,
        "admin_pages/create_blog.html",
        {
            "blog": blog
        }
    )


@_admin_required
def blog_delete(request, pk):

    blog = get_object_or_404(
        Blog,
        pk=pk
    )


    if request.method == "POST":

        blog.delete()

        messages.success(
            request,
            "Blog deleted successfully."
        )


    return redirect(
        "admin_blog_list"
    )



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

        is_active = (
            request.POST.get("is_active")
            == "on"
        )


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
                "admin_pages/ride_form.html"
            )


        if not description:

            messages.error(
                request,
                "Description is required."
            )

            return render(
                request,
                "admin_pages/ride_form.html"
            )


        if not duration:

            messages.error(
                request,
                "Duration is required."
            )

            return render(
                request,
                "admin_pages/ride_form.html"
            )


        # ==========================
        # CREATE RIDE
        # ==========================

        ride = Ride.objects.create(
            name=name,
            description=description,
            duration=duration,
            safety_notes=safety_notes,
            is_active=is_active,
        )


        # ==========================
        # MULTIPLE IMAGES
        # ==========================

        images = request.FILES.getlist(
            "images"
        )

        for image in images:

            RideMedia.objects.create(
                ride=ride,
                media_type="image",
                image=image
            )


        # ==========================
        # SINGLE VIDEO
        # ==========================

        video = request.FILES.get(
            "video"
        )

        if video:

            RideMedia.objects.create(
                ride=ride,
                media_type="video",
                video=video
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

@login_required(login_url="admin_login")
def ride_update(request, pk):

    ride = get_object_or_404(
        Ride,
        pk=pk
    )

    if request.method == "POST":

        ride.name = request.POST.get(
            "name",
            ""
        ).strip()

        ride.description = request.POST.get(
            "description",
            ""
        ).strip()

        ride.duration = request.POST.get(
            "duration",
            ""
        ).strip()

        ride.safety_notes = request.POST.get(
            "safety_notes",
            ""
        ).strip()

        ride.is_active = (
            request.POST.get("is_active")
            == "on"
        )

        ride.save()


        # Add new images
        images = request.FILES.getlist(
            "images"
        )

        for image in images:

            RideMedia.objects.create(
                ride=ride,
                media_type="image",
                image=image
            )


        # Add new video
        video = request.FILES.get(
            "video"
        )

        video_url = request.POST.get(
            "video_url",
            ""
        ).strip()

        thumbnail = request.FILES.get(
            "thumbnail"
        )


        if video or video_url:

            RideMedia.objects.create(
                ride=ride,
                media_type="video",
                video=video,
                video_url=video_url or None,
                thumbnail=thumbnail,
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
            "ride": ride
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
            "user",
            "ride",
            "ride_price",
        )
        .prefetch_related(
            "participants"
        )
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


    if search:

        bookings_qs = bookings_qs.filter(
            Q(user__full_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(user__phone__icontains=search) |
            Q(ride__name__icontains=search)
        )


    if status:

        bookings_qs = bookings_qs.filter(
            status=status
        )


    paginator = Paginator(
        bookings_qs,
        10
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
        }
    )



@_admin_required
@transaction.atomic
def booking_create(request):

    users = UserProfile.objects.all().order_by(
        "full_name"
    )

    rides = Ride.objects.filter(
        is_active=True
    ).order_by(
        "name"
    )

    prices = (
        RidePrice.objects
        .filter(is_active=True)
        .select_related("ride")
        .order_by("ride__name", "-start_date")
    )


    if request.method == "POST":

        user_id = request.POST.get("user")
        ride_id = request.POST.get("ride")
        ride_price_id = request.POST.get("ride_price")

        booking_date = request.POST.get(
            "booking_date"
        )

        quantity_raw = request.POST.get(
            "quantity",
            "1"
        )


        try:
            quantity = int(quantity_raw)
        except (TypeError, ValueError):
            quantity = 0


        if quantity < 1:

            messages.error(
                request,
                "Quantity must be at least 1."
            )

            return redirect(
                "booking_create"
            )


        user = get_object_or_404(
            UserProfile,
            pk=user_id
        )

        ride = get_object_or_404(
            Ride,
            pk=ride_id
        )

        ride_price = get_object_or_404(
            RidePrice,
            pk=ride_price_id
        )


        # Make sure selected price belongs to ride
        if ride_price.ride_id != ride.id:

            messages.error(
                request,
                "Selected price does not belong to this ride."
            )

            return redirect(
                "booking_create"
            )


        # Make sure selected date is within price validity
        if booking_date:

            from datetime import datetime

            selected_date = datetime.strptime(
                booking_date,
                "%Y-%m-%d"
            ).date()

            if not (
                ride_price.start_date
                <= selected_date
                <= ride_price.end_date
            ):

                messages.error(
                    request,
                    "The selected price is not valid for this booking date."
                )

                return redirect(
                    "booking_create"
                )


        price_per_person = ride_price.price

        subtotal = (
            price_per_person
            * Decimal(quantity)
        )


        booking = Booking.objects.create(
            user=user,
            ride=ride,
            ride_price=ride_price,
            booking_date=booking_date,
            quantity=quantity,
            price_per_person=price_per_person,
            subtotal=subtotal,
            total_amount=subtotal,
            status="pending",
        )


        # =====================================
        # PARTICIPANTS
        # =====================================

        participant_names = request.POST.getlist(
            "participant_name"
        )

        participant_ages = request.POST.getlist(
            "participant_age"
        )


        for index in range(quantity):

            if index >= len(participant_names):
                continue

            name = participant_names[index].strip()

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


            BookingPerson.objects.create(
                booking=booking,
                full_name=name,
                age=age,
            )


        messages.success(
            request,
            "Booking created successfully."
        )

        return redirect(
            "booking_detail",
            pk=booking.pk
        )


    return render(
        request,
        "admin_pages/booking_form.html",
        {
            "users": users,
            "rides": rides,
            "prices": prices,
        }
    )



@_admin_required
@transaction.atomic
def booking_update(request, pk):

    booking = get_object_or_404(
        Booking.objects.select_related(
            "user",
            "ride",
            "ride_price",
        ),
        pk=pk
    )

    users = UserProfile.objects.all().order_by(
        "full_name"
    )

    rides = Ride.objects.filter(
        is_active=True
    ).order_by(
        "name"
    )

    prices = (
        RidePrice.objects
        .filter(is_active=True)
        .select_related("ride")
    )


    if request.method == "POST":

        user = get_object_or_404(
            UserProfile,
            pk=request.POST.get("user")
        )

        ride = get_object_or_404(
            Ride,
            pk=request.POST.get("ride")
        )

        ride_price = get_object_or_404(
            RidePrice,
            pk=request.POST.get("ride_price")
        )

        booking_date = request.POST.get(
            "booking_date"
        )

        quantity = int(
            request.POST.get(
                "quantity",
                1
            )
        )


        if ride_price.ride_id != ride.id:

            messages.error(
                request,
                "Selected price does not belong to this ride."
            )

            return redirect(
                "booking_update",
                pk=booking.pk
            )


        price_per_person = (
            ride_price.price
        )

        subtotal = (
            price_per_person
            * Decimal(quantity)
        )


        booking.user = user
        booking.ride = ride
        booking.ride_price = ride_price
        booking.booking_date = booking_date
        booking.quantity = quantity
        booking.price_per_person = price_per_person
        booking.subtotal = subtotal
        booking.total_amount = subtotal

        booking.save()


        messages.success(
            request,
            "Booking updated successfully."
        )

        return redirect(
            "booking_detail",
            pk=booking.pk
        )


    return render(
        request,
        "admin_pages/booking_form.html",
        {
            "booking": booking,
            "users": users,
            "rides": rides,
            "prices": prices,
        }
    )



@_admin_required
def booking_detail(request, pk):

    booking = get_object_or_404(
        Booking.objects.select_related(
            "user",
            "ride",
            "ride_price",
        ).prefetch_related(
            "participants"
        ),
        pk=pk
    )


    payment = None
    ticket = None


    try:
        payment = booking.payment
    except Payment.DoesNotExist:
        pass


    try:
        ticket = booking.ticket
    except Ticket.DoesNotExist:
        pass


    return render(
        request,
        "admin_pages/booking_detail.html",
        {
            "booking": booking,
            "payment": payment,
            "ticket": ticket,
        }
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
        return redirect("home")


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

    rides = Ride.objects.filter(
        is_active=True
    )

    return render(
        request,
        'frontend/index.html',
        {
             'rides': rides
        }
    )


def rides(request):

    rides = Ride.objects.filter(
        is_active=True
    )

    return render(
        request,
        'frontend/rides.html',
        {
            'rides': rides
        }
    )


from django.shortcuts import get_object_or_404


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