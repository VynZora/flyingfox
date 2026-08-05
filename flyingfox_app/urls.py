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

 # Admin - Testimonials
    path('dashboard/testimonials/', views.testimonial_list, name='review_list'),
    path('dashboard/testimonials/add/', views.testimonial_create, name='testimonial_create'),
    path('dashboard/testimonials/<int:pk>/edit/', views.testimonial_update, name='testimonial_update'),
    path('dashboard/testimonials/<int:pk>/delete/', views.testimonial_delete, name='testimonial_delete'),




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

path('bookings/', views.bookings, name='bookings'),
path(
        "booking/review/",
        views.booking_review,
        name="booking_review",
    ),

   # Temporary fake payment success
    path(
        "booking/temporary-payment-success/",
        views.temporary_payment_success,
        name="temporary_payment_success",
    ),

    path(
        "booking/success/<uuid:booking_id>/",
        views.booking_success,
        name="booking_success",
    ),

    path(
        "ticket/download/<uuid:ticket_id>/",
        views.download_ticket,
        name="download_ticket",
    ),

    path(
        "ticket/verify/<uuid:qr_token>/",
        views.verify_ticket,
        name="verify_ticket",
    ),








# ==========================================
# STATIC FRONTEND PAGES
# ==========================================

path(
    "about/",
    views.about,
    name="about"
),

path(
    "activity/",
    views.activity,
    name="activity"
),

path(
    "activity-single/",
    views.activity_single,
    name="activity_single"
),

path(
    "blog/",
    views.blog,
    name="blog"
),

path(
    "blog-single/",
    views.blog_single,
    name="blog_single"
),

path(
    "contact/",
    views.contact,
    name="contact"
),

path(
    "destination/",
    views.destination,
    name="destination"
),

path(
    "destination-single/",
    views.destination_single,
    name="destination_single"
),

path(
    "destination-2/",
    views.destination_two,
    name="destination_two"
),

path(
    "faq/",
    views.faq,
    name="faq"
),

path(
    "gallery/",
    views.gallery,
    name="gallery"
),

path(
    "login/",
    views.login_page,
    name="login_page"
),

path(
    "register/",
    views.register,
    name="register"
),

path(
    "team/",
    views.team,
    name="team"
),

path(
    "privacy/",
    views.privacy,
    name="privacy"
),

path(
    "terms/",
    views.terms,
    name="terms"
),

path(
    "testimonial/",
    views.testimonial,
    name="testimonial"
),

path(
    "tour-2/",
    views.tour_two,
    name="tour_two"
),

path(
    "forgot-password/",
    views.forgot_password,
    name="forgot_password"
),

path(
    "coming-soon/",
    views.coming_soon,
    name="coming_soon"
),

path(
    "404/",
    views.page_404,
    name="page_404"
),



# Chatbot rule management
path(
    "dashboard/chatbot/rules/",
    views.chatbot_rule_list,
    name="chatbot_rule_list",
),

path(
    "dashboard/chatbot/rules/create/",
    views.chatbot_rule_create,
    name="chatbot_rule_create",
),

path(
    "dashboard/chatbot/rules/<int:pk>/update/",
    views.chatbot_rule_update,
    name="chatbot_rule_update",
),

path(
    "dashboard/chatbot/rules/<int:pk>/delete/",
    views.chatbot_rule_delete,
    name="chatbot_rule_delete",
),

path(
    "dashboard/chatbot/rules/<int:pk>/toggle-status/",
    views.chatbot_rule_toggle_status,
    name="chatbot_rule_toggle_status",
),

path(
    "chatbot/initialize/",
    views.chatbot_initialize,
    name="chatbot_initialize",
),

path(
    "chatbot/message/",
    views.chatbot_message,
    name="chatbot_message",
),




# Chat sessions

path(
    "dashboard/chatbot/sessions/",
    views.chat_session_list,
    name="chat_session_list",
),

path(
    "dashboard/chatbot/sessions/<int:pk>/",
    views.chat_session_detail,
    name="chat_session_detail",
),

path(
    "dashboard/chatbot/sessions/<int:pk>/toggle-status/",
    views.chat_session_toggle_status,
    name="chat_session_toggle_status",
),

path(
    "dashboard/chatbot/sessions/<int:pk>/delete/",
    views.chat_session_delete,
    name="chat_session_delete",
),


# Chat enquiries

path(
    "dashboard/chatbot/enquiries/",
    views.chat_enquiry_list,
    name="chat_enquiry_list",
),

path(
    "dashboard/chatbot/enquiries/<int:pk>/",
    views.chat_enquiry_detail,
    name="chat_enquiry_detail",
),

path(
    "dashboard/chatbot/enquiries/<int:pk>/status/",
    views.chat_enquiry_update_status,
    name="chat_enquiry_update_status",
),

path(
    "dashboard/chatbot/enquiries/<int:pk>/delete/",
    views.chat_enquiry_delete,
    name="chat_enquiry_delete",
),



# blog
path(
    "blogs/<slug:slug>/",
    views.blog_detail,
    name="blog_detail",
),



]