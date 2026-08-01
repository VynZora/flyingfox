from django.urls import path
from . import views

urlpatterns = [

    # Admin authentication
    path("admin-login/", views.admin_login, name="admin_login"),
    path("admin-logout/", views.admin_logout, name="admin_logout"),

    # Dashboard
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),


     # =========================
# GALLERY CATEGORY
# =========================
# ==========================================
# GALLERY CATEGORIES
# ==========================================

path(
    "dashboard/categories/",
    views.category_list,
    name="category_list"
),

path(
    "dashboard/categories/add/",
    views.add_category,
    name="add_category"
),

path(
    "dashboard/categories/<int:pk>/edit/",
    views.update_category,
    name="update_category"
),

path(
    "dashboard/categories/<int:pk>/delete/",
    views.delete_category,
    name="delete_category"
),


# ==========================================
# GALLERY
# ==========================================

path(
    "dashboard/gallery/",
    views.gallery_items,
    name="list_image"
),

path(
    "dashboard/gallery/add/",
    views.add_gallery_item,
    name="add_image"
),

path(
    "dashboard/gallery/<int:item_id>/edit/",
    views.update_gallery_item,
    name="update_image"
),

path(
    "dashboard/gallery/<int:item_id>/delete/",
    views.delete_gallery_item,
    name="delete_image"
),


# ==========================================
# BLOGS
# ==========================================

path(
    "dashboard/blogs/",
    views.admin_blog_list,
    name="admin_blog_list"
),

path(
    "dashboard/blogs/create/",
    views.blog_create,
    name="blog_create"
),

path(
    "dashboard/blogs/<int:pk>/edit/",
    views.blog_update,
    name="blog_update"
),

path(
    "dashboard/blogs/<int:pk>/delete/",
    views.blog_delete,
    name="blog_delete"
),

# ==========================================
# contact 
# ==========================================
 path('dashboard/contacts/', views.view_contacts, name='view_contacts'),
 path('dashboard/contacts/<int:pk>/delete/', views.delete_contact, name='delete_contact'),


# ==========================================
# USERS
# ==========================================

path("dashboard/users/",views.user_list,name="user_list"),
path(
    "dashboard/users/<int:pk>/delete/",
    views.user_delete,
    name="user_delete"
),


# ==========================================
# RIDES
# ==========================================

path(
    "dashboard/rides/",
    views.ride_list,
    name="ride_list"
),

path(
    "dashboard/rides/add/",
    views.ride_create,
    name="ride_create"
),

path(
    "dashboard/rides/<int:pk>/edit/",
    views.ride_update,
    name="ride_update"
),

path(
    "dashboard/rides/<int:pk>/delete/",
    views.ride_delete,
    name="ride_delete"
),

path(
    "dashboard/rides/media/<int:pk>/delete/",
    views.ride_media_delete,
    name="ride_media_delete"
),




# ==========================================
# RIDE PRICE
# ==========================================

path(
    "dashboard/ride-prices/",
    views.ride_price_list,
    name="ride_price_list"
),

path(
    "dashboard/ride-prices/add/",
    views.ride_price_create,
    name="ride_price_create"
),

path(
    "dashboard/ride-prices/<int:pk>/update/",
    views.ride_price_update,
    name="ride_price_update"
),

path(
    "dashboard/ride-prices/<int:pk>/delete/",
    views.ride_price_delete,
    name="ride_price_delete"
),




# ==========================================
# BOOKINGS
# ==========================================

path(
    "dashboard/bookings/",
    views.booking_list,
    name="booking_list"
),

path(
    "dashboard/bookings/add/",
    views.booking_create,
    name="booking_create"
),

path(
    "dashboard/bookings/<int:pk>/",
    views.booking_detail,
    name="booking_detail"
),

path(
    "dashboard/bookings/<int:pk>/edit/",
    views.booking_update,
    name="booking_update"
),

path(
    "dashboard/bookings/<int:pk>/status/",
    views.booking_status_update,
    name="booking_status_update"
),

path(
    "dashboard/bookings/<int:pk>/delete/",
    views.booking_delete,
    name="booking_delete"
),


# ==========================================
# transaction
# ==========================================
path(
    "dashboard/transactions/",
    views.transaction_list,
    name="transaction_list"
),

path(
    "dashboard/transactions/<int:pk>/",
    views.transaction_detail,
    name="transaction_detail"
),


# ==========================================
# COUPONS
# ==========================================

path(
    "dashboard/coupons/",
    views.coupon_list,
    name="coupon_list"
),

path(
    "dashboard/coupons/add/",
    views.coupon_create,
    name="coupon_create"
),

path(
    "dashboard/coupons/<int:pk>/edit/",
    views.coupon_update,
    name="coupon_update"
),

path(
    "dashboard/coupons/<int:pk>/delete/",
    views.coupon_delete,
    name="coupon_delete"
),



# ===============================
# USER AUTHENTICATION
# ===============================

path(
    "signup/",
    views.user_signup,
    name="user_signup"
),

path(
    "signin/",
    views.user_signin,
    name="user_signin"
),

path(
    "logout/",
    views.user_logout,
    name="user_logout"
),



 path('', views.home, name='home'),

  path('rides/', views.rides, name='rides'),

    path(
        'rides/<slug:slug>/',
        views.ride_detail,
        name='ride_detail'
    ),

    # path(
    #     'gallery/',
    #     views.gallery,
    #     name='gallery'
    # ),

    # path(
    #     'about/',
    #     views.about,
    #     name='about'
    # ),

    # path(
    #     'contact/',
    #     views.contact,
    #     name='contact'
    # ),






]