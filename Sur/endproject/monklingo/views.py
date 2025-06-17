from django.shortcuts import render, get_object_or_404
from .models import  NewsPost , PrayersPost , UserImage ,ChatRoom , Message,Route, Checkpoint, Temple ,Event
from django.views.generic import TemplateView
from django.contrib.auth import login, authenticate ,logout
from django.contrib import messages
from django.shortcuts import render, redirect
import logging
from monklingo.models import CustomUser
from urllib.parse import urlparse, parse_qs
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.core.files.base import ContentFile
import base64
from django.utils.timezone import now ,localtime
from django.db.models import Value, Count , F, Func, IntegerField , CharField 
from django.db.models.functions import TruncDate, ExtractHour,TruncMinute,ExtractMinute
from datetime import date,datetime,timedelta
import plotly.graph_objects as go
from plotly.graph_objs import Scatter, Figure
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import math
from django.core.serializers import serialize
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.utils.http import urlencode
from django.http import HttpResponse
import re
import calendar
from django.db.models.functions import  Concat , Cast
from django.utils.dateparse import parse_date

logger = logging.getLogger(__name__)

class HomeView(TemplateView):
    template_name = 'auth/home_page.html'

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()
        email = request.POST.get('email', '').strip() or ""

        # Debug: แสดงค่าที่รับจากฟอร์ม
        logger.debug(f"Received username: {username}, email: {email}")

        # ✅ ตรวจสอบว่าชื่อผู้ใช้ไม่ซ้ำ
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'ชื่อผู้ใช้นี้ถูกใช้ไปแล้ว')
            return redirect('register')

        # ✅ ตรวจสอบความยาวของชื่อผู้ใช้
        if len(username) < 4:
            messages.error(request, 'ชื่อผู้ใช้ต้องมีอย่างน้อย 4 ตัวอักษร')
            return redirect('register')

        # ✅ ตรวจสอบรูปแบบของรหัสผ่าน
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password1):
            messages.error(request, 'รหัสผ่านต้องมีอย่างน้อย 8 ตัว และประกอบด้วยตัวอักษร, และ ตัวเลข')
            return redirect('register')

        # ✅ ตรวจสอบว่ารหัสผ่านตรงกัน
        if password1 != password2:
            messages.error(request, 'รหัสผ่านไม่ตรงกัน')
            return redirect('register')

        try:
            # ✅ สร้างบัญชีผู้ใช้
            user = CustomUser.objects.create_user(username=username, email=email, password=password1)
            user.save()

            messages.success(request, '✅ บัญชีถูกสร้างเรียบร้อย! กรุณาเข้าสู่ระบบ')
            return redirect('login')

        except Exception as e:
            logger.error(f"Error creating user: {e}")
            messages.error(request, f'เกิดข้อผิดพลาด: {e}')
            return redirect('register')

    return render(request, 'auth/register.html')


@csrf_exempt
def login_view(request):
    context = {'timestamp': int(datetime.now().timestamp())}

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Debug: ตรวจสอบข้อมูลที่รับมา
        logger.debug(f"Login attempt for username: {username}")

        # ✅ ตรวจสอบว่าใส่ข้อมูลครบหรือไม่
        if not username or not password:
            messages.error(request, 'กรุณากรอกชื่อผู้ใช้และรหัสผ่าน')
            return render(request, 'auth/login.html', context)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            logger.debug("User authenticated successfully")
            login(request, user)
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['is_authenticated'] = True
            messages.success(request, 'เข้าสู่ระบบสำเร็จ')
            return redirect('route_list')
        else:
            logger.debug("Authentication failed")
            messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')

    return render(request, 'auth/login.html', context)

