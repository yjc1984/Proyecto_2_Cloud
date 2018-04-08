from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, AbstractUser, AnonymousUser
from django.db.models.signals import post_save
from django.urls import reverse
from PIL import Image
from .validators import validar_formato
from django.conf import settings

from concursos.storage_backends import ProcesadosStorage, MediaStorage

class Locutor(models.Model):

    # Definicion atributos

    nombre = models.CharField(max_length=200)
    apellidos = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    #id_audio = models.ForeignKey(Audio,on_delete=models.CASCADE)
    observaciones = models.CharField(max_length=2000)

class UsuarioCustom(AbstractUser):
    ROLES = (
                ('Administrador', 'Administrador'),
                ('Marketing', 'Marketing'),
    )
    #Se deben crear los mismos campos que se enviaran desde la forma pues deben ser almacenados, de lo contrario falla
    id_administrador = models.AutoField(auto_created=True, primary_key=True)
    username = models.CharField(max_length=200,unique=True)
    Empresa = models.CharField(max_length=200, blank=True)
    Rol = models.CharField(max_length=200, blank=True, choices=ROLES)
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)

    @property
    def user_permissions(self):
        return self._user_permissions

    @property
    def groups(self):
        return self._groups

    def user(self):
        return self.username

    USERNAME_FIELD = 'username'

class Concurso(models.Model):

    # Definicion atributos

    nombre = models.CharField(max_length=200)
    fecha_inicio = models.DateTimeField(blank=False)
    fecha_fin = models.DateTimeField(blank=False)
    valor_pagar = models.IntegerField()
    ruta_imagen = models.ImageField(blank=True,null=True)
    texto_voz = models.CharField(max_length=2000)
    recomendaciones = models.CharField(max_length=2000)
    url_concurso = models.URLField(null=True,blank=False,max_length=200)
    url_concurso_custom = models.URLField(null=True,blank=True,max_length=200)
    fecha_creacion = models.DateTimeField(blank=True, default=timezone.now)
    estado = models.CharField(null=True,max_length=2000, default='Vigente')
    id_administrador = models.ForeignKey(User,on_delete=models.CASCADE)

class ListaLocutores(models.Model):
    nombre = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    id_administrador = models.ForeignKey(User,on_delete=models.CASCADE)

# YJC

class AudioLocutor(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    observaciones = models.CharField(max_length=1000)
    descripcion_audio = models.CharField(max_length=100,null=True)
    archivo_original = models.FileField(storage=MediaStorage(),validators=[validar_formato],default = 'Null')
    archivo_convertido = models.FileField(storage=ProcesadosStorage(),default = 'Null')
    estado = models.CharField(max_length=100,default='En Proceso')
    seleccionado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    id_concurso = models.ForeignKey(Concurso, related_name='concurso',on_delete=models.CASCADE,default = 1)

#BOAA01
class EmpresaRol(models.Model):
    ROLES = (
                ('Administrador', 'Administrador'),
                ('Marketing', 'Marketing'),
    )
    Empresa = models.CharField(max_length=200, blank=True, default='Asignar Empresa')
    Rol = models.CharField(max_length=200, blank=True, choices=ROLES, default='Administrador')
    id_usuario = models.ForeignKey(User,on_delete=models.CASCADE)
