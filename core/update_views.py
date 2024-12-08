from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import LeaveRequest, Employee, LeaveApproval
from django.utils import timezone
from datetime import timedelta

# View to add a leave request without using forms.py
@login_required
def add_leave_request(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        contact_address_during_leave = request.POST.get('contact_address_during_leave')
        leave_grant_requested = request.POST.get('leave_grant_requested')

        if start_date and end_date:
            # Ensure the dates are valid
            try:
                start_date = timezone.datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = timezone.datetime.strptime(end_date, "%Y-%m-%d").date()

                if start_date > end_date:
                    raise ValueError("Start date cannot be later than end date")

                # Create the leave request object
                leave_request = LeaveRequest(
                    employee=request.user.employee,  # Assuming the user has a one-to-one Employee relationship
                    start_date=start_date,
                    end_date=end_date,
                    contact_address_during_leave=contact_address_during_leave,
                    leave_grant_requested=leave_grant_requested,
                    status="Pending",  # Initial status is Pending
                    submission_date=timezone.now(),
                    user=request.user
                )
                leave_request.save()

                return redirect('dashboard')  # Redirect to the dashboard after submitting the request
            except ValueError as e:
                # Handle invalid date format or start > end date
                return render(request, 'add_leave_request.html', {'error': str(e)})

    return render(request, 'add_leave_request.html')

@login_required
def add_leave_request_hr_x(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        contact_address_during_leave = request.POST.get('contact_address_during_leave')
        leave_grant_requested = request.POST.get('leave_grant_requested')

        if start_date and end_date:
            # Ensure the dates are valid
            try:
                start_date = timezone.datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = timezone.datetime.strptime(end_date, "%Y-%m-%d").date()

                if start_date > end_date:
                    raise ValueError("Start date cannot be later than end date")

                # Create the leave request object
                leave_request = LeaveRequest(
                    employee=request.user.employee,  # Assuming the user has a one-to-one Employee relationship
                    start_date=start_date,
                    end_date=end_date,
                    contact_address_during_leave=contact_address_during_leave,
                    leave_grant_requested=leave_grant_requested,
                    status="Pending",  # Initial status is Pending
                    submission_date=timezone.now(),
                    user=request.user
                )
                leave_request.save()

                return redirect('hr_dashboard')  # Redirect to the dashboard after submitting the request
            except ValueError as e:
                # Handle invalid date format or start > end date
                return render(request, 'hr/request_leave.html', {'error': str(e)})

    return render(request, 'hr/request_leave.html')



@login_required
def add_leave_request_sp_x(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        contact_address_during_leave = request.POST.get('contact_address_during_leave')
        leave_grant_requested = request.POST.get('leave_grant_requested')

        if start_date and end_date:
            # Ensure the dates are valid
            try:
                start_date = timezone.datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = timezone.datetime.strptime(end_date, "%Y-%m-%d").date()

                if start_date > end_date:
                    raise ValueError("Start date cannot be later than end date")

                # Create the leave request object
                leave_request = LeaveRequest(
                    employee=request.user.employee,  # Assuming the user has a one-to-one Employee relationship
                    start_date=start_date,
                    end_date=end_date,
                    contact_address_during_leave=contact_address_during_leave,
                    leave_grant_requested=leave_grant_requested,
                    status="Pending",  # Initial status is Pending
                    submission_date=timezone.now(),
                    user=request.user
                )
                leave_request.save()

                return redirect('sp_dashboard')  # Redirect to the dashboard after submitting the request
            except ValueError as e:
                # Handle invalid date format or start > end date
                return render(request, 'sp/leave_requests.html', {'error': str(e)})

    return render(request, 'sp/leave_requests.html')


@login_required
def add_leave_request_hd_x(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        contact_address_during_leave = request.POST.get('contact_address_during_leave')
        leave_grant_requested = request.POST.get('leave_grant_requested')

        if start_date and end_date:
            # Ensure the dates are valid
            try:
                start_date = timezone.datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = timezone.datetime.strptime(end_date, "%Y-%m-%d").date()

                if start_date > end_date:
                    raise ValueError("Start date cannot be later than end date")

                # Create the leave request object
                leave_request = LeaveRequest(
                    employee=request.user.employee,  # Assuming the user has a one-to-one Employee relationship
                    start_date=start_date,
                    end_date=end_date,
                    contact_address_during_leave=contact_address_during_leave,
                    leave_grant_requested=leave_grant_requested,
                    status="Pending",  # Initial status is Pending
                    submission_date=timezone.now(),
                    user=request.user
                )
                leave_request.save()

                return redirect('hd_dashboard')  # Redirect to the dashboard after submitting the request
            except ValueError as e:
                # Handle invalid date format or start > end date
                return render(request, 'hd/leave_requests.html', {'error': str(e)})

    return render(request, 'hd/leave_requests.html')


# View to show the dashboard with annual leave and approved leave days
@login_required
def dashboard(request):
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

    return render(request, 'dashboard.html', {
        'employee': employee,
        'total_annual_leave': total_annual_leave,
        'approved_leave_days': approved_leave_days,
        'remaining_leave': remaining_leave,
        'leave_countdowns': leave_countdowns,
    })
