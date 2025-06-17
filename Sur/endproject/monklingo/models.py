from django.db import models
from django.contrib.auth.models import  BaseUserManager , AbstractUser
from django.utils.timezone import now
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.timezone import timedelta, now, make_aware, datetime
from datetime import date

# Custom User Manager
class UserProfileManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

    def create_social_user(self, username, email=None, google_id=None, facebook_id=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(
            username=username, 
            email=email, 
            google_id=google_id, 
            facebook_id=facebook_id, 
            **extra_fields
        )
        user.set_unusable_password()  # No password needed for social login
        user.is_social_login = True
        user.save(using=self._db)
        return user


# Custom User Model
class CustomUser(AbstractUser):
    email = models.EmailField(max_length=255, blank=True,default="")
    full_name = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    facebook_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    google_token = models.TextField(blank=True, null=True)  # Optional: For storing Google Token
    facebook_token = models.TextField(blank=True, null=True)  # Optional: For storing Facebook Token
    is_social_login = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    assigned_temple = models.OneToOneField(
        "Temple", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_staff"
    )

    objects = UserProfileManager()

    def __str__(self):
        return self.username

class Temple(models.Model):
    name = models.CharField(max_length=255, unique=True, default="Unknown Temple")
    location = models.CharField(max_length=255, blank=True, null=True)  # เพิ่มที่ตั้งได้
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="temples")

    def __str__(self):
        return self.name

class Route(models.Model):
    name = models.CharField(max_length=255)  # ชื่อเส้นทาง
    start_time = models.TimeField()  # เวลาเริ่มต้นในแต่ละวัน  
    temple = models.ForeignKey(Temple, on_delete=models.CASCADE, related_name="routes", null=True, blank=True)  # เชื่อมกับ Temple
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name="routes")

    def __str__(self):
        return f"{self.temple.name} - {self.name}"  # ✅ แสดงชื่อวัด + เส้นทาง

    def get_today_start_time(self):
        """ ✅ คืนค่าเวลาเริ่มต้นของเส้นทางเป็น datetime ที่ใช้ได้จริง """
        today_start = make_aware(datetime.combine(now().date(), self.start_time))
        return today_start


class Checkpoint(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='checkpoints', default=None)
    name = models.CharField(max_length=255, default="Checkpoint")  # ✅ เพิ่มชื่อ Checkpoint
    lat = models.FloatField(default=None)  # ละติจูดของ Checkpoint
    lon = models.FloatField(default=None)  # ลองจิจูดของ Checkpoint
    order = models.PositiveIntegerField(default=None)  # ลำดับของจุดเช็คพอยต์
    travel_time = models.DurationField(default=timedelta(minutes=5))  # ⏳ เวลาที่ใช้เดินไปจุดถัดไป

    def __str__(self):
        return f"{self.name} (Checkpoint {self.order} for {self.route.name})"

    def get_today_arrival_time(self):
        """
        คืนค่า arrival_time สำหรับวันนี้โดยคำนวณจาก start_time + travel_time
        """
        return self.route.get_today_start_time() + sum(
            cp.travel_time for cp in self.route.checkpoints.filter(order__lt=self.order)
        )


class NewsPost(models.Model):
    news_id = models.AutoField(primary_key=True)
    heading = models.CharField(max_length=255)
    content = models.TextField()
    date_time = models.DateTimeField(default=now)
    img = models.ImageField(upload_to='prayers_images/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    age = models.TextField(null=True)
    TYPE_CHOICES = [
        ('news', 'News'),
        ('announcement', 'Announcement'),
        ('event', 'Event'),
    ]
    post_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='news')
    def __str__(self):
        return self.heading
    
class PrayersPost(models.Model):
    prayers_id = models.AutoField(primary_key=True)
    heading = models.CharField(max_length=255)
    content = models.TextField()
    date_time = models.DateTimeField(default=now)
    url = models.URLField(blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE ,null=True)
    
    def __str__(self):
        return self.heading
    

CustomUser = get_user_model()

# โมเดลสำหรับเก็บรูปภาพของผู้ใช้
class UserImage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_images')
    image = models.ImageField(upload_to='user_images/')
    uploaded_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.image.name}"


class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)  # ชื่อห้องต้องไม่ซ้ำ
    description = models.TextField(blank=True, null=True)  # รายละเอียดของห้อง
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField(blank=True)  # ทำให้ข้อความว่างได้ในกรณีส่งเฉพาะไฟล์หรือรูป
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    # ฟิลด์สำหรับไฟล์และรูปภาพ
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"


class Event(models.Model):
    EVENT_TYPES = [
        ('buddhist_day', 'วันพระ'),
        ('special_event', 'กิจนิมนต์'),
        ('weather', 'สภาพอากาศ'),
        ('other', 'เหตุการณ์อื่นๆ'),
    ]

    temple = models.ForeignKey(Temple, on_delete=models.CASCADE)
    date = models.DateField(default=now)  # วันที่ของ Event
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)  # ประเภทของ Event
    description = models.CharField(max_length=255)  # คำอธิบาย
    is_canceled = models.BooleanField(default=False)  # กรณีงดบิณฑบาต

    class Meta:
        unique_together = ('temple', 'date') 

    def __str__(self):
        status = " (งดบิณฑบาต)" if self.is_canceled else ""
        return f"{self.date}: {self.get_event_type_display()} - {self.description}{status}"

    @classmethod
    def get_today_events(cls):
        """ คืนค่ากิจกรรมของวันนี้ """
        today = date.today()
        return cls.objects.filter(date=today).order_by('event_type')