from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('client', 'Client'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='client')

    def __str__(self):
        return f"{self.username} ({self.user_type})"

class UserSession(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} logged in at {self.login_time}"
    
class Settings(models.Model):
    site_name = models.CharField(max_length=255, default="PMG Time Central")
    theme_mode = models.CharField(max_length=10, choices=[('light', 'Light'), ('dark', 'Dark')], default='light')
    font_size = models.CharField(max_length=10, choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')], default='medium')
    layout_spacing = models.CharField(max_length=50, default='normal')

    max_upload_files = models.IntegerField(default=5)
    max_file_size_mb = models.IntegerField(default=20)
    allowed_file_extensions = models.CharField(max_length=255, default="pdf,docx,xlsx")
    retention_days = models.IntegerField(default=30)
    enable_auto_delete = models.BooleanField(default=False)

    email_host = models.CharField(max_length=255, default="smtp.example.com")
    email_port = models.IntegerField(default=587)
    email_use_tls = models.BooleanField(default=True)
    email_host_user = models.CharField(max_length=255, blank=True, null=True)
    email_host_password = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"Settings (Theme: {self.theme_mode}, Font: {self.font_size})"

class AuditLog(models.Model):
    action = models.CharField(max_length=255)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} - {self.user.username}"
    
class SystemLog(models.Model):
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp} - {self.action}"
    
class BackupLog(models.Model):
    ACTION_CHOICES = [
        ("Backup", "Backup"),
        ("Restore", "Restore"),
    ]
    action = models.CharField(max_length=255, choices=ACTION_CHOICES)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} - {self.action} by {self.user.username}"