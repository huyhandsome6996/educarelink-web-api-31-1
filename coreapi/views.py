from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from datetime import datetime
import json

from .models import (
    CarePartner, Booking, Child, Service, Review
)

# ======================================================
# 1. RENDER PAGES (HTML)
# ======================================================

def home(request): return render(request, "home.html")
def trang_dangky(request): return render(request, "dangky.html")
def trang_dangnhap(request): return render(request, "dangnhap.html")


@login_required
def dashboard(request):
    # Lấy chế độ từ session, mặc định là 'parent'
    mode = request.session.get("mode", "parent")
    
    if mode == "carepartner":
        # Nếu đang ở chế độ đối tác, trả về giao diện làm việc
        return render(request, "carepartner_dashboard.html")
    else:
        # Nếu là phụ huynh, trả về giao diện đặt lịch cũ
        return render(request, "dashboard.html")
def trang_carepartner(request): return render(request, "carepartner_register.html")
def trang_tao_booking(request): return render(request, "booking_create.html")
def trang_jobs(request): return render(request, "booking_jobs.html")
def trang_ho_so(request): return render(request, "profile.html")
def trang_chi_tiet_booking(request): return render(request, "booking_detail.html")
def trang_chat(request): return render(request, "chat.html")
# ======================================================
# 2. AUTHENTICATION API
# ======================================================

@csrf_exempt
def api_dangky(request):
    data = json.loads(request.body)
    if User.objects.filter(username=data["username"]).exists():
        return JsonResponse({"status": "user_exists"})
    user = User.objects.create_user(
        username=data["username"], password=data["password"], email=data.get("email", "")
    )
    return JsonResponse({"status": "ok"})

@csrf_exempt
def api_dangnhap(request):
    data = json.loads(request.body)
    user = authenticate(username=data["username"], password=data["password"])
    if user:
        login(request, user)
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "fail"})

@csrf_exempt
def api_logout(request):
    logout(request)
    return JsonResponse({"status": "ok"})

def api_me(request):
    if request.user.is_authenticated:
        # Trả về thêm flag is_carepartner để Frontend ẩn/hiện nút đăng ký
        is_cp = CarePartner.objects.filter(user=request.user).exists()
        return JsonResponse({
            "login": True, "username": request.user.username, "is_carepartner": is_cp
        })
    return JsonResponse({"login": False})

# ======================================================
# 3. ROLE & MODE MANAGEMENT
# ======================================================

def api_get_mode(request):
    return JsonResponse({"mode": request.session.get("mode", "parent")})

@csrf_exempt
def api_switch_mode(request):
    data = json.loads(request.body)
    new_mode = data.get("mode")
    if new_mode == "carepartner":
        cp = CarePartner.objects.filter(user=request.user, trang_thai="approved").first()
        if not cp: return JsonResponse({"status": "not_approved"})
    request.session["mode"] = new_mode
    return JsonResponse({"status": "ok", "mode": new_mode})

# ======================================================
# 4. BOOKING CORE LOGIC (bTaskee Flow)
# ======================================================

def api_services(request):
    services = Service.objects.all().values("id", "ten", "mo_ta", "gia_moi_gio")
    return JsonResponse({"data": list(services)})

@csrf_exempt
def api_tinhgia(request):
    data = json.loads(request.body)
    try:
        service = Service.objects.get(id=data["service_id"])
        start = datetime.fromisoformat(data["start"].replace('Z', ''))
        end = datetime.fromisoformat(data["end"].replace('Z', ''))
        hours = (end - start).total_seconds() / 3600
        return JsonResponse({"status": "ok", "gia": int(hours * service.gia_moi_gio)})
    except: return JsonResponse({"status": "error"})

@csrf_exempt
@login_required
def api_booking_create(request):
    data = json.loads(request.body)
    service = Service.objects.get(id=data["service_id"])
    Booking.objects.create(
        parent=request.user, service=service,
        gio_bat_dau=data["start"], gio_ket_thuc=data["end"],
        dia_chi=data["dia_chi"], tre_mo_ta=data["tre_mo_ta"],
        yeu_cau=data.get("yeu_cau", ""), gia_tam_tinh=data["gia_tam_tinh"],
        status="pending"
    )
    return JsonResponse({"status": "ok"})

def api_jobs_open(request):
    # CarePartner xem danh sách các đơn chưa có ai nhận
    jobs = Booking.objects.filter(status="pending").select_related("service")
    data = [{
        "id": j.id, "service": j.service.ten, "address": j.dia_chi,
        "price": j.gia_tam_tinh, "desc": j.tre_mo_ta
    } for j in jobs]
    return JsonResponse({"data": data})

