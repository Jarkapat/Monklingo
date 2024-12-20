from django.shortcuts import render, get_object_or_404
from .models import AlmsgivingRoute , NewsPost , PrayersPost , UserImage
from django.views.generic import TemplateView
from django.contrib.auth import login, authenticate ,logout
from django.contrib import messages
from django.shortcuts import render, redirect
import logging
from monklingo.models import CustomUser
from urllib.parse import urlparse, parse_qs
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.core.files.base import ContentFile
import base64
from django.utils.timezone import now
from django.db.models import Count
from django.db.models.functions import TruncDate

@login_required
def route_list(request):
    # ดึงข้อมูลเส้นทางการเดินบิณฑบาตทั้งหมดจากฐานข้อมูล
    routes = AlmsgivingRoute.objects.all()
    return render(request, 'pages/route_list.html', {'routes': routes})


class HomeView(TemplateView):
    template_name = 'auth/home_page.html'
    
class LoginView(TemplateView):
    template_name = 'auth/login.html'

class RegisterView(TemplateView):
    template_name = 'auth/register.html'

class RankingView(TemplateView):
    template_name = 'pages/ranking.html'

class ChatView(TemplateView):
    template_name = 'pages/chat.html'

class PrayersView(TemplateView):
    template_name = 'pages/prayers.html'

class NewsView(TemplateView):
    template_name = 'pages/news.html'

class SettingView(TemplateView):
    template_name = 'pages/setting.html'

class UserView(TemplateView):
    template_name = 'pages/webuser.html'

class DashboardView(TemplateView):
    template_name = 'pages/dashboard.html'



