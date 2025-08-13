from django.db import models
from django.conf import settings

class ExcelUpload(models.Model):
    file = models.FileField(upload_to='uploads/')
    original_filename = models.CharField(max_length=255)
    
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploads_by_user',
        null=True, blank=True
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploads_for_client',
        null=True, blank=True
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

class DTRRecord(models.Model):
    upload = models.ForeignKey(ExcelUpload, on_delete=models.CASCADE, related_name='records')
    
    sheet_name = models.CharField(max_length=100, null=True, blank=True)  # 👈 ADD THIS

    employee_code = models.CharField(max_length=50)
    employee_name = models.CharField(max_length=100)
    
    total_hours = models.FloatField(null=True, blank=True)
    nd_reg_hours = models.FloatField(null=True, blank=True)
    absences = models.FloatField(null=True, blank=True)
    tardiness = models.FloatField(null=True, blank=True)
    undertime = models.FloatField(null=True, blank=True)
    
    ot_regular = models.FloatField(null=True, blank=True)
    nd_ot_reg = models.FloatField(null=True, blank=True)
    ot_restday = models.FloatField(null=True, blank=True)
    nd_restday = models.FloatField(null=True, blank=True)
    ot_rest_excess = models.FloatField(null=True, blank=True)
    nd_rest_excess = models.FloatField(null=True, blank=True)
    
    ot_special_holiday = models.FloatField(null=True, blank=True)
    nd_special_holiday = models.FloatField(null=True, blank=True)
    ot_sh_excess = models.FloatField(null=True, blank=True)
    nd_sh_excess = models.FloatField(null=True, blank=True)
    
    ot_legal_holiday = models.FloatField(null=True, blank=True)
    special_holiday = models.FloatField(null=True, blank=True)
    ot_legal_excess = models.FloatField(null=True, blank=True)
    nd_legal_excess = models.FloatField(null=True, blank=True)
    
    ot_sh_rest = models.FloatField(null=True, blank=True)
    nd_sh_rest = models.FloatField(null=True, blank=True)
    ot_sh_rest_excess = models.FloatField(null=True, blank=True)
    nd_sh_rest_excess = models.FloatField(null=True, blank=True)
    
    legal_rest = models.FloatField(null=True, blank=True)
    nd_legal_rest = models.FloatField(null=True, blank=True)
    ot_legal_rest_excess = models.FloatField(null=True, blank=True)
    nd_legal_rest_excess = models.FloatField(null=True, blank=True)
    
    vac_leave_applied = models.FloatField(null=True, blank=True)
    sick_leave_applied = models.FloatField(null=True, blank=True)
    backpay_vl = models.FloatField(null=True, blank=True)
    backpay_sl = models.FloatField(null=True, blank=True)
    
    ot_regular_excess = models.FloatField(null=True, blank=True)
    nd_ot_reg_excess = models.FloatField(null=True, blank=True)
    
    legal_holiday = models.FloatField(null=True, blank=True)
    nd_legal_holiday = models.FloatField(null=True, blank=True)
    overnight_rate = models.FloatField(null=True, blank=True)
    
    project = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.employee_name} ({self.employee_code})"

class Sheet2Record(models.Model):
    upload = models.ForeignKey(ExcelUpload, on_delete=models.CASCADE)
    sheet_name = models.CharField(max_length=255)
    col_a = models.CharField(max_length=255, null=True, blank=True)
    col_b = models.CharField(max_length=255, null=True, blank=True)
    col_c = models.CharField(max_length=255, null=True, blank=True)
    
# For Sheet 3
class ProjectManpowerRecord(models.Model):
    upload = models.ForeignKey(ExcelUpload, on_delete=models.CASCADE)
    sheet_name = models.CharField(max_length=100)
    project = models.CharField(max_length=255)
    supervisor = models.CharField(max_length=255, blank=True, null=True)
    tl = models.CharField(max_length=255, blank=True, null=True)
    messenger = models.CharField(max_length=255, blank=True, null=True)
    hk = models.CharField(max_length=255, blank=True, null=True)
    gnl = models.CharField("G&L", max_length=255, blank=True, null=True)
    day_off_reliever = models.CharField(max_length=255, blank=True, null=True)
    aa = models.CharField(max_length=255, blank=True, null=True)
    electrician = models.CharField(max_length=255, blank=True, null=True)
    plumber = models.CharField(max_length=255, blank=True, null=True)
    driver = models.CharField(max_length=255, blank=True, null=True)
    total = models.IntegerField(blank=True, null=True)

# For Sheet 4
class ProjectListRecord(models.Model):
    upload = models.ForeignKey(ExcelUpload, on_delete=models.CASCADE)
    sheet_name = models.CharField(max_length=100)
    project = models.CharField(max_length=255)
