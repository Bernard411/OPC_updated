from django.shortcuts import render, redirect
from django.contrib import messages
from .models import LeaveRequest, Employee
from django.contrib.auth.decorators import login_required

@login_required

def create_leave_request(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        number_of_days = int(request.POST.get('number_of_days'))
        contact_address = request.POST.get('contact_address_during_leave', '')  # Default to empty string if not provided
        leave_grant_requested = request.POST.get('leave_grant_requested', '')

        employee = request.user.employee  # Assuming the logged-in user has an associated Employee

        # Create the leave request
        leave_request = LeaveRequest(
            employee=employee,
            start_date=start_date,
            end_date=end_date,
            number_of_days=number_of_days,
            contact_address_during_leave=contact_address,
            leave_grant_requested=leave_grant_requested,
        )
        leave_request.save()

        messages.success(request, 'Your leave request has been submitted and is pending approval.')
        return redirect('homepage')
    
    leave_requests = LeaveRequest.objects.all()

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

    return render(request, 'request_leave.html', {'leave_requests': leave_requests_data})


@login_required
def hr_approval(request, leave_request_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)

    # Check if the user has the HR role
    if request.user.employee.post and request.user.employee.post.role_name in ['HR']:  # Only HR can approve
        if request.method == 'POST':
            approval_status = request.POST.get('approval_status')
            comments = request.POST.get('comments', '')

            if approval_status == 'Rejected':
                leave_request.status = 'Rejected'
                leave_request.save()
                messages.error(request, 'Leave request has been rejected.')
            else:
                leave_request.status = 'HR Approved'
                leave_request.save()

                # Check if an HR approval exists, update it or create a new one
                hr_approval = leave_request.leaveapproval_set.filter(approver_role__role_name='HR').first()
                
                if hr_approval:
                    # If HR approval exists, update it
                    hr_approval.approval_status = 'Approved'
                    hr_approval.comments = comments
                    hr_approval.save()
                    messages.success(request, 'Leave request updated and forwarded to Supervisor.')
                else:
                    LeaveApproval.objects.create(
                        leave_request=leave_request,
                        approver=request.user.employee,  # Assuming 'employee' is related to 'User'
                        approver_role=request.user.employee.post,
                        approval_status='Approved',
                        comments=comments
                    )
                    messages.success(request, 'Leave request approved and forwarded to Supervisor.')

            return redirect('hr_dashboard')

        return render(request, 'hr/hr_approval.html', {'leave_request': leave_request})

    else:
        messages.error(request, 'You are not authorized to approve leave requests.')
        return redirect('hr_dashboard')
@login_required
def supervisor_approval(request, leave_request_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)

    # Supervisor can approve only if HR has approved
    if leave_request.status == 'HR Approved' and request.user.employee.post and request.user.employee.post.role_name == 'Supervisor':
        # Get the HR and Supervisor approvals
        hr_approval = leave_request.leaveapproval_set.filter(approver_role__role_name='HR').first()
        supervisor_approval = leave_request.leaveapproval_set.filter(approver_role__role_name='Supervisor').first()

        if request.method == 'POST':
            approval_status = request.POST.get('approval_status')
            comments = request.POST.get('comments', '')

            if approval_status == 'Rejected':
                leave_request.status = 'Rejected'
                leave_request.save()
                messages.error(request, 'Leave request has been rejected by Supervisor.')
            else:
                leave_request.status = 'Supervisor Approved'
                leave_request.save()

                LeaveApproval.objects.create(
                    leave_request=leave_request,
                    approver=request.user.employee,  # Assuming 'employee' is related to 'User'
                    approver_role=request.user.employee.post,
                    approval_status='Approved',
                    comments=comments
                )
                messages.success(request, 'Leave request approved and forwarded to Head of Section.')

            return redirect('supervisor_dashboard')

        return render(request, 'sp/supervisor_approval.html', {
            'leave_request': leave_request,
            'hr_approval': hr_approval,
            'supervisor_approval': supervisor_approval
        })

    else:
        messages.error(request, 'You are not authorized to approve this leave request or it is not at the correct stage.')
        return redirect('supervisor_dashboard')
@login_required
def head_of_section_approval(request, leave_request_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)

    # Head of Section can approve the leave request only if Supervisor has approved it
    if leave_request.status == 'Supervisor Approved' and request.user.employee.post and request.user.employee.post.role_name == 'Head of Department':
        # Get the HR, Supervisor, and Head of Section approvals
        hr_approval = leave_request.leaveapproval_set.filter(approver_role__role_name='HR').first()
        supervisor_approval = leave_request.leaveapproval_set.filter(approver_role__role_name='Supervisor').first()
        head_of_section_approval = leave_request.leaveapproval_set.filter(approver_role__role_name='Head of Department').first()

        if request.method == 'POST':
            approval_status = request.POST.get('approval_status')
            comments = request.POST.get('comments', '')

            if approval_status == 'Rejected':
                leave_request.status = 'Rejected'
                leave_request.save()
                messages.error(request, 'Leave request has been rejected by Head of Section.')
            else:
                leave_request.status = 'Head Approved'
                leave_request.save()
                LeaveApproval.objects.create(
                    leave_request=leave_request,
                    approver=request.user.employee,
                    approver_role=request.user.employee.post,
                    approval_status='Approved',
                    comments=comments
                )
                messages.success(request, 'Leave request approved successfully.')

            return redirect('head_of_section_dashboard')

        return render(request, 'hd/head_of_section_approval.html', {
            'leave_request': leave_request,
            'hr_approval': hr_approval,
            'supervisor_approval': supervisor_approval,
            'head_of_section_approval': head_of_section_approval,
        })

    else:
        messages.error(request, 'Leave request cannot be approved by you at this stage.')
        return redirect('head_of_section_dashboard')


from django.shortcuts import render
from .models import LeaveRequest

@login_required
def leave_request_list(request):
    employee = request.user.employee
    leave_requests = LeaveRequest.objects.filter(employee=employee)

    return render(request, 'leave_request_list.html', {'leave_requests': leave_requests})

def home(request):
    leave_requests = LeaveRequest.objects.all()
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

    return render(request, 'home.html', {'leave_requests': leave_requests_data})


from django.shortcuts import render
from django.urls import reverse



@login_required
def leave_requests_table(request):
    leave_requests = LeaveRequest.objects.all()

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

    return render(request, 'leave_requests_table.html', {'leave_requests': leave_requests_data})

from django.core.paginator import Paginator
from django.shortcuts import render

def leave_requests_table_hr(request):
    leave_requests = LeaveRequest.objects.all()

    leave_requests_data = []
    for leave in leave_requests:
        head_approved = leave.leaveapproval_set.filter(
            approver_role__role_name='Head of Department',
            approval_status='Approved'
        ).exists()

        leave_requests_data.append({
            'id': leave.id,
            'employee_name': leave.employee.name,
            'start_date': leave.start_date,
            'end_date': leave.end_date,
            'status': "Approved by Head" if head_approved else "Pending",
            'download_enabled': head_approved,
        })

    # Paginate the leave requests data
    paginator = Paginator(leave_requests_data, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'hr/leave_requests_table.html', {'page_obj': page_obj})


def leave_requests_table_sp(request):
    leave_requests = LeaveRequest.objects.all()

    leave_requests_data = []
    for leave in leave_requests:
        head_approved = leave.leaveapproval_set.filter(
            approver_role__role_name='Head of Department',
            approval_status='Approved'
        ).exists()

        leave_requests_data.append({
            'id': leave.id,
            'employee_name': leave.employee.name,
            'start_date': leave.start_date,
            'end_date': leave.end_date,
            'status': "Approved by Head" if head_approved else "Pending",
            'download_enabled': head_approved,
        })

    paginator = Paginator(leave_requests_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'sp/leave_requests_table.html', {'page_obj': page_obj})


def leave_requests_table_hd(request):
    leave_requests = LeaveRequest.objects.all()

    leave_requests_data = []
    for leave in leave_requests:
        head_approved = leave.leaveapproval_set.filter(
            approver_role__role_name='Head of Department',
            approval_status='Approved'
        ).exists()

        leave_requests_data.append({
            'id': leave.id,
            'employee_name': leave.employee.name,
            'start_date': leave.start_date,
            'end_date': leave.end_date,
            'status': "Approved by Head" if head_approved else "Pending",
            'download_enabled': head_approved,
        })

    paginator = Paginator(leave_requests_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'hd/leave_requests_table.html', {'page_obj': page_obj})





from django.shortcuts import render
from .models import LeaveRequest, LeaveApproval
from django.contrib.auth.decorators import login_required


from django.shortcuts import render
from .models import LeaveRequest, LeaveApproval



from django.shortcuts import render
from .models import LeaveRequest, LeaveApproval
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import LeaveRequest

@login_required
def hr_dashboard(request):
    if request.user.employee.post and request.user.employee.post.role_name == 'HR':  # Check if the user is HR
        leave_requests = LeaveRequest.objects.all()  # Or filter as needed

        # Pre-fetching approvals related to the leave requests to optimize database hits
        for leave_request in leave_requests:
            leave_request.hr_approval = leave_request.leaveapproval_set.filter(approver_role__role_name='HR').first()
            leave_request.supervisor_approval = leave_request.leaveapproval_set.filter(approver_role__role_name='Supervisor').first()
            leave_request.head_approval = leave_request.leaveapproval_set.filter(approver_role__role_name='Head of Department').first()

        return render(request, 'hr/hr_dashboard.html', {'leave_requests': leave_requests})
    else:
        return redirect('home')  # Redirect to home if not HR

from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import LeaveRequest

@login_required
def supervisor_dashboard(request):
    if request.user.employee.post and request.user.employee.post.role_name == 'Supervisor':  # Check if the user is Supervisor
        leave_requests = LeaveRequest.objects.filter(status='HR Approved')  # Only show HR-approved requests
        paginator = Paginator(leave_requests, 10)  # Show 10 leave requests per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'sp/supervisor_dashboard.html', {'page_obj': page_obj})
    else:
        return redirect('home')  # Redirect to home if not Supervisor


@login_required
def head_of_section_dashboard(request):
    if request.user.employee.post and request.user.employee.post.role_name == 'Head of Department':  # Check if the user is Head of Department
        leave_requests = LeaveRequest.objects.filter(status='Supervisor Approved')  # Only show Supervisor-approved requests
        return render(request, 'hd/head_of_section_dashboard.html', {'leave_requests': leave_requests})
    else:
        return redirect('home')  # Redirect to home if not Head of Department


from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import RegistrationForm
from .models import Employee, Role
from django.contrib.auth.models import User

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create the user
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )

            # Create the employee record
            role = Role.objects.get(role_name=form.cleaned_data['role'])
            employee = Employee.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                grade=form.cleaned_data['grade'],
                post=role,
                employment_no=form.cleaned_data['employment_no'],
                contact_address=form.cleaned_data['contact_address'],
                bank_name=form.cleaned_data['bank_name'],
                bank_account_no=form.cleaned_data['bank_account_no'],
                annual_leave_entitlement=form.cleaned_data['annual_leave_entitlement']
            )

            # Log the user in and redirect to the appropriate dashboard
            login(request, user)
            messages.success(request, 'Registration successful! You are now logged in.')

            # Redirect to the home page or user dashboard
            return redirect('home')  # Replace with a specific dashboard URL if needed
        else:
            messages.error(request, 'There was an error in the form. Please check your input.')
    else:
        form = RegistrationForm()

    return render(request, 'hr/register.html', {'form': form})

