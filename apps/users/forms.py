from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import CustomUser

HOUSE_CHOICES = [
    ('gryffindor', 'Gryffindor'),
    ('hufflepuff', 'Hufflepuff'),
    ('ravenclaw', 'Ravenclaw'),
    ('slytherin', 'Slytherin'),
]

# LOGIN OPTIONS

class StudentRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'maxlength': 4}),
        min_length=4,
        label="Llave (PIN de 4 dígitos):"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'maxlength': 4}),
        min_length=4,
        label="Confirma tu llave:"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'full_name', 'house', 'password']
        labels = {
            'username': "Usuario",
            'full_name': "Nombre Mágico",
            'house': "Casa de Hogwarts",
        }
        widgets = {
            'house': forms.Select(choices=HOUSE_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            field.required = True

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if " " in username:
            raise forms.ValidationError(
                "El nombre de usuario no debe contener espacios.")

        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "Este nombre de usuario ya está en uso.")

        return username

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if CustomUser.objects.filter(full_name=full_name).exists():
            raise forms.ValidationError(
                "Este nombre mágico ya está registrado.")
        return full_name

    def clean(self):
        cleaned_data = super().clean()

        password = self.cleaned_data.get('password')
        confirm = self.cleaned_data.get('confirm_password')

        if not password.isdigit() or not confirm.isdigit():
            raise forms.ValidationError("La llave debe contener solo números.")

        if password and confirm and password != confirm:
            self.add_error("confirm_password", "Las llaves no coinciden.")

        return cleaned_data


class StudentLoginForm(forms.Form):
    username = forms.CharField(label="Nombre de usuario", max_length=150)
    password = forms.CharField(label="Llave", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# PROFILE OPTIONS

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'full_name']
        
        labels = {
            'username': "Usuario",
            'full_name': "Nombre Mágico",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if " " in username:
            raise forms.ValidationError("El nombre de usuario no debe contener espacios.")
            
        if CustomUser.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso por otro estudiante.")
            
        return username

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')

        if CustomUser.objects.filter(full_name=full_name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este nombre mágico ya está registrado por otra persona.")
            
        return full_name

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Llave actual",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label="Nueva llave",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Nueva contraseña'})
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Confirmar nueva contraseña'})
    )


# USER CREATION AS ADMIN

class AdminUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'role', 'is_staff', 'house', 'password']
