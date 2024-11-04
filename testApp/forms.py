from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
import re

class CustomUserCreationForm(UserCreationForm):
    habbo_username = forms.CharField(max_length=100)
    birthday = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'habbo_username', 'birthday')

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if len(password1) < 6 or not re.match("^[a-zA-Z0-9]*$", password1):
            raise forms.ValidationError("Password must be at least 6 alphanumeric characters.")
        return password1
