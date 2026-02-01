from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
import json

from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime
from datetime import datetime
from .models import (
    CarePartner,
    Booking,
    Child,
    Service,
    Review,
    ChatSession,
    ChatMessage
)
import os





# ======================================================
# WEB PAGES
# ======================================================

def home(request):
    return render(request, "home.html")


def trang_dangky(request):
    return render(request, "dangky.html")


def trang_dangnhap(request):
    return render(request, "dangnhap.html")


def trang_carepartner(request):
    return render(request, "carepartner_register.html")


def trang_tao_booking(request):
    return render(request, "booking_create.html")


def trang_jobs(request):
    return render(request, "booking_jobs.html")


# ======================================================
# PHẦN 1 — AUTH
# ======================================================

@csrf_exempt
def api_dangky(request):
    if request.method != "POST":
        return JsonResponse({"status": "POST_required"})

    data = json.loads(request.body)

    if User.objects.filter(username=data["username"]).exists():
        return JsonResponse({"status": "user_exists"})

    user = User.objects.create_user(
        username=data["username"],
        password=data["password"],
        email=data.get("email", "")
    )

    return JsonResponse({"status": "ok", "user_id": user.id})


@csrf_exempt
def api_dangnhap(request):
    if request.method != "POST":
        return JsonResponse({"status": "POST_required"})

    data = json.loads(request.body)

    user = authenticate(
        username=data["username"],
        password=data["password"]
    )

    if user:
        login(request, user)
        return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "fail"})


@csrf_exempt
def api_logout(request):
    logout(request)
    return JsonResponse({"status": "logged_out"})


def api_me(request):
    if request.user.is_authenticated:
        return JsonResponse({
            "login": True,
            "username": request.user.username,
            "user_id": request.user.id
        })

    return JsonResponse({"login": False})


# ======================================================
# PHẦN 2 — CARE PARTNER
# ======================================================

@csrf_exempt
def api_dangky_carepartner(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "login_required"})

    if request.method != "POST":
        return JsonResponse({"status": "POST_required"})

    if CarePartner.objects.filter(user=request.user).exists():
        return JsonResponse({"status": "already_registered"})

    if "anh_cccd" not in request.FILES or "bang_cap" not in request.FILES:
        return JsonResponse({"status": "missing_files"})

    cp = CarePartner.objects.create(
        user=request.user,
        chuyen_nganh=request.POST.get("chuyen_nganh", ""),
        truong=request.POST.get("truong", ""),
        ky_nang=request.POST.get("ky_nang", ""),
        anh_cccd=request.FILES["anh_cccd"],
        bang_cap=request.FILES["bang_cap"],
    )

    return JsonResponse({"status": "ok", "id": cp.id})


def api_danhsach_carepartner(request):
    cps = CarePartner.objects.filter(trang_thai="approved")

    data = []
    for cp in cps:
        data.append({
            "id": cp.id,
            "username": cp.user.username,
            "truong": cp.truong,
            "rating": cp.rating_trung_binh
        })

    return JsonResponse({"data": data})


# ======================================================
# PHẦN 3 — CHILD MANAGEMENT
# ======================================================

@csrf_exempt
def api_child_create(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "login_required"})

    if request.method != "POST":
        return JsonResponse({"status": "POST_required"})

    data = json.loads(request.body)

    child = Child.objects.create(
        parent=request.user,
        ten=data["ten"],
        ngay_sinh=data.get("ngay_sinh"),
        ghi_chu=data.get("ghi_chu", "")
    )

    return JsonResponse({"status": "ok", "id": child.id})


def api_child_list(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "login_required"})

    children = Child.objects.filter(parent=request.user)

    data = []
    for c in children:
        data.append({
            "id": c.id,
            "ten": c.ten,
            "ghi_chu": c.ghi_chu
        })

    return JsonResponse({"data": data})


@csrf_exempt
def api_child_delete(request, child_id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "login_required"})

    Child.objects.filter(id=child_id, parent=request.user).delete()
    return JsonResponse({"status": "deleted"})


# ======================================================
# PHẦN SERVICE
# ======================================================

def api_services(request):
    services = Service.objects.all()

    data = []
    for s in services:
        data.append({
            "id": s.id,
            "ten": s.ten,
            "mo_ta": s.mo_ta,
            "gia_moi_gio": s.gia_moi_gio,
        })

    return JsonResponse({"data": data})



