from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()  # Récupère le modèle User utilisé dans le projet

class AuthForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User  # Utilisation correcte du modèle User
        fields = ["username", "email", "password1", "password2"]