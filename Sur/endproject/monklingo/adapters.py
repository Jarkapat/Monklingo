from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login
from django.utils.text import slugify
import random
from django.contrib.auth import get_user_model
from django.db import IntegrityError


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
        ตรวจสอบว่าผู้ใช้มีบัญชีอยู่แล้วหรือไม่ก่อนสร้างใหม่
        """
        user = sociallogin.user
        User = get_user_model()

        # ✅ ตรวจสอบว่าผู้ใช้ล็อกอินด้วยอีเมล และมีอีเมลใน social login หรือไม่
        if not user.email:
            return  # ❌ ไม่มีอีเมล ไม่สามารถตรวจสอบได้

        try:
            # ✅ ค้นหาผู้ใช้ที่มี email นี้ในระบบ
            existing_user = User.objects.get(email=user.email)
            
            # ✅ เชื่อมโยงบัญชี Social กับบัญชีเดิม
            sociallogin.connect(request, existing_user)
            
            # ✅ กำหนดให้ล็อกอินเป็นบัญชีเดิม
            user.backend = 'allauth.account.auth_backends.AuthenticationBackend'
            login(request, existing_user, backend=user.backend)
            return
        
        except User.DoesNotExist:
            pass  # ✅ ถ้ายังไม่มีบัญชี ก็ให้ดำเนินการสมัครปกติ
        
        # ✅ ถ้ายังไม่มี username ให้สร้างใหม่อัตโนมัติ
        if not user.username:
            base_username = slugify(user.email.split("@")[0])  # ใช้ email prefix เป็น username
            user.username = base_username

            # ✅ ตรวจสอบ username ซ้ำ
            counter = 1
            while User.objects.filter(username=user.username).exists():
                user.username = f"{base_username}{counter}"
                counter += 1

        # ✅ บันทึกผู้ใช้ใหม่
        if not user.pk:
            try:
                user.save()
            except IntegrityError:
                pass  # ป้องกันข้อผิดพลาดหากบันทึกซ้ำ

        # ✅ กำหนด Backend และล็อกอิน
        user.backend = 'allauth.account.auth_backends.AuthenticationBackend'
        login(request, user, backend=user.backend)


    def get_connect_redirect_url(self, request, socialaccount):
        """
        ✅ ข้าม Continue Page และ Redirect ไปยัง /routes/ หลังจากเชื่อมบัญชีสำเร็จ
        """
        return "/routes/"

   