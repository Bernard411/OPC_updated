from django import forms
from django.contrib.auth.models import User
from .models import Employee, Role

class RegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    name = forms.CharField(max_length=255, required=True)
    grade = forms.ChoiceField(choices=Employee.GRADE_CHOICES, required=True)
    role = forms.ChoiceField(choices=[(role.role_name, role.role_name) for role in Role.objects.all()], required=True)
    employment_no = forms.CharField(max_length=100, required=True)
    contact_address = forms.CharField(widget=forms.Textarea, required=True)
    bank_name = forms.CharField(max_length=255, required=True)
    bank_account_no = forms.CharField(max_length=100, required=True)
    annual_leave_entitlement = forms.IntegerField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

# forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

class EmailAuthenticationForm(AuthenticationForm):
    email = forms.EmailField(label='Email', max_length=254)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            # Check if email exists in the User model
            user = User.objects.get(email=email)
            return email
        except User.DoesNotExist:
            raise forms.ValidationError("This email is not registered.")
