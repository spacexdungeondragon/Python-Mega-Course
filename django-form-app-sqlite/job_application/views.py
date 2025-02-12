from django.shortcuts import render
from .forms import ApplicationForm
from .models import Form
from django.contrib import messages
from django.core.mail import EmailMessage

def index(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            date = form.cleaned_data["date"]
            occupation = form.cleaned_data["occupation"]
            
            Form.objects.create(first_name=first_name, last_name=last_name, email=email, date=date, occupation=occupation)
            
            message_body = f"""Hello {first_name},

            Thank you for your submission!

            Here are the details you submitted:
            First Name: {first_name}
            Last Name: {last_name}
            Date: {date}

            Thank you!"""

            email_message = EmailMessage("Form Submission Confirmation", message_body, to=[email])
            email_message.send()


            messages.success(request, "Form submitted successfully!")

            # Add debug prints
            print("Messages after adding success message:")
            for message in messages.get_messages(request):
                print(f"Message: {message}")
                print(f"Message Level: {message.level}")
                print(f"Message Tags: {message.tags}")

    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

