from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render,redirect
from django.db.models import Avg
from .models import *
from .forms import *
from .decorators import admin_required
@login_required
def dashboard(request):
 avg=Grade.objects.aggregate(v=Avg("score"))["v"] or 0
 c={"students":Student.objects.count(),"teachers":Teacher.objects.count(),"grades":Grade.objects.count(),"average":round(float(avg),2),"classes":ClassGroup.objects.count(),"subjects":Subject.objects.count(),"enrollments":Enrollment.objects.filter(active=True).count(),"attendance_count":Attendance.objects.count(),"recent_grades":Grade.objects.select_related("student__user").order_by("-created_at")[:8]}
 if hasattr(request.user,"student_profile"):
  c["my_grades"]=Grade.objects.filter(student=request.user.student_profile)
  c["my_attendance"]=Attendance.objects.filter(student=request.user.student_profile).select_related("subject").order_by("-date")[:10]
 return render(request,"school/dashboard.html",c)
def admin_form(request, Form, Model, template, msg, related=()):
 form=Form(request.POST or None)
 if request.method=="POST" and form.is_valid():
  form.save(); messages.success(request,msg); return redirect(request.resolver_match.url_name)
 return render(request,template,{"form":form,"items":Model.objects.select_related(*related) if related else Model.objects.all()})
@login_required
@admin_required
def students(request): return admin_form(request,StudentForm,Student,"school/students.html","Estudante cadastrado.",("user",))
@login_required
@admin_required
def teachers(request): return admin_form(request,TeacherForm,Teacher,"school/teachers.html","Professor cadastrado.",("user",))
@login_required
@admin_required
def classes(request): return admin_form(request,ClassGroupForm,ClassGroup,"school/classes.html","Turma criada.")
@login_required
@admin_required
def subjects(request): return admin_form(request,SubjectForm,Subject,"school/subjects.html","Disciplina criada.",("class_group","teacher__user"))
@login_required
@admin_required
def enrollments(request): return admin_form(request,EnrollmentForm,Enrollment,"school/enrollments.html","Matrícula registada.",("student__user","class_group"))
@login_required
def grades(request):
 can_add=request.user.is_superuser or hasattr(request.user,"teacher_profile"); form=GradeForm(request.POST or None)
 if request.method=="POST":
  if not can_add: messages.error(request,"Sem permissão."); return redirect("grades")
  if form.is_valid():
   obj=form.save(commit=False); obj.recorded_by=request.user; obj.save(); messages.success(request,"Nota registada."); return redirect("grades")
 items=Grade.objects.filter(student=request.user.student_profile) if hasattr(request.user,"student_profile") else Grade.objects.select_related("student__user")
 return render(request,"school/grades.html",{"form":form,"items":items.order_by("-created_at"),"can_add":can_add})
@login_required
def attendance(request):
 can_add=request.user.is_superuser or hasattr(request.user,"teacher_profile"); form=AttendanceForm(request.POST or None)
 if request.method=="POST":
  if not can_add: messages.error(request,"Sem permissão."); return redirect("attendance")
  if form.is_valid():
   obj=form.save(commit=False); obj.recorded_by=request.user; obj.save(); messages.success(request,"Registo guardado."); return redirect("attendance")
 items=Attendance.objects.filter(student=request.user.student_profile) if hasattr(request.user,"student_profile") else Attendance.objects.select_related("student__user","subject")
 return render(request,"school/attendance.html",{"form":form,"items":items.order_by("-date"),"can_add":can_add})


from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count
from .models import InstitutionSettings, AuditLog
from .forms import InstitutionSettingsForm
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


def log_action(request, action, details=""):
    ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR"))
    if ip and "," in ip:
        ip = ip.split(",")[0].strip()
    AuditLog.objects.create(user=request.user if request.user.is_authenticated else None,
                            action=action, details=details, ip_address=ip or None)


def get_institution():
    return InstitutionSettings.objects.first() or InstitutionSettings.objects.create()


@login_required
@admin_required
def institution_settings(request):
    obj = get_institution()
    form = InstitutionSettingsForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "Actualização dos dados da instituição", obj.name)
        messages.success(request, "Dados institucionais actualizados.")
        return redirect("institution_settings")
    return render(request, "school/institution_settings.html", {"form": form, "institution": obj})


@login_required
@admin_required
def audit_logs(request):
    return render(request, "school/audit_logs.html",
                  {"logs": AuditLog.objects.select_related("user")[:250]})


