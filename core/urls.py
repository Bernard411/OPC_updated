from django.urls import path
from . import views

urlpatterns = [
    path('hr-dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('supervisor-dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('head-of-section-dashboard/', views.head_of_section_dashboard, name='head_of_section_dashboard'),
    path('leave-request/approve/<int:leave_request_id>/', views.hr_approval, name='hr_approval'),
    path('leave-request/approve/supervisor/<int:leave_request_id>/', views.supervisor_approval, name='supervisor_approval'),
    path('leave-request/approve/head-of-section/<int:leave_request_id>/', views.head_of_section_approval, name='head_of_section_approval'),
    path('register/', views.register, name='register'),
    path('', views.login_view, name='login_view' ),
    path('leave/request/', views.create_leave_request, name='submit_leave_request'),
   path('generate-pdf/<int:leave_id>/', views.generate_leave_form_view, name='generate_leave_form_view'),
   path('leave-requests/', views.leave_requests_table, name='leave_requests_table'),
       path('logout_user/', views.logoutuser, name="logout_user"),
    path('success/', views.success_page, name='success'),
     path('home/', views.home, name='homepage'),


   path('hr/leave-requests/', views.leave_requests_table_hr, name='leave_requests_table_hr'),
    path('sp/leave-requests/', views.leave_requests_table_sp, name='leave_requests_table_sp'),
    path('hd/leave-requests/', views.leave_requests_table_hd, name='leave_requests_table_hd'),
]