logger = logging.getLogger(__name__)

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Debug: แสดงค่าที่รับจากฟอร์ม
        logger.debug(f"Received username: {username}")
        logger.debug(f"Received password1: {password1}")
        logger.debug(f"Received password2: {password2}")
        
        # ตรวจสอบว่ารหัสผ่านตรงกันหรือไม่
        if password1 != password2:
            logger.debug("Passwords do not match!")
            messages.error(request, 'รหัสผ่านไม่ตรงกัน')
            return redirect('register')  # กลับไปที่หน้า register
        
        try:
            # Debug: ลองสร้างผู้ใช้ใหม่
            logger.debug("Creating new CustomUser...")
            user = CustomUser.objects.create_user(username=username, password=password1)
            user.save()
            
            # Debug: ผู้ใช้ถูกสร้างแล้ว
            logger.debug(f"User created: {user}")
            
            messages.success(request, 'บัญชีผู้ใช้ถูกสร้างเรียบร้อยแล้ว!')
            return redirect('login')  # ไปที่หน้า login
        except Exception as e:
            # ถ้ามีข้อผิดพลาด ให้แสดงข้อผิดพลาด
            logger.error(f"Error occurred while creating user: {e}")
            messages.error(request, f'เกิดข้อผิดพลาด: {e}')
            return redirect('login')
    
    # ถ้าไม่ได้ส่งข้อมูลด้วย POST ก็ให้ render หน้า register
    return render(request, 'auth/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Debug: แสดงข้อมูลที่ผู้ใช้กรอก
        print(f"Username: {username}")
        print(f"Password: {password}")  # ระวังการแสดงรหัสผ่านใน log จริง

        user = authenticate(request, username=username, password=password)
        
        # Debug: ตรวจสอบผลลัพธ์จากการ authenticate
        if user is not None:
            print("User authenticated successfully")
            login(request, user)
            request.session[user.id] = user.id
            request.session['username'] = user.username
            request.session['is_authenticated'] = True
            messages.success(request, 'เข้าสู่ระบบสำเร็จ')
            print("Redirecting to route_list")
            return redirect('route_list')
        else:
            print("Authentication failed")
            messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
    
    return render(request, 'auth/login.html')

@login_required
def create_news_post(request):
    if request.method == "POST":
        # ดึงข้อมูลจาก POST และ FILES
        heading = request.POST.get("heading")
        content = request.POST.get("content")
        url = request.POST.get("url")
        img = request.FILES.get("img")
        post_type = request.POST.get("post_type")  # รับไฟล์ภาพ

        # ตรวจสอบข้อมูลที่จำเป็น
        if not heading or not content:
            print("ข้อมูลไม่ครบถ้วน")
            return JsonResponse({"error": "กรุณากรอกข้อมูลให้ครบถ้วน"}, status=400)

        # สร้าง Object โดยตรวจสอบว่ามีรูปภาพหรือไม่
        try:
            post = NewsPost.objects.create(
                heading=heading,
                content=content,
                url=url,
                post_type=post_type,
                author=request.user,
                img=img if img else None  # ตั้งค่า img เป็น None หากไม่มีการอัปโหลด
            )
            return JsonResponse({"message": "โพสต์สำเร็จ!", "redirect_url": reverse('news_list')}, status=201)
        except Exception as e:
            return JsonResponse({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@login_required
def logout_view(request):
    request.session.flush()
    logout(request)
    return redirect('home')


def get_embedded_url(url):
    # ตรวจสอบประเภทของลิงก์
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    # กรณี YouTube
    if "youtube.com" in domain or "youtu.be" in domain:
        video_id = None
        if domain == "youtu.be":
            video_id = parsed_url.path[1:]
        elif domain in ["www.youtube.com", "youtube.com"]:
            video_id = parse_qs(parsed_url.query).get("v", [None])[0]
        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"

    # กรณี Google Maps
    if "google.com" in domain and "maps" in parsed_url.path:
        return url  # Google Maps Embed URL ใช้ URL เดิมได้เลย

    # ลิงก์อื่นๆ
    return None  # ไม่รองรับการฝัง

@login_required
def news_list(request):
    news_posts = NewsPost.objects.order_by('-date_time')
    for post in news_posts:
        post.embedded_url = get_embedded_url(post.url)  # เพิ่ม URL สำหรับฝัง
    return render(request, 'pages/news.html', {'news_posts': news_posts})

@login_required
def edit_news(request, post_id):
    post = get_object_or_404(NewsPost, pk=post_id)

    if request.method == "POST":
        post.heading = request.POST.get("heading", post.heading)
        post.content = request.POST.get("content", post.content)
        post.url = request.POST.get("url", post.url)
        post_type = request.POST.get("post_type")

        valid_post_types = ['news', 'announcement', 'event']
        if post_type in valid_post_types:
            post.post_type = post_type

        if "img" in request.FILES:
            post.img = request.FILES["img"]

        post.save()
        messages.error(request, 'รหัสผ่านไม่ตรงกัน')
        return redirect('news_list')
        
    return render(request, "element/edit_news.html", {"post": post})
    
@login_required
def delete_news(request, post_id):
    post = get_object_or_404(NewsPost, pk=post_id)
    post.delete()
    return JsonResponse({"message": "ลบโพสต์สำเร็จ!"})






@login_required
def create_prayers_post(request):
    if request.method == "POST":
        # ดึงข้อมูลจาก POST และ FILES
        heading = request.POST.get("heading")
        content = request.POST.get("content")
        url = request.POST.get("url")

        # ตรวจสอบข้อมูลที่จำเป็น
        if not heading or not content:
            print("ข้อมูลไม่ครบถ้วน")
            return JsonResponse({"error": "กรุณากรอกข้อมูลให้ครบถ้วน"}, status=400)

        # สร้าง Object โดยตรวจสอบว่ามีรูปภาพหรือไม่
        try:
            post = PrayersPost.objects.create(
                heading=heading,
                content=content,
                url=url,
                author=request.user,
            )
            return JsonResponse({"message": "โพสต์สำเร็จ!", "redirect_url": reverse('prayers_list')}, status=201)
        except Exception as e:
            return JsonResponse({"error": f"เกิดข้อผิดพลาด: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def get_embedded_url_prayers(url):
    # ตรวจสอบว่ามี URL หรือไม่
    if not url:
        return None

    # แยกส่วนของ URL
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    # กรณี YouTube
    if "youtube.com" in domain or "youtu.be" in domain:
        video_id = None
        if domain == "youtu.be":
            video_id = parsed_url.path[1:]
        elif "youtube.com" in domain:
            video_id = parse_qs(parsed_url.query).get("v", [None])[0]
        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
        
    # กรณี Google Maps
    if "google.com" in domain and "maps" in parsed_url.path:
        if "/embed" in parsed_url.path:
            return url  # เป็น Embed URL อยู่แล้ว
        else:
            return None  # ไม่รองรับลิงก์อื่นนอกจาก Embed URL

    # ลิงก์อื่นๆ
    return None

@login_required
def prayers_list(request):
    prayers_posts = PrayersPost.objects.order_by('-date_time')
    for post in prayers_posts:
        post.embedded_url_prayers = get_embedded_url_prayers(post.url)
    return render(request, 'pages/prayers.html', {'prayers_posts': prayers_posts})

@login_required
def edit_prayers(request, post_id):
    post = get_object_or_404(PrayersPost, pk=post_id)

    if request.method == "POST":
        post.heading = request.POST.get("heading", post.heading)
        post.content = request.POST.get("content", post.content)
        post.url = request.POST.get("url", post.url)


        post.save()
        messages.error(request, 'รหัสผ่านไม่ตรงกัน')
        return redirect('prayers_list')
        
    return render(request, "element/edit_prayers.html", {"post": post})
    
@login_required
def delete_prayers(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(PrayersPost, pk=post_id)
        post.delete()
    return JsonResponse({"message": "ลบโพสต์สำเร็จ!"})


@login_required
def edit_profile(request):
    user = request.user

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        profile_picture = request.FILES.get("profile_picture")

        # แก้ไขข้อมูลโปรไฟล์
        if username:
            user.username = username
        if email:
            user.email = email
        if profile_picture:
            user.profile_picture = profile_picture
            messages.success(request, "อัปโหลดรูปภาพสำเร็จ")

        # ตรวจสอบรหัสผ่าน
        if current_password or new_password:
            if not current_password or not new_password:
                messages.error(request, "กรุณากรอกทั้งรหัสผ่านปัจจุบันและรหัสผ่านใหม่")
            elif user.check_password(current_password):
                user.set_password(new_password)
                messages.success(request, "เปลี่ยนรหัสผ่านสำเร็จ กรุณาล็อกอินใหม่")
                user.save()
                return redirect('login')
            else:
                messages.error(request, "รหัสผ่านปัจจุบันไม่ถูกต้อง")
        else:
            user.save()
            messages.success(request, "แก้ไขข้อมูลสำเร็จ")
            return redirect('setting')

    return render(request, 'pages/setting.html', {'user': user})

# ใช้ get_user_model() เพื่อดึงโมเดล CustomUser
CustomUser = get_user_model()

def UserView(request):
    # ดึงข้อมูลทั้งหมดของผู้ใช้
    users = CustomUser.objects.all()

    # สร้างลิสต์เพื่อเก็บข้อมูลผู้ใช้พร้อมกับจำนวนรูปภาพ
    users_with_image_count = []
    for user in users:
        # คำนวณจำนวนรูปภาพที่ผู้ใช้แต่ละคนมี
        image_count = UserImage.objects.filter(user=user).count()  # นับจำนวน UserImage ที่เชื่อมโยงกับผู้ใช้
        
        # เก็บข้อมูลในลิสต์
        users_with_image_count.append({
            'user': user,
            'image_count': image_count,
        })

    # เรียงลำดับผู้ใช้จากจำนวนรูปภาพมากไปน้อย
    users_with_image_count.sort(key=lambda x: x['image_count'], reverse=True)

    # ส่งข้อมูลไปยังเทมเพลต
    return render(request, 'pages/webuser.html', {'users_with_image_count': users_with_image_count})


@login_required
def delete_user(request, user_id):
    # ตรวจสอบว่า user_id เป็นผู้ใช้ที่มีอยู่ในฐานข้อมูลหรือไม่
    user = get_object_or_404(CustomUser, id=user_id)
    
    # ตรวจสอบว่าเป็นผู้ดูแลระบบหรือไม่
    if request.user.is_superuser:
        user.delete()  # ลบผู้ใช้
        return JsonResponse({"message": "ผู้ใช้ถูกลบสำเร็จ!"})
    else:
        return JsonResponse({"error": "คุณไม่มีสิทธิ์ในการลบผู้ใช้นี้!"}, status=403)
    
@login_required
def upload_image(request):
    if request.method == 'POST':
        # ตรวจสอบว่าอัพโหลดวันนี้แล้วหรือยัง
        if UserImage.objects.filter(user=request.user, uploaded_at__date=now().date()).exists():
            return JsonResponse({
                "status": "error",
                "message": "คุณสามารถอัพโหลดรูปได้เพียงวันละครั้ง"
            }, status=400)

        # ดำเนินการอัพโหลดรูปภาพ
        image_data = request.POST.get('image')
        if not image_data or ';base64,' not in image_data:
            return JsonResponse({"status": "error", "message": "ข้อมูลรูปภาพไม่ถูกต้อง"}, status=400)

        try:
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_file = ContentFile(base64.b64decode(imgstr), name=f"user_image.{ext}")
            UserImage.objects.create(user=request.user, image=image_file, uploaded_at=now())

            return JsonResponse({"status": "success", "message": "อัพโหลดรูปภาพสำเร็จ!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"เกิดข้อผิดพลาด: {str(e)}"}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

@login_required
def dashboard(request):
    today = now().date()
    users_today = CustomUser.objects.filter(last_login__date=today).count()
    photos_today = UserImage.objects.filter(uploaded_at__date=today).count()
    
    # สรุปจำนวนรูปภาพ
    photo_summary = (
        UserImage.objects.filter(uploaded_at__month=today.month)
        .annotate(uploaded_date=TruncDate('uploaded_at'))
        .values('uploaded_date')
        .annotate(total_photos=Count('id'))
        .order_by('uploaded_date')
    )
    print(list(photo_summary))  # Debug: แสดงข้อมูล photo_summary ใน console/log

    user_images = UserImage.objects.select_related('user').all()

    context = {
        'users_today': users_today,
        'photos_today': photos_today,
        'photo_summary': list(photo_summary),  # ส่งเป็น list
        'user_images': user_images,
    }
    return render(request, 'pages/dashboard.html', context)