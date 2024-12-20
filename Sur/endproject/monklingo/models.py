from django.db import models
from django.contrib.auth.models import  BaseUserManager , AbstractUser
from django.utils.timezone import now
from django.conf import settings
from django.contrib.auth import get_user_model

#routes
class AlmsgivingRoute(models.Model):
    temple_name = models.CharField(max_length=255)
    starting_point_name = models.CharField(max_length=255)
    starting_point_lat = models.FloatField()
    starting_point_lng = models.FloatField()
    ending_point_name = models.CharField(max_length=255)
    ending_point_lat = models.FloatField()
    ending_point_lng = models.FloatField()
    average_time = models.CharField(max_length=8)  # เก็บรูปแบบ "00:30:00"
    distance = models.FloatField()
    number_of_monks = models.IntegerField()
    route_description = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.temple_name






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

# สร้าง Custom User Model
class CustomUser(AbstractUser):
    # เพิ่มฟิลด์เพิ่มเติมที่คุณต้องการ เช่น อีเมล, รูปภาพโปรไฟล์
    email = models.EmailField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.username

class NewsPost(models.Model):
    news_id = models.AutoField(primary_key=True)
    heading = models.CharField(max_length=255)
    content = models.TextField()
    date_time = models.DateTimeField(default=now)
    img = models.ImageField(upload_to='prayers_images/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
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
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.image.name}"

