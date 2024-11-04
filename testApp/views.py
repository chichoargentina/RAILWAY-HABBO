from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
import requests
import random
import string

def landing(request):
    print("User has accessed the landing page.")
    return render(request, 'testApp/landing.html')

def dashboard(request):
    if request.user.is_authenticated:
        print(f"Authenticated user '{request.user.username}' accessed the dashboard.")
        return render(request, 'testApp/dashboard.html')
    else:
        print("Unauthenticated user attempted to access the dashboard. Redirecting to landing page.")
        return redirect('landing')

def register(request):
    if request.method == 'POST':
        print("Received POST request for registration.")
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            habbo_username = form.cleaned_data.get('habbo_username')
            verification_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            print(f"Generated verification code '{verification_code}' for Habbo username '{habbo_username}'.")
            
            # Store the verification code temporarily
            request.session['verification_code'] = verification_code
            request.session['habbo_username'] = habbo_username
            request.session['form_data'] = request.POST  # Store form data in session to use after verification
            
            print("Asking user to update motto with verification code. Redirecting to motto verification page.")
            return render(request, 'testApp/verify_motto.html', {'verification_code': verification_code})
        else:
            print("Form is invalid. Errors:", form.errors)
    else:
        form = CustomUserCreationForm()
        print("Rendering registration page with a blank form.")
        
    return render(request, 'testApp/register.html', {'form': form})

def verify_habbo(request):
    print("Received request to verify Habbo username and motto.")
    verification_code = request.session.get('verification_code')
    habbo_username = request.session.get('habbo_username')
    
    if verification_code and habbo_username:
        print(f"Verification code: {verification_code}, Habbo username: {habbo_username}")
        
        # Make a request to the Habbo API to check the user's motto
        api_url = f'https://www.habbo.com/api/public/users?name={habbo_username}'
        print(f"Sending GET request to {api_url}")
        
        try:
            response = requests.get(api_url)
            print("Received response from Habbo API:", response.status_code, response.text)
            
            if response.status_code == 200:
                user_data = response.json()
                print("Parsed user data from response:", user_data)
                
                # Check if the motto matches the verification code
                if user_data.get('motto') == verification_code:
                    print("Verification successful! Motto matches verification code.")
                    
                    # Retrieve form data from session and complete registration
                    form_data = request.session.get('form_data')
                    form = CustomUserCreationForm(form_data)
                    
                    if form.is_valid():
                        print("Form data is valid. Saving user.")
                        user = form.save()
                        login(request, user)
                        print(f"User '{user.username}' successfully registered and logged in.")
                        return redirect('dashboard')
                    else:
                        print("Form data is invalid upon re-validation. Errors:", form.errors)
                        return render(request, 'testApp/register.html', {'form': form, 'error': "Form data is invalid. Please try again."})
                else:
                    print("Verification failed. Motto does not match verification code.")
                    return render(request, 'testApp/verify_motto.html', {'verification_code': verification_code, 'error': "Verification failed. Please try again."})
            else:
                print(f"Failed to retrieve data from Habbo API. Status code: {response.status_code}")
                return render(request, 'testApp/verify_motto.html', {'verification_code': verification_code, 'error': "Unable to verify Habbo username. Please try again."})
        
        except requests.RequestException as e:
            print("Error occurred while trying to verify with Habbo API:", e)
            return render(request, 'testApp/verify_motto.html', {'verification_code': verification_code, 'error': "Error connecting to Habbo API. Please try again."})
    
    else:
        print("Verification code or Habbo username is missing. Redirecting to registration.")
        return redirect('register')

def custom_login(request):
    if request.method == 'POST':
        print("Received POST request for login.")
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                print(f"User '{username}' successfully logged in. Redirecting to dashboard.")
                return redirect('dashboard')
            else:
                print("Authentication failed. Invalid credentials.")
        else:
            print("Login form is invalid. Errors:", form.errors)
    else:
        form = AuthenticationForm()
        print("Rendering login page with a blank form.")
        
    return render(request, 'testApp/login.html', {'form': form})