@login_required
def create_news_post(request):
    if request.method == "POST":
        # ดึงข้อมูลจาก POST และ FILES
        heading = request.POST.get("heading")
        content = request.POST.get("content")
        url = request.POST.get("url")
        img = request.FILES.get("img")
        post_type = request.POST.get("post_type")  # รับไฟล์ภาพ
        age = request.POST.get("age")
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
                age=age,
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
        post.embedded_url = get_embedded_url(post.url)
    ranking = (
        CustomUser.objects.annotate(total_photos=Count('user_images'))
        .filter(total_photos__gt=0)  # กรองเฉพาะผู้ใช้ที่มีรูป
        .order_by('-total_photos')  # เรียงจากมากไปน้อย
    )
    user_rank = next((i + 1 for i, user in enumerate(ranking) if user == request.user), None)
    user_photos = UserImage.objects.filter(user=request.user).count()
    context = {
        'news_posts': news_posts,
        'user_rank': user_rank,
        'user_photos': user_photos,
        'ranking': ranking,
    }

    return render(request, 'pages/news.html', context)

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
            return JsonResponse({"message": "✅โพสต์สำเร็จ!", "redirect_url": reverse('prayers_list')}, status=201)
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
        ranking = (
        CustomUser.objects.annotate(total_photos=Count('user_images'))
        .filter(total_photos__gt=0)  # กรองเฉพาะผู้ใช้ที่มีรูป
        .order_by('-total_photos')  # เรียงจากมากไปน้อย
    )
    user_rank = next((i + 1 for i, user in enumerate(ranking) if user == request.user), None)
    user_photos = UserImage.objects.filter(user=request.user).count()
    latest_news = NewsPost.objects.order_by('-date_time').first()
    context = {
        'prayers_posts': prayers_posts,
        'user_rank': user_rank,
        'user_photos': user_photos,
        'ranking': ranking,
        'latest_news': latest_news
    }
    return render(request, 'pages/prayers.html', context)

@login_required
def edit_prayers(request, post_id):
    post = get_object_or_404(PrayersPost, pk=post_id)

    if request.method == "POST":
        post.heading = request.POST.get("heading", post.heading)
        post.content = request.POST.get("content", post.content)
        post.url = request.POST.get("url", post.url)


        post.save()
        messages.success(request, '✅แก้ไขโพสต์สำเร็จ')
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
        confirm_new_password = request.POST.get("confirm_new_password")
        profile_picture = request.FILES.get("profile_picture")

        # แก้ไขข้อมูลโปรไฟล์
        if username:
            user.username = username
        if email:
            user.email = email
        if profile_picture:
            user.profile_picture = profile_picture
            messages.success(request, "อัปโหลดรูปภาพสำเร็จ")

        # ตรวจสอบการเปลี่ยนรหัสผ่าน
        if current_password or new_password or confirm_new_password:
            if not current_password or not new_password or not confirm_new_password:
                messages.error(request, "กรุณากรอกข้อมูลให้ครบทุกช่อง")
            elif new_password != confirm_new_password:
                messages.error(request, "รหัสผ่านใหม่และยืนยันรหัสผ่านไม่ตรงกัน")
            elif not user.check_password(current_password):
                messages.error(request, "รหัสผ่านปัจจุบันไม่ถูกต้อง")
            elif not is_valid_password(new_password):
                messages.error(request, "รหัสผ่านต้องมีอย่างน้อย 8 ตัว, ตัวเลข, ตัวพิมพ์ใหญ่, และอักขระพิเศษ")
            else:
                user.set_password(new_password)
                user.save()
                messages.success(request, "✅เปลี่ยนรหัสผ่านสำเร็จ กรุณาล็อกอินใหม่")
                return redirect('login')  # บังคับล็อกอินใหม่

        # บันทึกการเปลี่ยนแปลงทั่วไป
        else:
            user.save()
            messages.success(request, "✅แก้ไขข้อมูลสำเร็จ")
            return redirect('setting')

    return render(request, 'pages/setting.html', {'user': user})


def is_valid_password(password):
    """ ตรวจสอบว่ารหัสผ่านตรงตามข้อกำหนด """
    return (
        len(password) >= 8
        and re.search(r"\d", password)   # ต้องมีตัวเลข
        and re.search(r"[A-Z]", password)  # ต้องมีตัวพิมพ์ใหญ่
    )


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
        now_time = localtime(now())  # แปลงเป็นเวลาท้องถิ่น
        today = now_time.date()
        start_time = now_time.replace(hour=5, minute=0, second=0, microsecond=0)  # 05:00 น.
        end_time = now_time.replace(hour=8, minute=0, second=0, microsecond=0)  # 08:00 น.

        # ตรวจสอบว่าผู้ใช้อัปโหลดรูปแล้ววันนี้หรือยัง
        if UserImage.objects.filter(user=request.user, uploaded_at__date=today).exists():
            messages.error(request, "คุณสามารถอัปโหลดรูปได้เพียงวันละครั้ง")
            return redirect('/routes/')

        # ✅ ตรวจสอบช่วงเวลา
        if not (start_time <= now_time <= end_time):
            messages.error(request, "คุณสามารถอัปโหลดรูปได้เฉพาะช่วงเวลา 05.00 - 08.00 น.")
            return redirect('/routes/')

        # ตรวจสอบข้อมูลรูปภาพ
        image_data = request.POST.get('image')
        if not image_data or ';base64,' not in image_data:
            messages.error(request, "ข้อมูลรูปภาพไม่ถูกต้อง")
            return redirect('/routes/')

        try:
            # แปลงข้อมูลรูปเป็นไฟล์
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_file = ContentFile(base64.b64decode(imgstr), name=f"user_{request.user.id}.{ext}")

            # บันทึกข้อมูลลงโมเดล UserImage
            UserImage.objects.create(user=request.user, image=image_file, uploaded_at=now())

            messages.success(request, "อัปโหลดรูปภาพสำเร็จ!")
            return redirect('/routes/')
        except Exception as e:
            messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
            return redirect('/routes/')

    messages.error(request, "Invalid request method")
    return redirect('/routes/')


