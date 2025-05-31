from django.urls import path,include
from . import views
urlpatterns = [
    
    path('',views.home,name='home'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),  
    path('mycart/', views.mycart, name='mycart'),
]
