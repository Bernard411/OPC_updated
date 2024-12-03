from django.shortcuts import render, redirect
from django.contrib import messages
from .models import LeaveRequest, Employee
from django.contrib.auth.decorators import login_required

@login_required
def home_admin(request):
    return render(request, 'admin_z/index.html')