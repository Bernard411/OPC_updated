from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta  # Import timedelta here

class Role(models.Model):
    # Updated roles to match your requirements
    ROLE_CHOICES = [
        ('HR', 'HR'),
        ('Supervisor', 'Supervisor'),
        ('Head of Department', 'Head of Department'),
        ('Employee', 'Employee'), 
        ('System Administrator', 'System Administrator'),  # For a System Administrator with no specific role
    ]

    role_name = models.CharField(
        max_length=100, choices=ROLE_CHOICES, unique=True
    )

    def __str__(self):
        return self.get_role_name_display()


class Employee(models.Model):
    # Employee grades (no change to this part)
    GRADE_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E (P3)', 'E (P3)'),
        ('E (P4)', 'E (P4)'),
        ('F', 'F'),
        ('G', 'G'),
        ('H', 'H'),
        ('I', 'I'),
        ('J', 'J'),
        ('K', 'K'),
        ('L', 'L'),
        ('M', 'M'),
        ('N', 'N'),
        ('O', 'O'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    grade = models.CharField(max_length=10, choices=GRADE_CHOICES)
    post = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)  # Allow for employees without roles
    employment_no = models.CharField(max_length=100, unique=True)
    contact_address = models.TextField()
    bank_name = models.CharField(max_length=255)
    bank_account_no = models.CharField(max_length=100)
    annual_leave_entitlement = models.IntegerField(default=28)  # Default to 28 days
    leave_days_taken = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.get_grade_display()})"


from datetime import timedelta
from datetime import date

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('HR Approved', 'HR Approved'),
        ('Supervisor Approved', 'Supervisor Approved'),
        ('Head Approved', 'Head Approved'),
        ('Rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    contact_address_during_leave = models.TextField(blank=True, null=True)
    leave_grant_requested = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    submission_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # You can keep this if you still need it

    def __str__(self):
        return f"LeaveRequest ({self.employee.name}, {self.status})"

    def calculate_leave_days(self):
        """Calculate the leave days excluding weekends (Saturday & Sunday)."""
        current_date = self.start_date
        total_days = 0

        while current_date <= self.end_date:
            # Weekdays are 0-4 (Monday to Friday)
            if current_date.weekday() < 5:
                total_days += 1
            current_date += timedelta(days=1)  # Increment the date by one day
        
        return total_days

    def days_remaining(self):
        """Calculate remaining leave days based on employee's leave entitlement and leave taken."""
        leave_taken = self.calculate_leave_days()  # Get the leave days based on start and end date
        return self.employee.annual_leave_entitlement - self.employee.leave_days_taken - leave_taken

 


        

    def countdown(self):
        today = date.today()  # Calculate today's date once for use
        if not self.end_date:
            return "No end date set for this leave request"
        
        if today > self.end_date:
            return "Leave Expired"
        else:
            remaining_days = (self.end_date - today).days
            return f"{remaining_days} days remaining until leave expires"




# Update employee's leave days taken when leave is approved
class LeaveApproval(models.Model):
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE)
    approver = models.ForeignKey(Employee, on_delete=models.CASCADE)
    approver_role = models.ForeignKey(Role, on_delete=models.CASCADE)
    approval_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )
    comments = models.TextField(blank=True)
    action_date = models.DateTimeField(auto_now=True)
    signature = models.ImageField(upload_to='signatures/', blank=True, null=True)

    def __str__(self):
        return f"Approval ({self.leave_request}, {self.approver})"

    def save(self, *args, **kwargs):
        # Update the leave days taken for the employee when the leave is approved
        if self.approval_status == 'Approved':
            leave_request = self.leave_request
            leave_days = leave_request.calculate_leave_days()
            employee = leave_request.employee
            employee.leave_days_taken += leave_days
            employee.save()
        
        super().save(*args, **kwargs)

