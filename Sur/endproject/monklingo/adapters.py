from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login
from django.utils.text import slugify
import random

class MyAccountAdapter(DefaultAccountAdapter):
    """
    Custom Account Adapter สำหรับจัดการบัญชีผู้ใช้ทั่วไป
    """
    def get_login_redirect_url(self, request):
        """
        หลังจากล็อกอินสำเร็จ ให้เปลี่ยนเส้นทางไปยัง /routes/
        """
        return "/routes/"

    def respond_email_verification_sent(self, request, user):
        """
        ถ้าไม่ต้องการให้ผู้ใช้เห็นหน้า 'อีเมลถูกส่งแล้ว' ก็ Redirect ทันที
        """
        return redirect("/routes/")


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_app(self, request, provider, **kwargs):
        """
        ดึง SocialApp จากฐานข้อมูล
        """
        app = SocialApp.objects.filter(provider=provider).first()
        if not app:
            raise ObjectDoesNotExist(f"⚠️ ไม่มี SocialApp สำหรับ {provider}. โปรดเพิ่มใน Django Admin")
        return app

    def get_login_redirect_url(self, request):
        """
        ข้ามหน้า Continue Page และ Redirect ไปยัง /routes/
        """
        return "/routes/"


    def pre_social_login(self, request, sociallogin):
        """
        ตรวจสอบว่าผู้ใช้มี username หรือยัง ถ้ายังให้กำหนดอัตโนมัติ
        """
        user = sociallogin.user

        # ✅ ตรวจสอบว่ามี username หรือยัง
        if not user.username:
            base_username = slugify(user.email.split("@")[0])  # ใช้ email prefix เป็น username
            user.username = base_username

            # ✅ ตรวจสอบว่าซ้ำหรือไม่
            from django.contrib.auth import get_user_model
            User = get_user_model()
            counter = 1
            while User.objects.filter(username=user.username).exists():
                user.username = f"{base_username}{counter}"
                counter += 1

        # ✅ ตรวจสอบว่าผู้ใช้มี Primary Key หรือยัง
        if not user.pk:
            user.save()  # 🔹 บันทึก user ลงฐานข้อมูลก่อน

        user.backend = 'allauth.account.auth_backends.AuthenticationBackend'  # ✅ กำหนด Backend
        login(request, user, backend=user.backend)  # ✅ ล็อกอิน 

    def get_connect_redirect_url(self, request, socialaccount):
        """
        ✅ ข้าม Continue Page และ Redirect ไปยัง /routes/ หลังจากเชื่อมบัญชีสำเร็จ
        """
        return "/routes/"

   