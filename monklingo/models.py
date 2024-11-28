from django.contrib.gis.db import models

class Route(models.Model):
    name = models.CharField(max_length=100)  # ชื่อเส้นทาง
    geometry = models.LineStringField()  # เส้นทาง
    description = models.TextField(blank=True, null=True)  # คำอธิบาย

class Checkpoint(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='checkpoints')
    name = models.CharField(max_length=100)  # ชื่อจุด
    location = models.PointField()  # พิกัดจุด
    order = models.IntegerField()  # ลำดับจุด

class Meta:
        db_table = 'monklingo_route'  # กำหนดชื่อที่ต้องการให้ตารางในฐานข้อมูล