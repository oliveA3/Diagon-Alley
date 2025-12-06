from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import CustomUser

HOUSE_CHOICES = [
    ('gryffindor', 'Gryffindor'),
    ('hufflepuff', 'Hufflepuff'),
    ('ravenclaw', 'Ravenclaw'),
    ('slytherin', 'Slytherin'),
]


class StudentRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'maxlength': 4}),
        max_length=4,
        min_length=4,
        label="Llave (PIN de 4 dígitos):"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'full_name', 'house', 'password']
        widgets = {
            'house': forms.Select(choices=HOUSE_CHOICES),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

    def clean_pin(self):
        pin = self.cleaned_data.get('password')
        if not pin.isdigit():
            raise forms.ValidationError("El PIN debe contener solo números.")
        return pin
    

class StudentLoginForm(forms.Form):
    username = forms.CharField(label="Nombre de usuario", max_length=150)
    password = forms.CharField(label="Llave", widget=forms.PasswordInput)
    

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Contraseña actual",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Contraseña actual'})
    )
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Nueva contraseña'})
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Confirmar nueva contraseña'})
    )

class AdminUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'role', 'is_staff', 'house', 'password']