# views.py
# from .forms import EmailAuthenticationForm

# def custom_login(request):
#     if request.method == 'POST':
#         form = EmailAuthenticationForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password']
#             user = authenticate(request, username=email, password=password)

#             if user is not None:
#                 login(request, user)
#                 messages.success(request, 'You have successfully logged in!')
#                 # Redirect user based on role
#                 if user.employee.grade == 'A' or user.employee.grade == 'B':
#                     return redirect('hr_dashboard')
#                 elif user.employee.grade == 'C':
#                     return redirect('supervisor_dashboard')
#                 elif user.employee.grade == 'E (P4)':
#                     return redirect('head_of_section_dashboard')
#                 else:
#                     return redirect('home')  # Or any default page

#             else:
#                 messages.error(request, 'Invalid email or password.')
#         else:
#             messages.error(request, 'Invalid form submission.')

#     else:
#         form = EmailAuthenticationForm()

#     return render(request, 'login.html', {'form': form})

from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .EmailBackEnd import EmailBackEnd
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import login as auth_login


from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import redirect, render

def login_view(request):
    if request.method == "POST":
        user = EmailBackEnd.authenticate(request, username=request.POST.get('email'), password=request.POST.get('password'))
        if user is not None:
            login(request, user)
            messages.success(request, 'You have successfully logged in!')
            
            # Redirect user based on role
            if user.employee.post and user.employee.post.role_name == 'HR':
                return redirect('hr_dashboard')
            elif user.employee.post and user.employee.post.role_name == 'Supervisor':
                return redirect('supervisor_dashboard')
            elif user.employee.post and user.employee.post.role_name == 'Head of Department':
                return redirect('head_of_section_dashboard')
            else:
                return redirect('homepage')  # Default page for employees with no specific role
                
        else:
            messages.error(request, "Invalid Login Credentials!")
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')


