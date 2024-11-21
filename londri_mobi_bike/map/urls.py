from django.urls import path
from . import views

app_name = 'map'
urlpatterns = [
    path('', views.index, name='index'),
    path("login/", views.LoginView.as_view(), name="login"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path('logout/', views.logout_view, name="logout"),
    path('rent/', views.RentView.as_view(), name="rent"),
    path('redict_rent', views.redict_rent, name="redirect")
]
