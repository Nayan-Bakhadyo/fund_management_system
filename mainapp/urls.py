from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('send_verification_code/', views.send_verification_code, name='send_verification_code'),
    path('verify_email/', views.verify_email, name='verify_email'),
    path('logout/', views.logout_view, name='logout'), 
    path('fundmanager/dashboard/', views.fundmanager_dashboard, name='fundmanager_dashboard'),
    path('fundmanager/add_transaction/', views.add_transaction, name='add_transaction'),
    path('fundmanager/add_transaction_form/', views.add_transaction_form, name='add_transaction_form'),
    path('fundmanager/view_transactions/', views.view_transactions, name='view_transactions'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/portfolio/', views.portfolio, name='portfolio'),
    path('user/transactions/', views.transaction_history, name='transaction_history'),
    path('auth/', include('social_django.urls', namespace='social')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)