@csrf_exempt
@login_required
def api_booking_apply(request):
    # CarePartner ứng tuyển vào một đơn hàng
    data = json.loads(request.body)
    booking = Booking.objects.get(id=data["booking_id"], status="pending")
    booking.carepartner = request.user
    booking.status = "applied"
    booking.save()
    return JsonResponse({"status": "ok"})

def api_booking_detail(request, booking_id):
    # Phụ huynh xem chi tiết đơn để duyệt CarePartner
    try:
        b = Booking.objects.get(id=booking_id)
        cp_info = None
        if b.carepartner:
            cp = CarePartner.objects.get(user=b.carepartner)
            cp_info = {"name": b.carepartner.username, "truong": cp.truong, "rating": cp.rating_trung_binh}
        return JsonResponse({
            "id": b.id, "status": b.status, "service": b.service.ten, 
            "carepartner": cp_info, "desc": b.tre_mo_ta
        })
    except: return JsonResponse({"status": "error"})

@csrf_exempt
@login_required
def api_booking_confirm(request):
    # Phụ huynh chốt chọn CarePartner này
    data = json.loads(request.body)
    booking = Booking.objects.get(id=data["booking_id"], parent=request.user, status="applied")
    booking.status = "confirmed"
    booking.save()
    return JsonResponse({"status": "ok"})

@csrf_exempt
@login_required
def api_booking_start(request):
    data = json.loads(request.body)
    booking = Booking.objects.get(id=data["booking_id"], carepartner=request.user, status="confirmed")
    booking.status = "doing"
    booking.save()
    return JsonResponse({"status": "ok"})

@csrf_exempt
@login_required
def api_booking_done(request):
    data = json.loads(request.body)
    booking = Booking.objects.get(id=data["booking_id"], carepartner=request.user, status="doing")
    booking.status = "done"
    booking.save()
    return JsonResponse({"status": "ok"})

def api_my_bookings(request):
    # Lấy danh sách lịch sử cho Phụ huynh
    bookings = Booking.objects.filter(parent=request.user).order_by("-created_at")
    data = [{
        "id": b.id, "service": b.service.ten, "status": b.status, "price": b.gia_tam_tinh
    } for b in bookings]
    return JsonResponse({"data": data})

# ... (các import cũ giữ nguyên)
# Đảm bảo bạn đã import CarePartner và JsonResponse

@csrf_exempt
@login_required
def api_dangky_carepartner(request):
    if request.method == "POST":
        try:
            # 1. Kiểm tra xem user này đã đăng ký chưa
            if CarePartner.objects.filter(user=request.user).exists():
                return JsonResponse({"status": "already_registered"})

            # 2. Lấy dữ liệu text từ request.POST
            chuyen_nganh = request.POST.get("chuyen_nganh")
            truong = request.POST.get("truong")
            ky_nang = request.POST.get("ky_nang")

            # 3. Lấy file ảnh từ request.FILES
            anh_cccd = request.FILES.get("anh_cccd")
            bang_cap = request.FILES.get("bang_cap")

            # Kiểm tra file bắt buộc
            if not anh_cccd or not bang_cap:
                return JsonResponse({"status": "error", "msg": "Vui lòng tải lên đủ ảnh CCCD và Bằng cấp"})

            # 4. Tạo bản ghi CarePartner mới
            cp = CarePartner.objects.create(
                user=request.user,
                chuyen_nganh=chuyen_nganh,
                truong=truong,
                ky_nang=ky_nang,
                anh_cccd=anh_cccd,
                bang_cap=bang_cap,
                trang_thai="pending", # Chờ admin duyệt
                rating_trung_binh=0,
                tong_so_danh_gia=0
            )
            
            return JsonResponse({"status": "ok"})

        except Exception as e:
            print("Lỗi đăng ký:", str(e)) # In lỗi ra terminal để debug
            return JsonResponse({"status": "error", "msg": str(e)})

    return JsonResponse({"status": "error", "msg": "Sai phương thức request"})


# Trong views.py

@login_required
def api_my_jobs(request):
    """API lấy danh sách công việc ĐÃ ĐƯỢC DUYỆT của CarePartner"""
    # Lọc các đơn mà user hiện tại là carepartner VÀ trạng thái là confirmed hoặc doing
    jobs = Booking.objects.filter(
        carepartner=request.user, 
        status__in=["confirmed", "doing", "done"]
    ).order_by("-gio_bat_dau") # Sắp xếp mới nhất lên đầu

    data = [{
        "id": j.id,
        "service": j.service.ten,
        "parent": j.parent.username, # Hoặc j.parent.last_name nếu có
        "address": j.dia_chi,
        "time": j.gio_bat_dau.strftime("%H:%M %d/%m"), # Giờ và ngày
        "price": j.gia_tam_tinh,
        "status": j.status
    } for j in jobs]
    
    return JsonResponse({"data": data})