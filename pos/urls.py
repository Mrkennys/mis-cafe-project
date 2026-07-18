from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='pos/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('route/', views.route_user, name='route_user'),
    path('', views.waiter_dashboard, name='waiter_dashboard'),
    path('create-order/', views.create_order, name='create_order'),
    path('cashier/', views.cashier_dashboard, name='cashier_dashboard'),
    path('settle-order/', views.settle_order, name='settle_order'),
]