@login_required
def dashboard(request):
    today = date.today()
    selected_month = int(request.GET.get('month', today.month))
    selected_date = request.GET.get('date', today.strftime('%Y-%m-%d'))  # ค่าเริ่มต้นเป็นวันนี้
    selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

    thai_months = [
        "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
        "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]
    months = [{'value': i+1, 'name': thai_months[i]} for i in range(12)]

    users_today = CustomUser.objects.filter(last_login__date=today).count()
    photos_today = UserImage.objects.filter(uploaded_at__date=today).count()
    user_images = UserImage.objects.select_related('user').order_by('-uploaded_at')
    user_images = UserImage.objects.filter(uploaded_at__date=selected_date)

    first_day = date(today.year, selected_month, 1)
    last_day = date(today.year, selected_month, calendar.monthrange(today.year, selected_month)[1])
    date_range = [first_day + timedelta(days=i) for i in range((last_day - first_day).days + 1)]
    date_mapping = {d.strftime('%d-%m-%Y'): 0 for d in date_range}

    available_dates = (
        UserImage.objects
        .annotate(upload_date=TruncDate('uploaded_at'))
        .values_list('upload_date', flat=True)
        .distinct()
        .order_by('-upload_date')
    )

    photo_summary_data = (
        UserImage.objects.filter(uploaded_at__month=selected_month)
        .annotate(uploaded_date=TruncDate('uploaded_at'))
        .values('uploaded_date')
        .annotate(total_photos=Count('id'))
        .order_by('uploaded_date')
    )

    for entry in photo_summary_data:
        date_mapping[entry['uploaded_date'].strftime('%d-%m-%Y')] = entry['total_photos']

    photo_summary = [
        {'uploaded_date': datetime.strptime(k, "%d-%m-%Y").strftime('%d'), 'total_photos': v}
        for k, v in date_mapping.items()
    ]

    ranked_users = (
        CustomUser.objects.annotate(photo_count=Count('user_images'))
        .filter(photo_count__gt=0)
        .order_by('-photo_count')
    )

    top_ranked_users = [
        {
            'username': user.username,
            'profile_picture': user.profile_picture.url if user.profile_picture else None,
            'rank': idx + 1,
            'photo_count': user.photo_count
        }
        for idx, user in enumerate(ranked_users[:5])
    ]

    # ✅ ผู้ใช้ที่ได้อันดับ 1
    top_user = top_ranked_users[0] if top_ranked_users else None
    total_competitors = max(0, ranked_users.count() - 1)

    labels = [entry['uploaded_date'] for entry in sorted(photo_summary, key=lambda x: x['uploaded_date'])]
    data = [entry['total_photos'] for entry in sorted(photo_summary, key=lambda x: x['uploaded_date'])]

    if not labels:
        labels = ["ไม่มีข้อมูล"]
        data = [0]

    graph = Figure()
    graph.add_trace(Scatter(x=labels, y=data, mode='lines+markers', name='Photos', marker=dict(size=8, color='blue')))
    graph.update_layout(
        title="จำนวนรูปภาพที่อัปโหลดในแต่ละวัน (รายเดือน)",
        xaxis=dict(title="วันที่", type="category", tickangle=-45, showgrid=True, zeroline=False),
        yaxis=dict(title="จำนวนรูป", rangemode="tozero", tickmode="linear", dtick=1, tickformat=".0f"),
        template="plotly_white",
        margin=dict(l=50, r=50, t=50, b=100)
    )
    graph_html = graph.to_html(full_html=False)

    users_total = CustomUser.objects.count()
    users_registered_today = CustomUser.objects.filter(date_joined__date=today).count()
    photos_total = UserImage.objects.count()
    total_prayers = PrayersPost.objects.count()
    BIN_SIZE = 60  # ✅ ปรับ bin เป็น 30 นาที
    class LPAD(Func):
        function = 'LPAD'
        arity = 3  # รับ 3 ค่า (ค่าที่ต้องการเติม, ความยาว, อักขระที่ใช้เติม)
        output_field = CharField()
    # ✅ ใช้ Floor() เพื่อลดค่านาทีให้เป็น bin-size ที่ถูกต้อง
    class Floor(Func):
        function = 'FLOOR'
        output_field = IntegerField()

    histogram_data = (
        UserImage.objects.filter(uploaded_at__month=selected_month)
        .annotate(
            minute_group=Floor(ExtractMinute('uploaded_at') / BIN_SIZE) * BIN_SIZE
        )
        .annotate(
            grouped_time=Concat(
                ExtractHour('uploaded_at'),
                Value(':'),
                LPAD(Cast('minute_group', CharField()), 2, Value('0')),
                output_field=CharField()
            )
        )
        .values('grouped_time')
        .annotate(total_photos=Count('id'))
        .order_by('grouped_time')
    )

    histogram_summary = [
        {'uploaded_time': entry['grouped_time'], 'total_photos': entry['total_photos']}
        for entry in histogram_data
    ]


    context = {
        'users_today': users_today,
        'photos_today': photos_today,
        'user_images': user_images,
        'photo_summary': json.dumps(photo_summary, cls=DjangoJSONEncoder),
        'graph_html': graph_html,
        'months': months,
        'selected_month': selected_month,
        'users_total': users_total,
        'users_registered_today': users_registered_today,
        'photos_total': photos_total,
        'total_prayers': total_prayers,
        'top_ranked_users': top_ranked_users,
        'top_user': top_user,
        'total_competitors': total_competitors,
        'histogram_summary': json.dumps(histogram_summary, cls=DjangoJSONEncoder),
        'available_dates': available_dates,
        'selected_date': selected_date.strftime('%Y-%m-%d'),
    }

    return render(request, 'pages/dashboard.html', context)


@login_required
def chat_list(request):
    # ดึงรายการห้องแชททั้งหมด
    chatrooms = ChatRoom.objects.all()

    # สร้าง Ranking ของผู้ใช้
    ranking = (
        CustomUser.objects.annotate(total_photos=Count('user_images'))
        .filter(total_photos__gt=0)  # กรองเฉพาะผู้ใช้ที่มีรูป
        .order_by('-total_photos')  # เรียงจากมากไปน้อย
    )

    # หาอันดับของผู้ใช้ปัจจุบัน
    user_rank = next((i + 1 for i, user in enumerate(ranking) if user == request.user), None)
    
    # นับจำนวนรูปของผู้ใช้
    user_photos = UserImage.objects.filter(user=request.user).count()

    # ดึงข่าวล่าสุด
    latest_news = NewsPost.objects.order_by('-date_time').first()

    # สร้าง context ที่รวมข้อมูลทั้งหมด
    context = {
        'chatrooms': chatrooms,
        'user_rank': user_rank,
        'latest_news': latest_news,
        'user_photos': user_photos,
        'ranking': ranking,
    }

    return render(request, 'pages/chat_list.html', context)

@login_required
def chat_room(request, room_id):
    # ดึงข้อมูลห้องแชทที่เลือก
    chatroom = get_object_or_404(ChatRoom, id=room_id)
    messages = chatroom.messages.order_by('timestamp')

    if request.method == 'POST':
        content = request.POST.get('content', '')
        image = request.FILES.get('image')
        file = request.FILES.get('file')

        # สร้างข้อความใหม่
        new_message = Message.objects.create(
            chatroom=chatroom,
            sender=request.user,
            content=content,
            image=image,
            file=file,
        )

        # ส่งข้อมูลกลับเป็น JSON
        return JsonResponse({
            'sender': new_message.sender.username,
            'content': new_message.content,
            "timestamp": localtime(new_message.timestamp).strftime("%d/%m/%Y %H:%M"),
            'image': new_message.image.url if new_message.image else None,
            'file': new_message.file.url if new_message.file else None,
        })

    # คำนวณ Ranking ของผู้ใช้
    ranking = (
        CustomUser.objects.annotate(total_photos=Count('user_images'))
        .filter(total_photos__gt=0)  # กรองเฉพาะผู้ใช้ที่มีรูป
        .order_by('-total_photos')  # เรียงจากมากไปน้อย
    )

    # หาอันดับของผู้ใช้ปัจจุบัน
    user_rank = next((i + 1 for i, user in enumerate(ranking) if user == request.user), None)
    
    # นับจำนวนรูปของผู้ใช้
    user_photos = UserImage.objects.filter(user=request.user).count()

    # ดึงข่าวล่าสุด
    latest_news = NewsPost.objects.order_by('-date_time').first()

    # สร้าง context ที่รวมข้อมูลทั้งหมด
    context = {
        'chatroom': chatroom,
        'messages': messages,
        'user_rank': user_rank,
        'latest_news': latest_news,
        'user_photos': user_photos,
        'ranking': ranking,
    }

    return render(request, 'pages/chat_room.html', context)



@login_required
def chat_room_create(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST.get('description', '')
        ChatRoom.objects.create(name=name, description=description)
        return redirect('chat_list')
    return render(request, 'element/chat_edit.html')


@login_required
def chat_room_update(request, room_id):
    chatroom = get_object_or_404(ChatRoom, id=room_id)
    if request.method == 'POST':
        chatroom.name = request.POST['name']
        chatroom.description = request.POST.get('description', '')
        chatroom.save()
        return redirect('chat_list')
    return render(request, 'element/chat_edit.html', {'chatroom': chatroom})


@login_required
def chat_room_delete(request, room_id):
    chatroom = get_object_or_404(ChatRoom, id=room_id)
    if request.method == "POST":
        chatroom.delete()
        return JsonResponse({"success": True}, status=200)

    if request.method == "GET":
        # เพิ่มการแจ้งเตือนเมื่อเข้าผ่าน GET
        return JsonResponse({"error": "This endpoint only accepts POST requests."}, status=405)

    return JsonResponse({"error": "Invalid request method"}, status=400)



@login_required
def chat_room_messages(request, room_id):
    chatroom = get_object_or_404(ChatRoom, id=room_id)
    messages = chatroom.messages.order_by('timestamp')
    messages_data = [
        {
            'sender': message.sender.username,
            'content': message.content,
            'timestamp': localtime(message.timestamp).strftime('%d/%m/%Y %H:%M'),
            'image': message.image.url if message.image else None,
            'file': message.file.url if message.file else None,
        }
        for message in messages
    ]
    return JsonResponse(messages_data, safe=False)

def is_facebook_bot(request):
    """ ตรวจสอบว่า request มาจาก Facebook Bot หรือไม่ """
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    return "facebookexternalhit" in user_agent or "facebot" in user_agent


def ranking_view(request):
    """ แสดงหน้า Ranking และให้ Facebook Scraper ดึงข้อมูลของผู้ใช้ที่ถูกแชร์ """
    is_facebook = is_facebook_bot(request)
    ranking = (
        CustomUser.objects.annotate(total_photos=Count('user_images'))
        .filter(total_photos__gt=0)
        .order_by('-total_photos')
    )
    # ดึงข้อมูลผู้ใช้จากการแชร์หรือจากการล็อกอิน
    user_id = request.GET.get("user_id")
    user = None
    user_rank = "N/A"
    profile_picture = "https://3aa4-49-229-22-70.ngrok-free.app/static/images/monk.png"

    # ถ้ามี user_id ใน URL
    if user_id:
        try:
            user = CustomUser.objects.get(id=user_id)
            user_rank = next((i + 1 for i, u in enumerate(ranking) if u == user), "N/A")
            profile_picture = user.profile_picture.url if user.profile_picture else profile_picture
        except CustomUser.DoesNotExist:
            pass

    # ถ้าไม่มี user_id ใน URL และผู้ใช้ล็อกอิน
    elif request.user.is_authenticated:
        user = request.user
        user_rank = next((i + 1 for i, u in enumerate(ranking) if u == request.user), "N/A")
        profile_picture = request.user.profile_picture.url if request.user.profile_picture else profile_picture

    latest_news = NewsPost.objects.order_by('-date_time').first()
    user_photos = UserImage.objects.filter(user=request.user).count() if request.user.is_authenticated else 0

    context = {
        'ranking': ranking,
        'user_rank': user_rank,
        'profile_picture': profile_picture,
        'shared_user_id': user.id if user else "",
        'latest_news': latest_news,
        'user_photos': user_photos,
    }

    return render(request, 'pages/ranking.html', context)



@login_required
def route_list(request):
    ranking = (
        CustomUser.objects.annotate(total_photos=Count('user_images'))
        .filter(total_photos__gt=0)  # กรองเฉพาะผู้ใช้ที่มีรูป
        .order_by('-total_photos')  # เรียงจากรูปมากไปน้อย
    )
    user_rank = next((i + 1 for i, user in enumerate(ranking) if user == request.user), None)
    user_photos = UserImage.objects.filter(user=request.user).count()
    latest_news = NewsPost.objects.order_by('-date_time').first()
    event_messages = Event.objects.filter(date=date.today()).order_by('-date')
    context = {
        'user_rank': user_rank,
        'latest_news': latest_news,
        'user_photos': user_photos,
        'event_messages': event_messages,  
    }
    return render(request, 'pages/route_list.html', context)

@login_required
def list_routes(request):
    """ ดึงเส้นทางทั้งหมดของ Staff ที่ล็อกอินอยู่ """
    if request.user.is_superuser:
        routes = Route.objects.all()  # ✅ แอดมินเห็นทุก Route
    else:
        routes = Route.objects.filter(created_by=request.user)  # ✅ Staff เห็นแค่ Route ตัวเอง

    data = [
        {"id": route.id, "name": route.name, "start_time": route.start_time.strftime("%H:%M")}
        for route in routes
    ]
    return JsonResponse(data, safe=False)

# 📌 เพิ่มเส้นทางใหม่
@csrf_exempt
def add_route(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "คุณต้องเข้าสู่ระบบก่อน"}, status=403)

        try:
            data = json.loads(request.body)

            # ✅ ดึงค่า temple_id, name และ start_time
            temple_id = data.get("temple_id")
            name = data.get("name")
            start_time = data.get("start_time")

            # ❌ ตรวจสอบว่าข้อมูลครบถ้วน
            if not temple_id or not name or not start_time:
                return JsonResponse({"error": "ข้อมูลไม่ครบถ้วน"}, status=400)

            # ❌ ตรวจสอบว่าวัดมีอยู่จริง
            try:
                temple = Temple.objects.get(id=temple_id)
            except Temple.DoesNotExist:
                return JsonResponse({"error": "ไม่พบวัดที่เลือก"}, status=404)

            # ✅ แปลง start_time จาก string เป็น time object
            start_time_obj = datetime.strptime(start_time, "%H:%M").time()

            # ✅ บันทึกเส้นทางลงฐานข้อมูล พร้อมระบุ created_by
            route = Route.objects.create(
                temple=temple,
                name=name,
                start_time=start_time_obj,
                created_by=request.user  # ✅ บันทึกว่าผู้ใช้คนไหนสร้างเส้นทาง
            )

            return JsonResponse({"message": "Route added", "id": route.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "รูปแบบ JSON ไม่ถูกต้อง"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)




# 📌 แก้ไข Route
@csrf_exempt
def update_route(request, route_id):
    if request.method == "PUT":
        try:
            route = Route.objects.get(id=route_id)

            # ✅ ตรวจสอบว่าเป็นเจ้าของ หรือ superuser
            if request.user != route.temple.created_by and not request.user.is_superuser:
                return JsonResponse({"error": "คุณไม่มีสิทธิ์แก้ไขเส้นทางนี้"}, status=403)

            data = json.loads(request.body)

            # ✅ อัปเดตชื่อเส้นทาง
            if "name" in data:
                route.name = data["name"]

            # ✅ อัปเดตเวลาเริ่ม
            if "start_time" in data:
                parsed_time = parse_time(data["start_time"])
                if parsed_time:
                    route.start_time = parsed_time
                else:
                    return JsonResponse({"error": "รูปแบบเวลาไม่ถูกต้อง (ควรเป็น HH:MM)"}, status=400)

            route.save()
            return JsonResponse({"message": "✅ อัปเดตเส้นทางสำเร็จ!"}, status=200)

        except Route.DoesNotExist:
            return JsonResponse({"error": "ไม่พบเส้นทาง"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)

# 📌 ลบ Route
@csrf_exempt
def delete_route(request, route_id):
    if request.method == "DELETE":
        try:
            route = Route.objects.get(id=route_id)
            route.delete()
            return JsonResponse({"message": "Route deleted"}, status=200)
        except Route.DoesNotExist:
            return JsonResponse({"error": "Route not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)

# 📌 ดึง Checkpoints ตาม Route
@csrf_exempt
def list_checkpoints(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    checkpoints = route.checkpoints.order_by('order')
    data = [{"id": cp.id, "name": cp.name, "lat": cp.lat, "lon": cp.lon, "order": cp.order, "travel_time": cp.travel_time.total_seconds() / 60} for cp in checkpoints]
    return JsonResponse(data, safe=False)

# 📌 เพิ่ม Checkpoint
@csrf_exempt
def add_checkpoint(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            travel_time = int(data.get("travel_time", 5))  # ✅ แปลงเป็น int ก่อนใช้

            checkpoint = Checkpoint.objects.create(
                route=route, 
                name=data.get("name", "Checkpoint"), 
                lat=float(data["lat"]),  # ✅ แปลง lat เป็น float
                lon=float(data["lon"]),  # ✅ แปลง lon เป็น float
                order=int(data.get("order", route.checkpoints.count() + 1)),  # ✅ แปลง order เป็น int
                travel_time=timedelta(minutes=travel_time)  # ✅ ใช้ travel_time ที่แปลงแล้ว
            )
            return JsonResponse({"message": "Checkpoint added", "id": checkpoint.id}, status=201)

        except ValueError:
            return JsonResponse({"error": "Invalid travel_time format"}, status=400)
        except KeyError:
            return JsonResponse({"error": "Missing required fields"}, status=400)


# 📌 ลบ Checkpoint
@csrf_exempt
def delete_checkpoint(request, checkpoint_id):
    checkpoint = get_object_or_404(Checkpoint, id=checkpoint_id)
    if request.method == "DELETE":
        checkpoint.delete()
        return JsonResponse({"message": "Checkpoint deleted"}, status=204)
    
@login_required
def manage_routes(request):
    return render(request, "element/manage_routes.html")

@csrf_exempt
def update_checkpoint(request, checkpoint_id):
    try:
        checkpoint = Checkpoint.objects.get(id=checkpoint_id)

        if request.method == "PUT":
            data = json.loads(request.body)
            checkpoint.name = data.get("name", checkpoint.name)
            checkpoint.lat = data.get("lat", checkpoint.lat)
            checkpoint.lon = data.get("lon", checkpoint.lon)

            # ✅ แปลง travel_time จาก int (นาที) เป็น timedelta ก่อนบันทึก
            travel_time_minutes = data.get("travel_time", None)
            if travel_time_minutes is not None:
                checkpoint.travel_time = timedelta(minutes=int(travel_time_minutes))

            checkpoint.save()

            return JsonResponse({"message": "Checkpoint updated successfully!"}, status=200)

    except Checkpoint.DoesNotExist:
        return JsonResponse({"error": "Checkpoint not found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)


def get_routes_by_temple(request, temple_id):
    routes = Route.objects.filter(temple_id=temple_id).values("id", "name", "start_time","temple_id")
    return JsonResponse(list(routes), safe=False)

# ✅ API ดึงข้อมูลวัดทั้งหมด
@login_required
def temple_list(request):
    """ ✅ จำกัดให้ staff เห็นเฉพาะวัดที่ตัวเองสร้าง """
    if request.user.is_superuser:
        temples = Temple.objects.all()  # Admin เห็นทุกวัด
    elif request.user.is_staff:
        temples = Temple.objects.filter(created_by=request.user)  # Staff เห็นเฉพาะวัดของตัวเอง
    else:
        temples = Temple.objects.all().only("id", "name")  # User ทั่วไปเห็นวัดทั้งหมดแต่ไม่มีข้อมูลอื่น

    data = list(temples.values("id", "name", "location", "created_by_id"))
    return JsonResponse(data, safe=False)  # User ทั่วไปเห็นวัดทั้งหมดแต่ไม่มีข้อมูลอื่น
    
# ✅ API เพิ่มวัดใหม่
@csrf_exempt
@login_required  # ปิดการตรวจสอบ CSRF (ใช้สำหรับ API)
def add_temple(request):
    if not request.user.is_staff:  # ❌ ผู้ใช้ทั่วไปห้ามเพิ่ม
        return JsonResponse({"error": "ไม่มีสิทธิ์เพิ่มวัด"}, status=403)

    if request.user.assigned_temple:  # ❌ Staff มีวัดอยู่แล้ว
        return JsonResponse({"error": "คุณมีวัดอยู่แล้ว ไม่สามารถเพิ่มใหม่ได้"}, status=403)

    if request.method == "POST":
        try:
            data = json.loads(request.body)  # อ่าน JSON จาก request
            name = data.get("name")
            location = data.get("location", "")

            if not name:
                return JsonResponse({"error": "ต้องระบุชื่อวัด"}, status=400)

            temple = Temple.objects.create(name=name, location=location, created_by=request.user)

            request.user.assigned_temple = temple
            request.user.save(update_fields=["assigned_temple"])

            return JsonResponse({"message": "✅ เพิ่มวัดเรียบร้อย!", "id": temple.id})

        except json.JSONDecodeError:
            return JsonResponse({"error": "ข้อมูลไม่ถูกต้อง"}, status=400)

    return JsonResponse({"error": "ใช้ได้เฉพาะ POST"}, status=405)


@csrf_exempt
@login_required
def delete_temple(request, temple_id):
    if request.method == "DELETE":
        try:
            temple = Temple.objects.get(id=temple_id)

            if temple.created_by != request.user and not request.user.is_superuser:
                return JsonResponse({"error": "คุณไม่มีสิทธิ์ลบวัดนี้"}, status=403)

            temple.delete()
            return JsonResponse({"message": "✅ ลบวัดเรียบร้อย!"}, status=200)

        except Temple.DoesNotExist:
            return JsonResponse({"error": "ไม่พบวัด"}, status=404)

    return JsonResponse({"error": "Invalid request method"}, status=400)

@csrf_exempt
@login_required
def update_temple(request, temple_id):
    if request.method == "PUT":
        try:
            temple = Temple.objects.get(id=temple_id)

            if not request.user.is_superuser and temple.created_by != request.user:
                return JsonResponse({"error": "ไม่มีสิทธิ์แก้ไขวัดนี้"}, status=403)

            data = json.loads(request.body)
            temple.name = data.get("name", temple.name)
            temple.save()
            return JsonResponse({"message": "✅ อัปเดตชื่อวัดเรียบร้อย!"})

        except Temple.DoesNotExist:
            return JsonResponse({"error": "ไม่พบวัด"}, status=404)

    return JsonResponse({"error": "Invalid request method"}, status=400)


def robots_txt(request):
    content = "User-agent: *\nDisallow:"
    return HttpResponse(content, content_type="text/plain")


def capture_view(request):
    return render(request, 'element/capture.html')

@login_required
def check_daily_photo(request):
    now_time = localtime(now())  # ใช้ localtime เพื่อให้เป็นเวลาตามประเทศ
    today = now_time.date()
    start_time = now_time.replace(hour=5, minute=0, second=0, microsecond=0)
    end_time = now_time.replace(hour=8, minute=0, second=0, microsecond=0)

    has_taken_photo = UserImage.objects.filter(user=request.user, uploaded_at__date=today).exists()
    is_within_time_range = start_time <= now_time <= end_time  # ตรวจสอบว่าตอนนี้อยู่ในช่วงเวลาหรือไม่

    return JsonResponse({"has_taken_photo": has_taken_photo, "is_within_time_range": is_within_time_range})


@csrf_exempt
def add_event(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # ✅ ดึงวัดจาก temple_id ที่รับมา
            temple = Temple.objects.get(id=data["temple_id"])
            date = data["date"]

            # ✅ ลบ event เก่าของวัดนี้ที่มีวันที่เก่ากว่า
            Event.objects.filter(temple=temple, date__lt=now().date()).delete()

            # ✅ ลบ event ซ้ำในวันเดียวกัน (ถ้ามี)
            Event.objects.filter(temple=temple, date=date).delete()

            # ✅ สร้างเหตุการณ์ใหม่
            event = Event.objects.create(
                temple=temple,
                date=data["date"],
                event_type=data["event_type"],
                description=data["description"],
                is_canceled=data["is_canceled"]
            )

            return JsonResponse({"success": True, "message": "เพิ่มเหตุการณ์สำเร็จ!", "event_id": event.id}, status=201)
        
        except Temple.DoesNotExist:
            return JsonResponse({"success": False, "error": "ไม่พบวัดที่เลือก"}, status=400)
        
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

@csrf_exempt
def list_events(request, temple_id=None):
    """ API สำหรับดึง Event ของวัดที่เลือก """
    if temple_id:
        # ลบเหตุการณ์เก่าที่มีวันที่เก่ากว่า
        Event.objects.filter(temple_id=temple_id, date__lt=now().date()).delete()

        events = Event.objects.filter(temple_id=temple_id).order_by("date")
    else:
        events = Event.objects.all().order_by("date")

    event_list = [
        {
            "id": event.id,
            "date": event.date.strftime("%Y-%m-%d"),
            "event_type": event.get_event_type_display(),
            "description": event.description,
            "is_canceled": event.is_canceled,
        }
        for event in events
    ]
    return JsonResponse(event_list, safe=False)


@csrf_exempt
def delete_event(request, event_id):
    """ API สำหรับลบ Event """
    if request.method == "DELETE":
        try:
            event = Event.objects.get(id=event_id)
            event.delete()
            return JsonResponse({"message": "Event deleted successfully"}, status=200)
        except Event.DoesNotExist:
            return JsonResponse({"error": "Event not found"}, status=404)
    
    return JsonResponse({"error": "Invalid request method"}, status=400)
    

@login_required
def user_info(request):
    return JsonResponse({
        "is_staff": request.user.is_staff,
        "assigned_temple": request.user.assigned_temple.id if request.user.assigned_temple else None
    })