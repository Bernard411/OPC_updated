# import os
# import django

# # Setup Django environment
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OPC.settings")
# django.setup()

# from core.models import Role

# # List of roles to be added to the Role model
# roles = [
#     ('A', 'Chief Secretary, Chief Justice'),
#     ('B', 'Deputy Chief Secretary, Secretary to Treasury'),
#     ('C', 'Principal Secretary'),
#     ('D', 'Director'),
#     ('E (P3)', 'Deputy Director (P3)'),
#     ('E (P4)', 'Deputy Director (P4)'),
#     ('F', 'Head of Section (Chief Accountant, Chief HR Officer)'),
#     ('G', 'Principal Accountant, Principal HR Officer'),
#     ('H', 'Senior Officer'),
#     ('I', 'Officer'),
#     ('J', 'Senior Assistant Officer'),
#     ('K', 'Assistant Officer'),
#     ('L', 'Senior Clerk'),
#     ('M', 'Clerk'),
#     ('N', 'Driver, Cleaner'),
#     ('O', 'Driver, Cleaner'),
# ]

# # Adding roles to the Role model
# for role_code, role_name in roles:
#     role, created = Role.objects.get_or_create(role_name=role_name)
#     if created:
#         print(f"Added role: {role_name} ({role_code})")
#     else:
#         print(f"Role {role_name} ({role_code}) already exists")

# print("All roles added!")

import os
import random
from datetime import datetime, timedelta

import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OPC.settings")
django.setup()

from core.models import Role, Employee, LeaveRequest
from django.contrib.auth.models import User

# List of Malawian names
names = [
    "Chikondi Banda", "Thandiwe Chirwa", "Blessings Kamanga", "Limbani Mvula",
    "Tadala Moyo", "Lusekelo Phiri", "Yamikani Mwale", "Madalitso Kunda",
    "Tiwonge Nkosi", "Zikomo Chisi", "Tamanda Gondwe", "Kondwani Ngwira",
    "Mphatso Tembo", "Chisomo Chimaliro", "Kondwani Zimba", "Loveness Kaunda",
    "Tiyamike Jere", "Dalitso Nyirenda", "Mirriam Mkandawire", "Onjezani Kalua"
]

# List of roles for assignment
roles = list(Role.objects.all())

# Employee grades
grades = ['A', 'B', 'C', 'D', 'E (P3)', 'E (P4)', 'F', 'G', 'H', 'I']

# Helper function to generate random leave requests
def generate_random_leave_dates():
    start_date = datetime.now() + timedelta(days=random.randint(1, 30))
    number_of_days = random.randint(2, 15)
    end_date = start_date + timedelta(days=number_of_days)
    return start_date.date(), end_date.date(), number_of_days

# Adding employees and leave requests
for i, name in enumerate(names, start=1):
    # Create a User for the employee
    username = name.lower().replace(" ", ".")
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"first_name": name.split()[0], "last_name": name.split()[1], "email": f"{username}@opc.mw"}
    )

    # Assign random role and grade
    role = random.choice(roles)
    grade = random.choice(grades)

    # Create Employee instance
    employee, created = Employee.objects.get_or_create(
        user=user,
        defaults={
            "name": name,
            "grade": grade,
            "post": role,
            "employment_no": f"EMP{i:03}",
            "contact_address": f"Address for {name}",
            "bank_name": f"Bank of Malawi",
            "bank_account_no": f"10293847{i}",
            "annual_leave_entitlement": 30,
            "leave_days_taken": random.randint(0, 15),
        }
    )

    # Generate a leave request for this employee
    start_date, end_date, number_of_days = generate_random_leave_dates()
    LeaveRequest.objects.create(
        employee=employee,
        start_date=start_date,
        end_date=end_date,
        number_of_days=number_of_days,
        contact_address_during_leave=f"Leave Address for {name}",
        leave_grant_requested="Annual Leave",
        status=random.choice(['Pending', 'HR Approved', 'Supervisor Approved', 'Head Approved', 'Rejected'])
    )

    print(f"Added employee {name} and a leave request.")

print("All employees and leave requests added!")
