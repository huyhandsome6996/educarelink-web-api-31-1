from django.contrib import admin
from .models import (
    CarePartner,
    Booking,
    ParentProfile,
    Child,
    Service,
    Review,
    ChatSession,
    ChatMessage
)

# =========================
# PARENT PROFILE
# =========================
@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "so_dien_thoai", "dia_chi_mac_dinh")
    search_fields = ("user__username", "so_dien_thoai")


# =========================
# CHILD
# =========================
@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ("ten", "parent", "ngay_sinh")
    search_fields = ("ten", "parent__username")
    list_filter = ("ngay_sinh",)


# =========================
# SERVICE
# =========================
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("id","ten","gia_moi_gio")
    search_fields = ("ten",)


# =========================
# CARE PARTNER
# =========================
@admin.register(CarePartner)
class CarePartnerAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "truong",
        "chuyen_nganh",
        "trang_thai",
        "rating_trung_binh",
        "tong_job_hoan_thanh"
    )

    list_filter = ("trang_thai",)

    search_fields = (
        "user__username",
        "truong",
        "chuyen_nganh"
    )

    actions = ["duyet", "tuchoi"]

    def duyet(self, request, queryset):
        queryset.update(trang_thai="approved")
    duyet.short_description = "✅ Duyệt hồ sơ"

    def tuchoi(self, request, queryset):
        queryset.update(trang_thai="rejected")
    tuchoi.short_description = "❌ Từ chối hồ sơ"


# =========================
# BOOKING
# =========================
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "parent",
        "carepartner",
        "service",
        "gio_bat_dau",
        "gio_ket_thuc",
        "gia_tam_tinh",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "service",
    )

    search_fields = (
        "parent__username",
        "carepartner__username",
    )


# =========================
# REVIEW
# =========================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "booking",
        "parent",
        "carepartner",
        "so_sao",
        "created_at"
    )

    list_filter = ("so_sao",)


# =========================
# CHATBOT
# =========================
@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "started_at")


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("session", "role", "created_at")