def logoutuser(request):
    logout(request)
    return redirect('login_view')

def success_page(request):
    return render(request, 'success.html')


from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa  # Use any library for PDF generation

# @login_required
# def generate_leave_form_view(request, leave_id):
#     leave_request = LeaveRequest.objects.get(id=leave_id)

#     # Fetch details for the leave form
#     context = {
#         'name': leave_request.employee.name,
#         'grade': leave_request.employee.grade,
#         'employment_no': leave_request.employee.employment_no,
#         'bank_name': leave_request.employee.bank_name,
#         'account_no': leave_request.employee.bank_account_no,
#         'start_date': leave_request.start_date,
#         'end_date': leave_request.end_date,
#         'contact_address': leave_request.employee.contact_address,  # Access through the employee object
#         'days_remaining': leave_request.days_remaining(),  # Use the method here
#         'hr_approval': leave_request.leaveapproval_set.filter(approver_role__role_name='HR').first(),
#         'supervisor_approval': leave_request.leaveapproval_set.filter(approver_role__role_name='Supervisor').first(),
#         'head_approval': leave_request.leaveapproval_set.filter(approver_role__role_name='Head of Section').first(),
#     }

#     # Render the template to HTML
#     template = get_template('leave_form_pdf.html')
#     html = template.render(context)

