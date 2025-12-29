from django.urls import path
from django.http import HttpResponse

from .views import add
def home(request):
    return HttpResponse("Home page")

urlpatterns = [
    path('', home),
    path('add/', add, name='add')
]
