from django.db import models
from django.contrib.auth.models import User


# ===============================
# PROFILE PHỤ HUYNH
# ===============================
class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    so_dien_thoai = models.CharField(max_length=20, blank=True)
    dia_chi_mac_dinh = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return self.user.username


# ===============================
# CARE PARTNER
# ===============================
class CarePartner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    chuyen_nganh = models.CharField(max_length=200)
    truong = models.CharField(max_length=200)
    ky_nang = models.TextField()

    anh_cccd = models.ImageField(upload_to="cccd/")
    bang_cap = models.ImageField(upload_to="bangcap/")

    trang_thai = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Chờ duyệt"),
            ("approved", "Đã duyệt"),
            ("rejected", "Từ chối"),
        ],
        default="pending"
    )

    rating_trung_binh = models.FloatField(default=0)
    tong_so_danh_gia = models.IntegerField(default=0)
    tong_job_hoan_thanh = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


# ===============================
# QUẢN LÝ TRẺ EM
# ===============================
class Child(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE)

    ten = models.CharField(max_length=100)
    ngay_sinh = models.DateField(null=True, blank=True)
    ghi_chu = models.TextField(blank=True)

    def __str__(self):
        return self.ten


# ===============================
# 5 DỊCH VỤ CHÍNH
# ===============================
class Service(models.Model):
    ten = models.CharField(max_length=200)
    mo_ta = models.TextField(blank=True)

    # GIÁ THEO GIỜ
    gia_moi_gio = models.IntegerField(default=100000)

    def __str__(self):
        return f"{self.ten} - {self.gia_moi_gio}/giờ"


# ===============================
# BOOKING
# ===============================
class Booking(models.Model):

    STATUS_CHOICES = [
        ("pending","Pending"),
        ("applied","Applied"),
        ("confirmed","Confirmed"),
        ("done","Done"),
    ]

    parent = models.ForeignKey(User,on_delete=models.CASCADE,related_name="parent_bookings")
    carepartner = models.ForeignKey(User,null=True,blank=True,on_delete=models.SET_NULL)

    service = models.ForeignKey(Service,on_delete=models.CASCADE)
    dia_chi = models.CharField(max_length=255)

    gio_bat_dau = models.DateTimeField()
    gio_ket_thuc = models.DateTimeField()

    tre_mo_ta = models.TextField()
    yeu_cau = models.TextField(blank=True)

    gia_tam_tinh = models.IntegerField(default=0)

    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="pending")

    created_at = models.DateTimeField(auto_now_add=True)



# ===============================
# REVIEW
# ===============================
class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)

    parent = models.ForeignKey(User, on_delete=models.CASCADE)
    carepartner = models.ForeignKey(CarePartner, on_delete=models.CASCADE)

    so_sao = models.IntegerField()
    nhan_xet = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


# ===============================
# CHATBOT
# ===============================
class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)


class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    role = models.CharField(max_length=20)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
