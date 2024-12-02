from django.db import models
from django.contrib.auth.models import User

class Role(models.Model):
    # Updated roles to match your requirements
    ROLE_CHOICES = [
        ('HR', 'HR'),
        ('Supervisor', 'Supervisor'),
        ('Head of Department', 'Head of Department'),
        ('Employee', 'Employee'),  # For an employee with no specific role
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
    annual_leave_entitlement = models.IntegerField()
    leave_days_taken = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.get_grade_display()})"



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
    number_of_days = models.IntegerField()
    contact_address_during_leave = models.TextField(blank=True, null=True)
    leave_grant_requested = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    submission_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # You can keep this if you still need it

    def __str__(self):
        return f"LeaveRequest ({self.employee.name}, {self.status})"
    
    # Method to calculate remaining leave days
    def days_remaining(self):
        # Calculate the remaining days based on annual leave entitlement and days taken
        return self.employee.annual_leave_entitlement - self.employee.leave_days_taken - self.number_of_days


class LeaveApproval(models.Model):
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE)
    approver = models.ForeignKey(Employee, on_delete=models.CASCADE)
    approver_role = models.ForeignKey(Role, on_delete=models.CASCADE)
    approval_status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected'),
        ],
        default='Pending'
    )
    comments = models.TextField(blank=True)
    action_date = models.DateTimeField(auto_now=True)
    signature = models.ImageField(upload_to='signatures/', blank=True, null=True)  # Optional: Image signature
    is_signed = models.BooleanField(default=False)  # Tracks if the form is signed


    def __str__(self):
        return f"Approval ({self.leave_request}, {self.approver})"
