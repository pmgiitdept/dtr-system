from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from .forms import LoginForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django import forms
from .forms import EditAccountForm, AddAccountForm, GeneralSettingsForm, FileManagementForm, EmailSettingsForm, SecuritySettingsForm, BackupRestoreForm
from .models import CustomUser, Settings, AuditLog, SystemLog, BackupLog
from django.contrib import messages
from core.models import ExcelUpload
from django.http import JsonResponse
from .models import UserSession  
from .utils.backup_utils import run_backup, run_restore
import os
from django.conf import settings
import datetime
import subprocess
from django.db.models import Q
from django.http import FileResponse, Http404
from django.core.paginator import Paginator
from django.core.mail import send_mail, BadHeaderError
import requests
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

User = get_user_model()
AI_SERVICE_URL = "http://127.0.0.1:8001"  

@login_required
def user_info_api(request, user_id):
    from core.models import ExcelUpload
    uploads = ExcelUpload.objects.filter(user_id=user_id).order_by('-uploaded_at')
    data = [
        {"filename": u.file.name.split('/')[-1], "uploaded_at": u.uploaded_at.strftime('%Y-%m-%d %H:%M')}
        for u in uploads
    ]
    return JsonResponse({"uploads": data})

# -------------------- AI --------------------
def ask_ai(query, session_id, user_id):
    """
    Call the FastAPI AI service and return the response.
    """
    try:
        response = requests.post(
            f"{AI_SERVICE_URL}/ask",
            json={
                "user_input": query,
                "session_id": session_id,
                "user_id": user_id
            },
            timeout=60 
        )
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        return {"response": "⚠ AI service timed out. Try again later."}
    except requests.RequestException as e:
        return {"response": f"⚠ AI service request failed: {e}"}

@login_required
def ai_assistant(request):
    """
    Render AI assistant page. Optionally handle form-based queries.
    """
    response_data = None
    if request.method == "POST":
        query = request.POST.get("query")
        session_id = str(request.user.id)
        user_id = str(request.user.id)

        response_data = ask_ai(query, session_id, user_id)

    return render(request, "core/ai_assistant.html", {"response": response_data})