#     # Convert HTML to PDF
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="Leave_Form_{leave_id}.pdf"'
#     pisa_status = pisa.CreatePDF(html, dest=response)

#     if pisa_status.err:
#         return HttpResponse("Error generating PDF", status=500)

#     return response

@login_required
def generate_leave_form_view(request, leave_id):
    leave_request = LeaveRequest.objects.get(id=leave_id)

    # Fetch details for the leave form
    context = {
        'name': leave_request.employee.name,
        'grade': leave_request.employee.grade,
        'post': leave_request.employee.post,
        'employment_no': leave_request.employee.employment_no,
        'bank_name': leave_request.employee.bank_name,
        'account_no': leave_request.employee.bank_account_no,
        'start_date': leave_request.start_date,
        'end_date': leave_request.end_date,
        'contact_address': leave_request.contact_address_during_leave,  # Correct field
        'days_remaining': leave_request.days_remaining(),  # Use the method here
        'hr_approval': leave_request.leaveapproval_set.filter(approver_role__role_name='HR').first(),
        'supervisor_approval': leave_request.leaveapproval_set.filter(approver_role__role_name='Supervisor').first(),
        'head_approval': leave_request.leaveapproval_set.filter(approver_role__role_name='Head of Section').first(),
    }

    # Render the template to HTML
    template = get_template('leave_form_pdf.html')
    html = template.render(context)

    # Convert HTML to PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Leave_Form_{leave_id}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    return response


from django.shortcuts import redirect
from .models import LeaveRequest, LeaveApproval, Employee

def leave_request_handler(request):
    if request.method == 'POST':
        employee_id = request.POST['employee']
        employee = Employee.objects.get(id=employee_id)
        
        # Create Leave Request
        leave_request = LeaveRequest.objects.create(
            employee=employee,
            start_date=request.POST['start_date'],
            end_date=request.POST['end_date'],
            number_of_days=request.POST['number_of_days'],
            contact_address_during_leave=request.POST.get('contact_address_during_leave', ''),
            leave_grant_requested=request.POST.get('leave_grant_requested', '')
        )
        
        # Add Approval
        approver_id = request.POST['approver']
        approver = Employee.objects.get(id=approver_id)
        approval_status = request.POST['approval_status']
        comments = request.POST.get('comments', '')
        
        LeaveApproval.objects.create(
            leave_request=leave_request,
            approver=approver,
            approver_role=approver.post,
            approval_status=approval_status,
            comments=comments
        )
        
        return redirect('hr_dashboard')  # Redirect after successful submission
    return redirect('leave_request_form')


from django.shortcuts import render
from .models import Employee, Role

def leave_request_view(request):
    employees = Employee.objects.all()  # All employees
    approvers = Employee.objects.filter(post__role_name__in=['HR', 'Supervisor', 'Head of Department'])  # Approvers
    
    return render(request, 'hr/create.html', {
        'employees': employees,
        'approvers': approvers,
    })


from django.shortcuts import render
from .models import Employee

from django.shortcuts import render
from .models import Employee

def employee_list(request):
    employees = Employee.objects.select_related('user', 'post').all()
    for employee in employees:
        employee.role_name = employee.post.role_name if employee.post else 'N/A'
    return render(request, 'hr/emp.html', {'employees': employees})


from django.shortcuts import get_object_or_404, redirect

def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    employee.user.delete()  # This will delete the user as well
    employee.delete()
    return redirect('employee_list')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Employee
from django.contrib.auth.hashers import make_password

def edit_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    if request.method == 'POST':
        employee.name = request.POST['name']
        employee.grade = request.POST['grade']
        employee.employment_no = request.POST['employment_no']
        employee.contact_address = request.POST['contact_address']
        employee.bank_name = request.POST['bank_name']
        employee.bank_account_no = request.POST['bank_account_no']

        # Change Password
        if request.POST.get('password'):
            employee.user.password = make_password(request.POST['password'])
            employee.user.save()

        employee.save()
        return redirect('employee_list')

    return render(request, 'hr/edit_employee.html', {'employee': employee})
