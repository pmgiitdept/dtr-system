from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from .models import CustomUser, Settings

User = get_user_model()

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class EditAccountForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'user_type', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class AddAccountForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'user_type', 'is_active', 'password1', 'password2']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class GeneralSettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['theme_mode', 'font_size', 'layout_spacing']

class UserManagementForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    is_active = forms.BooleanField(required=False)

class FileManagementForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['max_upload_files', 'max_file_size_mb', 'allowed_file_extensions', 'retention_days', 'enable_auto_delete']

class EmailSettingsForm(forms.ModelForm):
    smtp_password = forms.CharField(
        label="SMTP Password",
        widget=forms.PasswordInput(render_value=True),
        required=False,
    )
    test_email = forms.EmailField(
        label="Send test email to",
        required=False,
        help_text="Enter an email to send a test message."
    )
    action = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Settings
        fields = ['email_host', 'email_port', 'email_host_user', 'email_host_password']
        labels = {
            'email_host': 'SMTP Server',
            'email_port': 'SMTP Port',
            'email_host_user': 'SMTP Username',
            'email_host_password': 'SMTP Password',
        }

class SecuritySettingsForm(forms.Form):
    require_2fa = forms.BooleanField(label="Require Two-Factor Authentication", required=False)
    password_expiry_days = forms.IntegerField(label="Password Expiry (Days)", min_value=0, required=False)
    lockout_threshold = forms.IntegerField(label="Account Lockout Threshold (failed attempts)", min_value=0, required=False)

class BackupRestoreForm(forms.Form):
    action = forms.CharField(widget=forms.HiddenInput())
    restore_file = forms.FileField(label="Restore from Backup File", required=False)