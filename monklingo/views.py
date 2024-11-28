from django.http import JsonResponse
from .models import Route
from django.contrib.gis.geos import Point

def get_routes(request):
    routes = Route.objects.prefetch_related('checkpoints').all()
    data = []

    for route in routes:
        checkpoints = route.checkpoints.order_by('order')
        data.append({
            "name": route.name,
            "geometry": list(route.geometry.coords),  # เส้นทางเป็น List ของพิกัด
            "checkpoints": [
                {
                    "name": cp.name,
                    "location": [cp.location.x, cp.location.y],  # พิกัดของ Checkpoint
                }
                for cp in checkpoints
            ]
        })

    return JsonResponse(data, safe=False)
