from django import forms
from django.contrib.auth.models import User
from .models import *
class UserBaseForm(forms.ModelForm):
 password=forms.CharField(label="Palavra-passe inicial",widget=forms.PasswordInput,min_length=8)
 class Meta:
  model=User
  fields=["username","first_name","last_name","email"]
  labels={"username":"Utilizador","first_name":"Nome","last_name":"Apelido","email":"E-mail"}
class StudentForm(UserBaseForm):
 number=forms.CharField(label="Matrícula"); course=forms.CharField(label="Curso/Classe"); class_name=forms.CharField(label="Turma")
 birth_date=forms.DateField(label="Nascimento",required=False,widget=forms.DateInput(attrs={"type":"date"}))
 def save(self):
  d=self.cleaned_data; u=User.objects.create_user(username=d["username"],password=d["password"],first_name=d["first_name"],last_name=d["last_name"],email=d["email"])
  Student.objects.create(user=u,number=d["number"],course=d["course"],class_name=d["class_name"],birth_date=d["birth_date"]); return u
class TeacherForm(UserBaseForm):
 subject=forms.CharField(label="Disciplina principal"); phone=forms.CharField(label="Telefone",required=False)
 def save(self):
  d=self.cleaned_data; u=User.objects.create_user(username=d["username"],password=d["password"],first_name=d["first_name"],last_name=d["last_name"],email=d["email"])
  Teacher.objects.create(user=u,subject=d["subject"],phone=d["phone"]); return u
class GradeForm(forms.ModelForm):
 class Meta:
  model=Grade; fields=["student","subject","term","score"]
  widgets={"score":forms.NumberInput(attrs={"min":"0","max":"20","step":"0.01"})}
class ClassGroupForm(forms.ModelForm):
 class Meta: model=ClassGroup; fields=["name","course","academic_year"]
class SubjectForm(forms.ModelForm):
 class Meta: model=Subject; fields=["name","code","class_group","teacher"]
class EnrollmentForm(forms.ModelForm):
 class Meta: model=Enrollment; fields=["student","class_group","academic_year","active"]
class AttendanceForm(forms.ModelForm):
 class Meta:
  model=Attendance; fields=["student","subject","date","status","note"]
  widgets={"date":forms.DateInput(attrs={"type":"date"})}


class InstitutionSettingsForm(forms.ModelForm):
 class Meta:
  model = InstitutionSettings
  fields = ["name","acronym","address","phone","email","logo","footer_text"]