def pdf_response(filename, title, lines, institution=None):
    institution = institution or get_institution()
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 22*mm
    p.setFillColorRGB(0.04, 0.15, 0.29)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(20*mm, y, institution.name[:75])
    y -= 8*mm
    p.setFillColorRGB(0.1, 0.1, 0.1)
    p.setFont("Helvetica", 9)
    details = " | ".join(x for x in [institution.acronym, institution.address, institution.phone, institution.email] if x)
    if details:
        p.drawString(20*mm, y, details[:110]); y -= 7*mm
    if institution.logo:
        try:
            p.drawImage(institution.logo.path, width-48*mm, height-42*mm, width=25*mm, height=25*mm,
                        preserveAspectRatio=True, mask="auto")
        except Exception:
            pass
    p.setStrokeColorRGB(0.08, 0.36, 0.63); p.line(20*mm, y, width-20*mm, y)
    y -= 14*mm
    p.setFont("Helvetica-Bold", 14); p.drawCentredString(width/2, y, title.upper()); y -= 15*mm
    p.setFont("Helvetica", 10)
    for line in lines:
        if y < 30*mm:
            p.showPage(); y = height - 25*mm; p.setFont("Helvetica", 10)
        p.drawString(22*mm, y, str(line)[:115]); y -= 8*mm
    y -= 5*mm
    p.setFont("Helvetica-Oblique", 8)
    p.drawString(20*mm, 18*mm, institution.footer_text[:130])
    p.drawRightString(width-20*mm, 18*mm, "Emitido em " + timezone.localtime().strftime("%d/%m/%Y %H:%M"))
    p.save()
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@login_required
def student_report_pdf(request, student_id):
    if not request.user.is_superuser and not hasattr(request.user, "teacher_profile"):
        if not hasattr(request.user, "student_profile") or request.user.student_profile.id != student_id:
            messages.error(request, "Não tem permissão para consultar este documento.")
            return redirect("dashboard")
    student = Student.objects.select_related("user").get(pk=student_id)
    grades = Grade.objects.filter(student=student).order_by("term", "subject")
    lines = [
        f"Estudante: {student.user.get_full_name()}",
        f"Número de matrícula: {student.number}",
        f"Curso/Classe: {student.course} | Turma: {student.class_name}",
        " "
    ]
    if grades:
        for g in grades:
            lines.append(f"{g.term} - {g.subject}: {g.score} valores")
        average = grades.aggregate(v=Avg("score"))["v"] or 0
        lines += [" ", f"Média geral das notas registadas: {average:.2f} valores"]
    else:
        lines.append("Ainda não existem notas registadas.")
    log_action(request, "Emissão de boletim", student.number)
    return pdf_response(f"boletim_{student.number}.pdf", "Boletim de notas", lines)


@login_required
def enrollment_certificate_pdf(request, student_id):
    if not request.user.is_superuser and not hasattr(request.user, "teacher_profile"):
        if not hasattr(request.user, "student_profile") or request.user.student_profile.id != student_id:
            messages.error(request, "Não tem permissão para consultar este documento.")
            return redirect("dashboard")
    student = Student.objects.select_related("user").get(pk=student_id)
    enrollment = Enrollment.objects.filter(student=student, active=True).order_by("-academic_year").first()
    lines = [f"Certifica-se que {student.user.get_full_name()}",
             f"Está registado(a) com o número de matrícula {student.number}.",
             f"Curso/Classe: {student.course}", f"Turma: {student.class_name}",
             f"Ano lectivo: {enrollment.academic_year if enrollment else 'Não indicado'}",
             " ", "Este documento é emitido para os devidos efeitos."]
    log_action(request, "Emissão de certificado de matrícula", student.number)
    return pdf_response(f"certificado_{student.number}.pdf", "Certificado de matrícula", lines)


@login_required
@admin_required
def performance_report(request):
    rows = []
    for student in Student.objects.select_related("user").all():
        agg = student.grades.aggregate(v=Avg("score"))
        avg = agg["v"]
        rows.append((student, avg))
    rows.sort(key=lambda x: (x[1] is not None, x[1] or 0), reverse=True)
    lines = [f"Gerado em: {timezone.localtime():%d/%m/%Y %H:%M}", " "]
    for student, avg in rows:
        lines.append(f"{student.number} - {student.user.get_full_name()}: {avg:.2f}" if avg is not None
                     else f"{student.number} - {student.user.get_full_name()}: sem notas")
    log_action(request, "Emissão de relatório de desempenho")
    return pdf_response("relatorio_desempenho.pdf", "Relatório de desempenho", lines)


def offline_page(request):
    return render(request, "offline.html")


def service_worker(request):
    from django.conf import settings
    from django.http import HttpResponse
    path = settings.BASE_DIR / "static" / "pwa" / "sw.js"
    response = HttpResponse(path.read_text(encoding="utf-8"), content_type="application/javascript")
    response["Service-Worker-Allowed"] = "/"
    response["Cache-Control"] = "no-cache"
    return response
