from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [    
    path('', views.HomeView.as_view(), name="home" ),   
    path('about/', views.AboutView.as_view(), name="about" ),  
    path('services/', views.ServicesView.as_view(), name="services" ),  
    path('contact/', views.ContactView.as_view(), name="contact" ),      
    path('dashboard/', views.DashboardView.as_view(), name="dashboard" ),  
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('createticket/', views.CreateTicket.as_view(), name='create_ticket'),    
    path('admin_view_ticket/', views.AdminTicketView.as_view(), name='admin_ticket'),
    path('technician_view_ticket/', views.TechnicianTicketView.as_view(), name='tech_ticket'),
    path('client_view_status/', views.ClientTicketView.as_view(), name='client_status'),
    path('ticket/<int:pk>/update/', views.TicketUpdateView.as_view(), name='ticket_update'),
    path('rate_technician/<int:pk>/', views.RateTechnicianView.as_view(), name='rate_technician'),
    path('delete_ticket/<int:pk>/', views.DeleteTicketView.as_view(), name='delete_ticket'),
    path('speed_test/', views.speed_test, name='speed_test'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

