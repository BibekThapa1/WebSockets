from asgiref.sync import async_to_sync

from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

from channels.layers import get_channel_layer

@csrf_exempt  # Only for testing; in production, handle CSRF properly
def add(request):
    if request.method == "POST":
        try:
            # Parse JSON body
            body = json.loads(request.body)
            data = body.get('data', 1)  # default empty list

            print("Entered here 2")
            # Example o peration: sum numbers
            # if isinstance(data, list):
            #     result = sum(data)
            # else:
            #     result = 0

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "demo",
                {
                    "type":"add_function",
                    "value": data
                }
            )

            print("Entered here 1")
            return JsonResponse({"result": data})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        return JsonResponse({"error": "POST request required"}, status=405)
