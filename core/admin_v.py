from django.shortcuts import render, redirect
from django.contrib import messages
from .models import LeaveRequest, Employee, LeaveApproval
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import LeaveRequest

@login_required
def home_admin(request):
    employee = request.user.employee  # Assuming the user has a one-to-one Employee relationship
    total_annual_leave = employee.annual_leave_entitlement

    # Get all approved leave requests
    approved_leaves = LeaveApproval.objects.filter(
        leave_request__employee=employee, 
        approval_status='Approved'
    )

    # Sum up the leave days from approved leave requests
    approved_leave_days = 0
    for approval in approved_leaves:
        leave_request = approval.leave_request
        approved_leave_days += leave_request.calculate_leave_days()

    # Calculate remaining leave days
    remaining_leave = total_annual_leave - approved_leave_days
    leave_requests = LeaveRequest.objects.filter(employee=employee, status='Head Approved')
    leave_countdowns = [leave.countdown() for leave in leave_requests]

   
        
    

    # Filter leave requests by the currently logged-in user
    leave_requests = LeaveRequest.objects.filter(user=request.user)

    leave_requests_data = []
    for leave in leave_requests:
        # Check if the approval exists for 'Head of Department'
        head_approved = leave.leaveapproval_set.filter(
            approver_role__role_name='Head of Department',  # Match database role name
            approval_status='Approved'  # Use the correct field name
        ).exists()

        leave_requests_data.append({
            'id': leave.id,
            'employee_name': leave.employee.name,
            'start_date': leave.start_date,
            'end_date': leave.end_date,
            'status': "Approved by Head" if head_approved else "Pending",
            'download_enabled': head_approved,  # Enable only if Head approved
        })
    
    # Paginate the leave requests data
    paginator = Paginator(leave_requests_data, 10)  # Show 10 leave requests per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'employee': employee,
        'total_annual_leave': total_annual_leave,
        'approved_leave_days': approved_leave_days,
        'remaining_leave': remaining_leave,
        'leave_countdowns': leave_countdowns,
        'page_obj': page_obj
    }
    return render(request, 'admin_z/index.html', context)