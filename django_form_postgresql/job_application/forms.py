from django import forms
from .models import JobApplication

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['first_name', 'last_name', 'email', 'date', 'occupation']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'occupation': forms.Select(attrs={'class': 'form-control'},
                                    choices=[
                                        ('employed', 'Employed'),
                                        ('unemployed', 'Unemployed'),
                                        ('self-employed', 'Self-employed'),
                                        ('student', 'Student')
                                    ])
        }