from django.contrib import admin
from .models import Role, Employee, LeaveRequest, LeaveApproval

# Admin class for Role model
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_name',)  # Display role name in the list view
    search_fields = ('role_name',)  # Allow searching by role name

admin.site.register(Role, RoleAdmin)


# Admin class for Employee model
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'post', 'employment_no', 'annual_leave_entitlement', 'leave_days_taken')
    search_fields = ('name', 'employment_no')  # Allow searching by name and employment number
    list_filter = ('grade', 'post')  # Filter employees by grade and post
    list_editable = ('annual_leave_entitlement', 'leave_days_taken')  # Make these fields editable directly in the list view

admin.site.register(Employee, EmployeeAdmin)


# Admin class for LeaveRequest model
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'start_date', 'end_date', 'status', 'submission_date', 'leave_grant_requested')
    search_fields = ('employee__name', 'status')  # Allow searching by employee name and status
    list_filter = ('status',)  # Filter by leave status

    # Method to show the number of days in the list view
    def days(self, obj):
        return obj.calculate_leave_days()
    days.short_description = 'Leave Days'

    # Adding the custom days to the list view
    list_display += ('days',)

admin.site.register(LeaveRequest, LeaveRequestAdmin)


# Admin class for LeaveApproval model
class LeaveApprovalAdmin(admin.ModelAdmin):
    list_display = ('leave_request', 'approver', 'approval_status', 'action_date', 'signature')
    search_fields = ('leave_request__employee__name', 'approval_status')  # Allow searching by employee name and approval status
    list_filter = ('approval_status',)  # Filter by approval status

admin.site.register(LeaveApproval, LeaveApprovalAdmin)
