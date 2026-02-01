from django.urls import path
from . import views


urlpatterns = [

    # =============================
    # WEB PAGES
    # =============================
    path('', views.home),

    path('dangky/', views.trang_dangky),
    path('dangnhap/', views.trang_dangnhap),

    path('carepartner/', views.trang_carepartner),

    path('booking/create/', views.trang_tao_booking),
    path('booking/jobs/', views.trang_jobs),


    # =============================
    # AUTH API
    # =============================
    path('api/dangky/', views.api_dangky),
    path('api/dangnhap/', views.api_dangnhap),
    path('api/logout/', views.api_logout),
    path('api/me/', views.api_me),


    # =============================
    # CARE PARTNER API
    # =============================
    path(
        'api/carepartner/register/',
        views.api_dangky_carepartner
    ),

    path(
        'api/carepartners/',
        views.api_danhsach_carepartner
    ),


    # =============================
    # CHILD MANAGEMENT
    # =============================
    path(
        'api/child/create/',
        views.api_child_create
    ),

    path(
        'api/child/list/',
        views.api_child_list
    ),

    path(
        'api/child/delete/<int:child_id>/',
        views.api_child_delete
    ),


    # =============================
    # SERVICES
    # =============================
    path(
        'api/services/',
        views.api_services
    ),


    # =============================
    # BOOKING API
    # =============================
    path("api/booking/create/",views.api_booking_create),
path("api/booking/apply/",views.api_booking_apply),
path("api/booking/confirm/",views.api_booking_confirm),
    path(
        'api/booking/open/',
        views.api_booking_open
    ),

    path(
        'api/booking/<int:booking_id>/accept/',
        views.api_booking_nhan
    ),

    path(
        'api/booking/<int:booking_id>/start/',
        views.api_booking_start
    ),

    path(
        'api/booking/<int:booking_id>/done/',
        views.api_booking_done
    ),

    path(
        'api/booking/<int:booking_id>/cancel/',
        views.api_booking_cancel
    ),


    # =============================
    # REVIEW API
    # =============================
    path(
        'api/review/<int:booking_id>/',
        views.api_review_create
    ),


    # =============================
    # MATCHING JOB
    # =============================
    path(
        'api/jobs/priority/',
        views.api_jobs_priority
    ),


    # =============================
    # CHATBOT AI
    # =============================
    



path('dashboard/', views.dashboard),
path("api/booking/<int:booking_id>/start/", views.api_booking_start),
path("account/", views.trang_tai_khoan),
path("profile/", views.trang_ho_so),
path("api/mode/", views.api_get_mode),
path("api/mode/switch/", views.api_switch_mode),
path("api/jobs/open/", views.api_jobs_open),
path("api/booking/nhan/", views.api_booking_nhan),
path("api/tinhgia/", views.api_tinhgia),
path("api/my-bookings/",views.api_my_bookings),
path("api/parent-confirm/",views.api_parent_confirm),


]
