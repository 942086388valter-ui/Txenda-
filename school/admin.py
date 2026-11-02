from django.contrib import admin
from .models import Student,Teacher,Grade,ClassGroup,Subject,Enrollment,Attendance
admin.site.register([Student,Teacher,Grade,ClassGroup,Subject,Enrollment,Attendance])


from .models import InstitutionSettings, AuditLog
admin.site.register(InstitutionSettings)
admin.site.register(AuditLog)
