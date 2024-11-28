from django.contrib import admin
from .models import Role, Employee, LeaveRequest, LeaveApproval

class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_name',)
    search_fields = ('role_name',)

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'post', 'employment_no', 'annual_leave_entitlement', 'leave_days_taken')
    list_filter = ('grade', 'post')
    search_fields = ('name', 'employment_no')
    raw_id_fields = ('user',)  # If you want to link the user object manually

class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'start_date', 'end_date', 'number_of_days', 'status', 'submission_date')
    list_filter = ('status', 'employee')
    search_fields = ('employee__name', 'status')

class LeaveApprovalAdmin(admin.ModelAdmin):
    list_display = ('leave_request', 'approver', 'approver_role', 'approval_status', 'action_date', 'comments')
    list_filter = ('approval_status', 'approver_role')
    search_fields = ('approver__name', 'leave_request__employee__name')

# Register models with the admin interface
admin.site.register(Role, RoleAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(LeaveRequest, LeaveRequestAdmin)
admin.site.register(LeaveApproval, LeaveApprovalAdmin)
