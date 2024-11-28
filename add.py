import os
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OPC.settings")
django.setup()

from core.models import Role

# List of roles to be added to the Role model
roles = [
    ('A', 'Chief Secretary, Chief Justice'),
    ('B', 'Deputy Chief Secretary, Secretary to Treasury'),
    ('C', 'Principal Secretary'),
    ('D', 'Director'),
    ('E (P3)', 'Deputy Director (P3)'),
    ('E (P4)', 'Deputy Director (P4)'),
    ('F', 'Head of Section (Chief Accountant, Chief HR Officer)'),
    ('G', 'Principal Accountant, Principal HR Officer'),
    ('H', 'Senior Officer'),
    ('I', 'Officer'),
    ('J', 'Senior Assistant Officer'),
    ('K', 'Assistant Officer'),
    ('L', 'Senior Clerk'),
    ('M', 'Clerk'),
    ('N', 'Driver, Cleaner'),
    ('O', 'Driver, Cleaner'),
]

# Adding roles to the Role model
for role_code, role_name in roles:
    role, created = Role.objects.get_or_create(role_name=role_name)
    if created:
        print(f"Added role: {role_name} ({role_code})")
    else:
        print(f"Role {role_name} ({role_code}) already exists")

print("All roles added!")
