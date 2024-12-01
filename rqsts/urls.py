from django.urls import path
from . import views

urlpatterns = [
    path('create-request/', views.create_request, name='create_request'),
    path('start-working/<int:rqst_id>/', views.start_working_on_request, name='start_working_on_request'),
    path('view/<int:rqst_id>/', views.show_request_details, name='view_request'),
    path('profile/', views.view_profile, name='view_profile'),
    path('login/', views.user_login, name='user_login'),  # New URL for login
    path('logout/', views.user_logout, name='user_logout'),
]
