import os
import django
import random
from datetime import datetime, timedelta
from django.core.files.base import ContentFile
from django.utils.timezone import make_aware

# ✅ ตั้งค่า Django Environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "endproject.settings")  # เปลี่ยนเป็นชื่อโปรเจกต์ของคุณ
django.setup()  # ✅ เรียกใช้งาน Django

# ✅ นำเข้าโมเดล
from monklingo.models import CustomUser, UserImage

# ✅ ตรวจสอบและสร้างผู้ใช้ (20 คน)
print("🚀 สร้างผู้ใช้ใหม่ 20 คน...")
for i in range(1, 21):
    username = f"user{i}"
    if not CustomUser.objects.filter(username=username).exists():
        user = CustomUser.objects.create_user(
            username=username,
            password="password123",
        )
        print(f"✅ เพิ่มผู้ใช้: {username}")
    else:
        print(f"⚠️ ผู้ใช้ {username} มีอยู่แล้ว ข้าม...")

# ✅ ดึงข้อมูลผู้ใช้ทั้งหมด
users = list(CustomUser.objects.all())

print("\n🚀 อัปโหลดรูปภาพแบบสุ่ม (วันละ 10-20 รูป) ตั้งแต่มกราคมถึงมีนาคม...")
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 3, 31)
date_generated = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

for day in date_generated:
    num_images = random.randint(10, 20)  # ✅ สุ่มจำนวนรูปภาพต่อวัน (10-20 รูป)
    print(f"📅 Mocking {num_images} images for {day.strftime('%Y-%m-%d')}")

    for _ in range(num_images):  
        user = random.choice(users)  # ✅ เลือกผู้ใช้แบบสุ่ม
        
        # ✅ สุ่มเวลาอัปโหลดในช่วง 05:00 - 08:00 น.
        random_hour = random.randint(5, 7)  # เฉพาะ 05:00 - 07:59
        random_minute = random.randint(0, 59)
        random_second = random.randint(0, 59)
        
        uploaded_at = datetime.combine(day, datetime.min.time()) + timedelta(
            hours=random_hour, minutes=random_minute, seconds=random_second
        )

        # ✅ ใช้ make_aware() เพื่อให้รองรับ Timezone ของ Django
        uploaded_at = make_aware(uploaded_at)

        # ✅ สร้างไฟล์ภาพ Mock
        image_content = ContentFile(b"fake_image_data", name=f"{user.username}_{uploaded_at.strftime('%Y%m%d%H%M%S')}.jpg")
        
        # ✅ บันทึกข้อมูลลงฐานข้อมูล
        UserImage.objects.create(user=user, image=image_content, uploaded_at=uploaded_at)
    
    print(f"✅ อัปโหลดรูปสำหรับวันที่ {day.strftime('%Y-%m-%d')} เรียบร้อย! ({num_images} รูป)")

print("\n🎉 Mock Data เสร็จสิ้น! 🎉")
