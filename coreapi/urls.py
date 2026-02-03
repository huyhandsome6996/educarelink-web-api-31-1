from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('', views.home),
    path('dangky/', views.trang_dangky),
    path('dangnhap/', views.trang_dangnhap),
    path('dashboard/', views.dashboard),
    path('carepartner/', views.trang_carepartner),
    path('booking/create/', views.trang_tao_booking),
    path('booking/jobs/', views.trang_jobs),
    path('profile/', views.trang_ho_so),

    # Auth & Mode
    path('api/dangky/', views.api_dangky),
    path('api/dangnhap/', views.api_dangnhap),
    path('api/logout/', views.api_logout),
    path('api/me/', views.api_me),
    path('api/mode/', views.api_get_mode),
    path('api/mode/switch/', views.api_switch_mode),

    # Core Business Logic (bTaskee Flow)
    path('api/services/', views.api_services),
    path('api/tinhgia/', views.api_tinhgia),
    
    # Booking Flow
    path('api/booking/create/', views.api_booking_create),     # Parent tạo đơn
    path('api/jobs/open/', views.api_jobs_open),               # CP xem đơn trống
    path('api/booking/apply/', views.api_booking_apply),       # CP ứng tuyển
    path('api/my-bookings/', views.api_my_bookings),           # PH xem danh sách đơn của mình
    path('api/booking/<int:booking_id>/', views.api_booking_detail), # Xem chi tiết (PH soi profile CP)
    path('api/booking/confirm/', views.api_booking_confirm),   # PH chốt CP
    path('api/booking/start/', views.api_booking_start),       # CP bắt đầu làm
    path('api/booking/done/', views.api_booking_done),         # CP hoàn thành
    path('api/carepartner/register/', views.api_dangky_carepartner),
    path('booking/detail/', views.trang_chi_tiet_booking), 
    
    path('profile/', views.trang_ho_so),
    path('api/my-jobs/', views.api_my_jobs),
]