@login_required
@csrf_exempt
def ai_query_stream(request):
    """
    SSE endpoint to stream AI responses from FastAPI to browser.
    """
    if request.method != "GET":
        return JsonResponse({"reply": "Invalid request method"}, status=400)

    import requests
    from django.http import StreamingHttpResponse

    session_id = str(request.user.id)
    user_id = str(request.user.id)
    question = request.GET.get("question", "")

    if not question:
        return JsonResponse({"reply": "No question provided"}, status=400)

    fastapi_url = f"{AI_SERVICE_URL}/ask_stream?session_id={session_id}&user_id={user_id}&question={question}"

    def stream_generator():
        try:
            with requests.get(fastapi_url, stream=True) as r:
                for line in r.iter_lines():
                    if line:
                        yield f"data: {line.decode('utf-8')}\n\n"
        except Exception as e:
            yield f'data: {{"text":"⚠ Stream error: {str(e)}"}}\n\n'

    response = StreamingHttpResponse(stream_generator(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response

@login_required
@csrf_exempt
def upload_file(request):
    """
    Upload file to FastAPI background processor, save locally, and save DB record.
    """
    if request.method == "POST":
        file = request.FILES.get("file")
        if not file:
            return JsonResponse({"success": False, "error": "No file provided."})

        try:
            user_folder = os.path.join(settings.MEDIA_ROOT, "uploads", str(request.user.id))
            os.makedirs(user_folder, exist_ok=True)
            file_path = os.path.join(user_folder, file.name)

            with open(file_path, "wb") as f:
                for chunk in file.chunks():
                    f.write(chunk)

            ExcelUpload.objects.create(
                uploaded_by=request.user,
                original_filename=file.name,
                file=f"uploads/{request.user.id}/{file.name}",
                uploaded_at=timezone.now()
            )

            files = {"file": (file.name, open(file_path, "rb"))}
            data = {"session_id": str(request.user.id), "user_id": str(request.user.id)}

            resp = requests.post(
                f"{AI_SERVICE_URL}/upload",
                files=files,
                data=data,
                timeout=120
            )
            resp.raise_for_status()
            return JsonResponse(resp.json())

        except requests.Timeout:
            return JsonResponse({"success": False, "error": "AI service timed out."})
        except requests.RequestException as e:
            return JsonResponse({"success": False, "error": f"AI service request failed: {e}"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

@login_required
@csrf_exempt
def generate_chart(request):
    """
    Call FastAPI /chart endpoint to generate a chart from uploaded files.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_input = data.get("user_input", "")
            session_id = str(request.user.id)
            user_id = str(request.user.id)

            resp = requests.post(
                f"{AI_SERVICE_URL}/chart",
                json={
                    "user_input": user_input,
                    "session_id": session_id,
                    "user_id": user_id
                },
                timeout=120 
            )
            resp.raise_for_status()
            return JsonResponse(resp.json())

        except requests.Timeout:
            return JsonResponse({"error": "⚠ Chart generation timed out."})
        except requests.RequestException as e:
            return JsonResponse({"error": f"⚠ Chart generation request failed: {e}"})
        except Exception as e:
            return JsonResponse({"error": f"⚠ Server error: {e}"})
    return JsonResponse({"error": "Invalid request method"})

# -------------------- Admin check --------------------
def is_admin(user):
    return user.is_authenticated and user.user_type == 'admin'

@user_passes_test(is_admin, login_url='login')
def admin_settings(request):
    section = request.GET.get("section", "general")  

    if request.method == "POST":
        if section == "general":
            messages.success(request, "General settings updated successfully.")
        elif section == "file":
            messages.success(request, "File management settings saved.")
        elif section == "users":
            messages.success(request, "User management updated.")
        elif section == "audit":
            messages.info(request, "Audit log viewed.")

    return render(request, "accounts/admin_settings.html", {"section": section})

@login_required
@user_passes_test(is_admin)
def accounts_list(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'accounts/accounts_list.html', {'accounts': users})

def login_view(request):
    if request.user.is_authenticated:
        return redirect_dashboard(request)

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect_dashboard(request)
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def redirect_dashboard(request):
    if request.user.user_type == 'admin':
        return redirect('admin_dashboard')
    else:
        return redirect('client_dashboard')

def logout_view(request):
    logout(request)
    return redirect('login')

def edit_account(request, user_id):
    account = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = EditAccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Account updated successfully!")
            return redirect('accounts_list')
        else:
            messages.error(request, "⚠️ Please correct the errors below.")
    else:
        form = EditAccountForm(instance=account)

    return render(request, 'accounts/edit_account.html', {'form': form, 'account': account})

def delete_account(request, account_id):
    account = get_object_or_404(CustomUser, id=account_id)
    if request.method == 'POST':
        account.delete()
        messages.success(request, "Account deleted successfully.")
    return redirect('accounts_list')

@login_required
@user_passes_test(is_admin)
def add_account(request):
    if request.method == 'POST':
        form = AddAccountForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            if user.user_type == 'admin':
                user.is_staff = True
                user.is_superuser = True
            else:
                user.is_staff = False
                user.is_superuser = False

            user.save()
            messages.success(request, "Account created successfully.")
            return redirect('accounts_list')
        else:
            messages.error(request, "Please correct the errors below.")
            print(form.errors) 
    else:
        form = AddAccountForm()

    return render(request, 'accounts/add_account.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def user_info_api(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    uploads = ExcelUpload.objects.filter(uploaded_by=user).order_by('-uploaded_at')  
    
    uploads_data = [
        {'filename': f.original_filename, 'uploaded_at': f.uploaded_at.strftime('%Y-%m-%d %H:%M')}
        for f in uploads
    ]

    data = {
        'username': user.username,
        'email': user.email,
        'user_type': user.user_type,
        'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M'),
        'uploads': uploads_data,
    }
    return JsonResponse(data)

@login_required
@user_passes_test(is_admin)
def transaction_history(request):
    uploads = ExcelUpload.objects.select_related('uploaded_by').order_by('-uploaded_at')

    sessions = UserSession.objects.select_related('user').order_by('-login_time')

    context = {
        'uploads': uploads,
        'sessions': sessions,
    }
    return render(request, 'accounts/transaction_history.html', context)

@login_required
def admin_settings(request):
    section = request.GET.get("section", "general")

    settings_instance, _ = Settings.objects.get_or_create(id=1)

    general_form = GeneralSettingsForm(instance=settings_instance)
    try:
        security_form = SecuritySettingsForm(instance=settings_instance)
    except TypeError:
        security_form = SecuritySettingsForm()

    try:
        file_form = FileManagementForm(instance=settings_instance)
    except TypeError:
        file_form = FileManagementForm()

    email_form = EmailSettingsForm()
    backup_form = BackupRestoreForm()

    audit_logs = AuditLog.objects.all().order_by("-timestamp")[:50]

    activity_logs = AuditLog.objects.all().order_by("-timestamp")

    uploaded_files = ExcelUpload.objects.all().order_by('-uploaded_at')
    if request.method == "POST":
        if section == "general":
            form = GeneralSettingsForm(request.POST, instance=settings_instance)
            if form.is_valid():
                form.save()
                AuditLog.objects.create(action="Updated General Settings", user=request.user)
                return redirect(f"{request.path}?section=general")

        elif section == "security":
            try:
                form = SecuritySettingsForm(request.POST, instance=settings_instance)
            except TypeError:
                form = SecuritySettingsForm(request.POST)

            if form.is_valid():
                if hasattr(form, "save"):
                    form.save()
                AuditLog.objects.create(action="Updated Security Settings", user=request.user)
                return redirect(f"{request.path}?section=security")

        elif section == "file":
            try:
                form = FileManagementForm(request.POST, instance=settings_instance)
            except TypeError:
                form = FileManagementForm(request.POST)

            if form.is_valid():
                if hasattr(form, "save"):
                    form.save()
                AuditLog.objects.create(action="Updated File Management Settings", user=request.user)
                return redirect(f"{request.path}?section=file")

        elif section == "email":
            form = EmailSettingsForm(request.POST, instance=settings_instance)
            if form.is_valid():
                action = form.cleaned_data.get("action")
                if action == "save":
                    form.save()
                    AuditLog.objects.create(action="Updated Email Settings", user=request.user)
                    messages.success(request, "Email settings saved successfully.")
                    return redirect(f"{request.path}?section=email")
                elif action == "test":
                    test_email = form.cleaned_data.get("test_email")
                    if test_email:
                        from django.conf import settings as django_settings
                        original_email_host = django_settings.EMAIL_HOST
                        original_email_port = django_settings.EMAIL_PORT
                        original_email_host_user = django_settings.EMAIL_HOST_USER
                        original_email_host_password = django_settings.EMAIL_HOST_PASSWORD
                        original_email_use_tls = django_settings.EMAIL_USE_TLS

                        try:
                            django_settings.EMAIL_HOST = form.cleaned_data['email_host']
                            django_settings.EMAIL_PORT = form.cleaned_data['email_port']
                            django_settings.EMAIL_HOST_USER = form.cleaned_data['email_host_user']
                            django_settings.EMAIL_HOST_PASSWORD = form.cleaned_data['email_host_password']
                            django_settings.EMAIL_USE_TLS = True 

                            send_mail(
                                subject="Test Email from Admin Settings",
                                message="This is a test email to verify SMTP settings.",
                                from_email=django_settings.EMAIL_HOST_USER,
                                recipient_list=[test_email],
                                fail_silently=False,
                            )
                            messages.success(request, f"Test email sent successfully to {test_email}.")
                            AuditLog.objects.create(action=f"Sent test email to {test_email}", user=request.user)
                        except BadHeaderError:
                            messages.error(request, "Invalid header found.")
                        except Exception as e:
                            messages.error(request, f"Failed to send test email: {str(e)}")
                        finally:
                            django_settings.EMAIL_HOST = original_email_host
                            django_settings.EMAIL_PORT = original_email_port
                            django_settings.EMAIL_HOST_USER = original_email_host_user
                            django_settings.EMAIL_HOST_PASSWORD = original_email_host_password
                            django_settings.EMAIL_USE_TLS = original_email_use_tls

                    else:
                        messages.error(request, "Please provide an email address to send the test email.")
                else:
                    form = EmailSettingsForm(instance=settings_instance)

        elif section == "backup":
            form = BackupRestoreForm(request.POST, request.FILES)
            if form.is_valid():
                action = form.cleaned_data.get("action")
                if action == "backup":
                    backup_file_path = run_backup()
                    backup_file_name = os.path.basename(backup_file_path)
                    AuditLog.objects.create(action=f"Performed system backup: {backup_file_name}", user=request.user)
                elif action == "restore":
                    backup_file = request.FILES.get("restore_file")
                    if backup_file:
                        temp_path = os.path.join(settings.BASE_DIR, "backups", backup_file.name)
                        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                        with open(temp_path, "wb+") as destination:
                            for chunk in backup_file.chunks():
                                destination.write(chunk)
                        run_restore(temp_path)
                        AuditLog.objects.create(
                            action=f"Restored system from {backup_file.name}",
                            user=request.user
                        )
                return redirect(f"{request.path}?section=backup")

    backup_logs = AuditLog.objects.filter(
        Q(action__icontains="backup") | Q(action__icontains="restore")
    ).order_by("-timestamp")[:20]

    context = {
        "section": section,
        "general_form": general_form,
        "security_form": security_form,
        "file_form": file_form,
        "email_form": email_form,
        "backup_form": backup_form,
        "audit_logs": audit_logs,
        "backup_logs": backup_logs,
        "audit_logs": audit_logs,
        "uploaded_files": uploaded_files,
    }
    return render(request, "accounts/admin_settings.html", context)

@login_required
def download_backup(request, filename):
    if ".." in filename or filename.startswith("/"):
        raise Http404("Invalid file path")

    backup_dir = os.path.join(settings.BASE_DIR, "backups")
    file_path = os.path.join(backup_dir, filename)

    if not os.path.exists(file_path):
        raise Http404("File does not exist")

    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
    return 

@login_required
def client_side_view(request):
    return render(request, "accounts/client_side.html")

@login_required
def delete_uploaded_file(request, file_id):
    file_obj = get_object_or_404(ExcelUpload, id=file_id)
    file_obj.file.delete() 
    file_obj.delete()    
    messages.success(request, "File deleted successfully.")
    return redirect('/accounts/admin-settings/?section=file')