# ======================================================
# PHẦN 4 — BOOKING
# ======================================================
@csrf_exempt
def api_booking_start(request, booking_id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "login_required"})

    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return JsonResponse({"status": "not_found"})

    # chỉ carepartner của job mới được start
    if not booking.carepartner or booking.carepartner.user != request.user:
        return JsonResponse({"status": "permission_denied"})

    if booking.trang_thai != "accepted":
        return JsonResponse({"status": "invalid_state"})

    booking.trang_thai = "doing"
    booking.save()

    return JsonResponse({"status": "started"})

@csrf_exempt
def api_booking_create(request):

    if not request.user.is_authenticated:
        return JsonResponse({"status":"error","msg":"login required"})

    try:
        data = json.loads(request.body)

        service = Service.objects.get(id=data["service_id"])

        start = datetime.fromisoformat(data["start"])
        end = datetime.fromisoformat(data["end"])

        booking = Booking.objects.create(
            parent=request.user,
            service=service,

            gio_bat_dau=start,
            gio_ket_thuc=end,

            dia_chi=data.get("dia_chi",""),
            tre_mo_ta=data.get("tre_mo_ta",""),
            yeu_cau=data.get("yeu_cau",""),

            gia_tam_tinh=data.get("gia_tam_tinh",0),

            status="pending"
        )

        return JsonResponse({"status":"ok"})

    except Exception as e:
        print("BOOKING ERROR:", e)
        return JsonResponse({"status":"error","msg":str(e)})

def api_booking_open(request):
    jobs = Booking.objects.filter(trang_thai="open")

    data = []
    for j in jobs:
        data.append({
            "id": j.id,
            "dia_chi": j.dia_chi,
            "mo_ta": j.mo_ta,
            "service": j.service.ten_dich_vu if j.service else ""
        })

    return JsonResponse({"data": data})


@csrf_exempt
@login_required
def api_booking_nhan(request):

    data = json.loads(request.body)

    booking = Booking.objects.get(id=data["booking_id"])

    # gán USER chứ không phải CarePartner object
    booking.carepartner = request.user
    booking.status = "applied"

    booking.save()

    return JsonResponse({"status":"ok"})






@csrf_exempt
def api_booking_done(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    booking.trang_thai = "done"
    booking.save()

    return JsonResponse({"status": "done"})


@csrf_exempt
def api_booking_cancel(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    booking.trang_thai = "cancel"
    booking.save()

    return JsonResponse({"status": "cancelled"})

@csrf_exempt
def api_booking_apply(request):

    if not request.user.is_authenticated:
        return JsonResponse({"status":"login_required"})

    data=json.loads(request.body)

    b=Booking.objects.get(id=data["booking_id"])

    b.carepartner=request.user
    b.status="applied"
    b.save()

    return JsonResponse({"status":"ok"})

@csrf_exempt
@login_required
def api_booking_confirm(request):
    data=json.loads(request.body)
    b=Booking.objects.get(id=data["booking_id"], parent=request.user)
    b.status="confirmed"
    b.save()
    return JsonResponse({"status":"ok"})


# ======================================================
# PHẦN 5 — REVIEW
# ======================================================

@csrf_exempt
def api_review_create(request, booking_id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "login_required"})

    data = json.loads(request.body)
    booking = Booking.objects.get(id=booking_id)

    # chỉ review job hoàn thành
    if booking.trang_thai != "done":
        return JsonResponse({"status": "job_not_done"})

    review = Review.objects.create(
        booking=booking,
        parent=request.user,
        carepartner=booking.carepartner,
        so_sao=data["so_sao"],
        nhan_xet=data.get("nhan_xet", "")
    )

    cp = booking.carepartner
    cp.tong_so_danh_gia += 1
    cp.tong_job_hoan_thanh += 1

    cp.rating_trung_binh = (
        (cp.rating_trung_binh * (cp.tong_so_danh_gia - 1)
         + data["so_sao"])
        / cp.tong_so_danh_gia
    )

    cp.save()

    return JsonResponse({"status": "review_saved"})



# ======================================================
# PHẦN 7 — CHATBOT AI
# ======================================================




#bổ xung
def dashboard(request):
    return render(request, "dashboard.html")

def api_jobs_priority(request):
    """
    API ưu tiên job cho CarePartner
    (version skeleton – demo)
    """

    if not request.user.is_authenticated:
        return JsonResponse({"status": "login_required"})

    try:
        cp = CarePartner.objects.get(user=request.user, trang_thai="approved")
    except CarePartner.DoesNotExist:
        return JsonResponse({"status": "not_carepartner"})

    # lấy các job chưa nhận
    jobs = Booking.objects.filter(
        trang_thai="open"
    ).order_by("-created_at")

    data = []
    for j in jobs:
        data.append({
            "id": j.id,
            "dia_chi": j.dia_chi,
            "thoi_gian": j.thoi_gian,
            "mo_ta": j.mo_ta,
        })

    return JsonResponse({
        "status": "ok",
        "jobs": data
    })

def trang_tai_khoan(request):
    if not request.user.is_authenticated:
        return redirect("/dangnhap/")
    return render(request, "account.html")

def trang_ho_so(request):
    if not request.user.is_authenticated:
        return redirect("/dangnhap/")
    return render(request, "profile.html")

#chuyển chế độ ph và carepartner
def api_get_mode(request):
    if not request.user.is_authenticated:
        return JsonResponse({"login": False})

    mode = request.session.get("mode", "parent")

    return JsonResponse({
        "login": True,
        "mode": mode
    })
@csrf_exempt
def api_switch_mode(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "login_required"})

    if request.method != "POST":
        return JsonResponse({"status": "POST_required"})

    try:
        data = json.loads(request.body)
        new_mode = data.get("mode")
    except:
        return JsonResponse({"status": "invalid_json"})

    if new_mode not in ["parent", "carepartner"]:
        return JsonResponse({"status": "invalid_mode"})

    # Nếu chuyển sang carepartner → kiểm tra duyệt
    if new_mode == "carepartner":
        try:
            cp = CarePartner.objects.get(user=request.user)
        except CarePartner.DoesNotExist:
            return JsonResponse({"status": "not_carepartner"})

        if cp.trang_thai != "approved":
            return JsonResponse({"status": "not_approved"})

    # OK → lưu session
    request.session["mode"] = new_mode

    return JsonResponse({
        "status": "ok",
        "mode": new_mode
    })


