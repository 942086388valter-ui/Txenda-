from django.urls import path
from . import views
urlpatterns=[path("",views.dashboard,name="dashboard"),path("estudantes/",views.students,name="students"),path("professores/",views.teachers,name="teachers"),path("notas/",views.grades,name="grades"),path("turmas/",views.classes,name="classes"),path("disciplinas/",views.subjects,name="subjects"),path("matriculas/",views.enrollments,name="enrollments"),path("presencas/",views.attendance,name="attendance"),
path("instituicao/",views.institution_settings,name="institution_settings"),
path("auditoria/",views.audit_logs,name="audit_logs"),
path("relatorios/desempenho.pdf",views.performance_report,name="performance_report"),
path("documentos/boletim/<int:student_id>.pdf",views.student_report_pdf,name="student_report_pdf"),
path("documentos/certificado/<int:student_id>.pdf",views.enrollment_certificate_pdf,name="enrollment_certificate_pdf")]
