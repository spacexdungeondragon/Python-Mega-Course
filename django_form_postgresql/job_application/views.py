from django.shortcuts import render
from .forms import ApplicationForm
from .models import JobApplication
from django.contrib import messages

def index(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Application submitted successfully!")
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')