def api_jobs_open(request):

    if not request.user.is_authenticated:
        return JsonResponse({"status":"login_required"})

    jobs = Booking.objects.filter(
        status="pending",
        carepartner__isnull=True
    ).select_related("service","parent")

    data=[]

    for j in jobs:
        data.append({
            "id": j.id,
            "service": j.service.ten,
            "parent": j.parent.username,
            "mo_ta": j.tre_mo_ta,
            "yeu_cau": j.yeu_cau,
            "thoi_gian": f"{j.gio_bat_dau} - {j.gio_ket_thuc}",
            "gia": j.gia_tam_tinh
        })

    return JsonResponse({"data":data})







@csrf_exempt
def api_tinhgia(request):

    data = json.loads(request.body)

    try:
        service = Service.objects.get(id=data["service_id"])

        start = datetime.strptime(data["start"], "%Y-%m-%dT%H:%M")
        end   = datetime.strptime(data["end"], "%Y-%m-%dT%H:%M")

        hours = (end - start).total_seconds() / 3600

        if hours <= 0:
            return JsonResponse({"status":"error"})

        price = int(hours * service.gia_moi_gio)

        return JsonResponse({
            "status":"ok",
            "gia": price
        })

    except Exception as e:
        print("TINH GIA ERROR:", e)
        return JsonResponse({"status":"error"})


def api_my_bookings(request):

    if not request.user.is_authenticated:
        return JsonResponse({"status":"login_required"})

    bookings = Booking.objects.filter(
        parent=request.user
    ).select_related("service","carepartner")

    data=[]

    for b in bookings:
        data.append({
            "id": b.id,
            "service": b.service.ten,
            "time": f"{b.gio_bat_dau} - {b.gio_ket_thuc}",
            "gia": b.gia_tam_tinh,
            "status": b.status,
            "carepartner": b.carepartner.username if b.carepartner else None
        })

    return JsonResponse({"data":data})

@csrf_exempt
def api_parent_confirm(request):

    if not request.user.is_authenticated:
        return JsonResponse({"status":"login_required"})

    data=json.loads(request.body)

    b=Booking.objects.get(
        id=data["booking_id"],
        parent=request.user
    )

    if b.status!="applied":
        return JsonResponse({"status":"not_valid"})

    b.status="confirmed"
    b.save()

    return JsonResponse({"status":"ok"})

@login_required
def chat_page(request):
    return render(request, "chat.html")


@login_required
def api_booking_detail(request, booking_id):
    b = Booking.objects.get(id=booking_id)

    return JsonResponse({
        "id": b.id,
        "service": b.service.name,
        "start": b.start_time,
        "end": b.end_time,
        "address": b.address,
        "child_desc": b.child_desc,
        "extra_req": b.extra_req,
        "price": b.price,
        "status": b.status,
        "parent": b.parent.username,
        "carepartner": b.carepartner.username if b.carepartner else None,
    })
