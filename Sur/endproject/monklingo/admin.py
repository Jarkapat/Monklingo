from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ChatRoom, Message, Route, Checkpoint, Temple, CustomUser

# ✅ ลงทะเบียนโมเดลอื่นๆ
admin.site.register(ChatRoom)
admin.site.register(Message)
admin.site.register(Checkpoint)
admin.site.register(Temple)

# ✅ กำหนดการจัดการ CustomUser
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['id', 'username', 'email', 'is_staff', 'is_active']  # ✅ เพิ่ม username กลับมา
    search_fields = ['username', 'email']  # ✅ ค้นหา username และ email
    ordering = ['id']

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),  # ✅ เพิ่ม username
        ('Personal Info', {'fields': ('profile_picture', 'google_id', 'facebook_id')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff')}
        ),
    )

    def get_queryset(self, request):
        """ ✅ Staff เห็นเฉพาะตัวเอง / Admin เห็นทั้งหมด """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(id=request.user.id)

# ✅ ลงทะเบียน CustomUser ใน Django Admin
admin.site.register(CustomUser, CustomUserAdmin)

# ✅ จำกัดสิทธิ์ Route ให้ Staff จัดการเฉพาะของตัวเอง
class RouteAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        """ ✅ Staff เห็นเฉพาะ Route ของตัวเอง """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)

admin.site.register(Route, RouteAdmin)
