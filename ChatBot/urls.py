from django.urls import path
from ChatBot import views
urlpatterns = [
    path('', views.HomePage),
    path('login/', views.LoginPage),
    path('signup/', views.SignUpPage),
    path("logout/",views.LogOutPage),
    path("sendmessage/",views.SendMessage)
]