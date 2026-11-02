from django.db import models
from django.contrib.auth.models import User
class Student(models.Model):
 user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="student_profile")
 number=models.CharField("Matrícula",max_length=30,unique=True)
 course=models.CharField("Curso/Classe",max_length=100)
 class_name=models.CharField("Turma",max_length=50)
 birth_date=models.DateField("Nascimento",null=True,blank=True)
 def __str__(self): return self.number+" - "+self.user.get_full_name()
class Teacher(models.Model):
 user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="teacher_profile")
 subject=models.CharField("Disciplina principal",max_length=100)
 phone=models.CharField("Telefone",max_length=30,blank=True)
 def __str__(self): return self.user.get_full_name() or self.user.username
class ClassGroup(models.Model):
 name=models.CharField("Turma",max_length=60,unique=True)
 course=models.CharField("Curso/Classe",max_length=100)
 academic_year=models.CharField("Ano lectivo",max_length=9)
 def __str__(self): return self.name+" - "+self.course
class Subject(models.Model):
 name=models.CharField("Disciplina",max_length=100)
 code=models.CharField("Código",max_length=20,unique=True)
 class_group=models.ForeignKey(ClassGroup,on_delete=models.CASCADE)
 teacher=models.ForeignKey(Teacher,on_delete=models.SET_NULL,null=True,blank=True,related_name="subjects")
 class Meta: unique_together=("name","class_group")
 def __str__(self): return self.name+" - "+self.class_group.name
class Enrollment(models.Model):
 student=models.ForeignKey(Student,on_delete=models.PROTECT)
 class_group=models.ForeignKey(ClassGroup,on_delete=models.PROTECT)
 academic_year=models.CharField("Ano lectivo",max_length=9)
 enrollment_date=models.DateField("Data da matrícula",auto_now_add=True)
 active=models.BooleanField("Activa",default=True)
 class Meta: unique_together=("student","academic_year")
class Attendance(models.Model):
 STATUS=[("P","Presente"),("F","Falta"),("J","Falta justificada")]
 student=models.ForeignKey(Student,on_delete=models.CASCADE)
 subject=models.ForeignKey(Subject,on_delete=models.CASCADE)
 date=models.DateField("Data")
 status=models.CharField("Estado",max_length=1,choices=STATUS)
 note=models.CharField("Observação",max_length=250,blank=True)
 recorded_by=models.ForeignKey(User,on_delete=models.PROTECT)
 class Meta: unique_together=("student","subject","date")
class Grade(models.Model):
 student=models.ForeignKey(Student,on_delete=models.CASCADE,related_name="grades")
 subject=models.CharField("Disciplina",max_length=100)
 term=models.CharField("Trimestre",max_length=30)
 score=models.DecimalField("Nota",max_digits=5,decimal_places=2)
 recorded_by=models.ForeignKey(User,on_delete=models.PROTECT)
 created_at=models.DateTimeField(auto_now_add=True)


class InstitutionSettings(models.Model):
    name = models.CharField("Nome da instituição", max_length=180, default="TXENDA - Instituição de Ensino")
    acronym = models.CharField("Sigla", max_length=30, blank=True)
    address = models.CharField("Endereço", max_length=220, blank=True)
    phone = models.CharField("Telefone", max_length=40, blank=True)
    email = models.EmailField("E-mail", blank=True)
    logo = models.ImageField("Logótipo", upload_to="institution/", blank=True, null=True)
    footer_text = models.CharField("Texto do rodapé dos documentos", max_length=250, blank=True,
                                   default="Documento emitido pelo TXENDA - Sistema Inteligente de Gestão Escolar.")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Configuração da instituição"
        verbose_name_plural = "Configurações da instituição"


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField("Acção", max_length=180)
    details = models.TextField("Detalhes", blank=True)
    ip_address = models.GenericIPAddressField("Endereço IP", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Registo de auditoria"
        verbose_name_plural = "Registos de auditoria"

    def __str__(self):
        return f"{self.action} - {self.created_at:%d/%m/%Y %H:%M}"
