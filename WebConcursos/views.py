from django.shortcuts import render, redirect
from django.http import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from .import forms
from django.contrib.auth.decorators import login_required
import re
from django.contrib import messages
from .models import Concurso, UsuarioCustom, ListaLocutores,AudioLocutor, EmpresaRol
from WebConcursos.forms import UserCreationCustom
from django.core.mail import EmailMessage, send_mail
from django.core.files.storage import FileSystemStorage
import boto3
import shutil

# Create your views here.
#registrar usuarios: metodo usado para crear el usuario en la aplicacion
def form_registrar_usuario(request):
	print(request.POST.get('username'))
	if request.method == 'POST':
		#formulario_registro = forms.UserRegisterFormCustom(request.POST)
		formulario_registro = forms.UserCreationCustom(request.POST) ##funciona con nombres y apellidos pero sin empresa ni rol
		#formulario_registro = UserCreationForm(request.POST)
		formulario_registro.errors.as_data()
		if formulario_registro.is_valid():
			patron_correo = re.compile(r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
			cumple_patron = patron_correo.match(request.POST.get('username'))
			print(cumple_patron)
			if cumple_patron:
				user = formulario_registro.save(commit=False) #crea el elemnto, lo captura sin dar commit para modificar campos
				user.save()
				login(request,user)
				messages.success(request, 'Gracias por registrarte!!!!!')
				messages.success(request, 'El username para ingreso a la aplicacion es ')
				messages.success(request, user.username)
				return redirect('WebConcursos:login') #Lo envio a la pantalla de ingreso de usuarios ya registrados
			else:
				messages.info(request, 'El registro debe realizarse con un correo electronico valido')
	else:
		#formulario_registro = forms.UserRegisterFormCustom()
		formulario_registro = forms.UserCreationCustom() ##funciona con nombres y apellidos pero sin empresa ni rol
		#formulario_registro = UserCreationForm()
	return render(request,'nuevo_usuario.html',{'formulario_registro':formulario_registro})


#login
def formulario_ingresar_usuario(request):
	if request.method == 'POST':
		print(request.POST)
		formulario_ingreso = AuthenticationForm(data=request.POST)
		print(formulario_ingreso.errors)
		if formulario_ingreso.is_valid(): #si el usuario y password son correctos
			#login
			user = formulario_ingreso.get_user()
			login(request,user)
			return redirect('WebConcursos:lista_concursos') #hacia urls.py para name = lista_eventos
	else:
		formulario_ingreso = AuthenticationForm()
	return render(request,'login.html',{'formulario_ingreso':formulario_ingreso})

#logout
def logout_view(request):
	logout(request)
	return redirect('WebConcursos:login') #hacia urls.py para name = lista_eventos


def formulario_crear_concurso(request):
	print(request.method)
	if request.method == 'POST':
		formulario_crear = forms.FormCrearConcurso(request.POST, request.FILES)
		print(formulario_crear.errors)
		print(request.FILES.get('ruta_imagen'))
		if formulario_crear.is_valid():
			print("Request para crear concurso", request.POST)
			concurso = formulario_crear.save(commit=False)
			concurso.id_administrador = request.user
			#concurso.ruta_imagen = 'http://localhost:8000/media/media/' + str(request.POST.get('ruta_imagen'))
			concurso.save()
			concurso.url_concurso = '/concursos/locutor/detalle_concurso/'+ str(concurso.id) + '/' + str(concurso.id_administrador.id)
			concurso.save()
			url_usuario = concurso.url_concurso_custom
			concurso.url_concurso_custom = str(url_usuario)
			concurso.save()
			if request.FILES.get('ruta_imagen') == None:
				concurso.ruta_imagen = 'sin-imagen.png'
				concurso.save()
			return redirect('WebConcursos:lista_concursos' ) #despues de guardarlo, envio al usuario a la lista de eventos
	else:
		form_crear_concurso = forms.FormCrearConcurso()
		return render(request, 'crear_concurso.html', {'form_crear_concurso':form_crear_concurso})

#Ordena los concursos por la fecha de inicio del mismo
def traer_lista_concursos(request):
	concursos = Concurso.objects.filter(id_administrador = request.user).order_by('fecha_inicio')
	empresa = EmpresaRol.objects.all().filter(id_usuario = request.user.id)
	return render(request, 'lista_concursos.html', {'concursos':concursos, 'empresa':empresa})



def borrar_concurso(request, id_concurso):
	id_elegido = id_concurso
	concurso = Concurso.objects.filter(id = id_elegido)
	concurso.delete()
	current_user = request.user
	concursos = Concurso.objects.filter(id_administrador = request.user).order_by('fecha_inicio')
	empresa = EmpresaRol.objects.all().filter(id_usuario = request.user.id)
	return render(request, 'lista_concursos.html', {'concursos':concursos, 'empresa':empresa})



def traer_detalle_concurso(request, id_concurso):
	id_elegido = id_concurso
	concurso = Concurso.objects.all().filter(id = id_elegido)
	return render(request, 'detalle_concurso.html', {'concurso':concurso})


def formulario_editar_concurso(request, id_concurso):
	print("metodo  formulario_editar_concurso ", request.method)
	if request.method == 'POST':
		formulario_edicion = forms.FormEditarConcurso(request.POST, request.FILES)
		print(formulario_edicion.errors.as_data)
		if formulario_edicion.is_valid():
			concurso = formulario_edicion.save(commit=False)
			concurso.id = id_concurso
			concurso.id_administrador = request.user
			concurso.url_concurso = '/concursos/locutor/detalle_concurso/'+ str(concurso.id) + '/' + str(concurso.id_administrador.id)
			concurso.save()
			concurso.url_concurso_custom = str(concurso.url_concurso_custom)
			concurso.save()
			if request.FILES.get('ruta_imagen') == None:
				concurso.ruta_imagen = 'sin-imagen.png'
				concurso.save()
			print("Edicion terminada")
		return redirect('WebConcursos:lista_concursos' ) #despues de guardarlo, envio al usuario a la lista de eventos
	else:
		concursos = Concurso.objects.filter(id = id_concurso)
		print(id_concurso)
		formulario_edicion = forms.FormEditarConcurso()
		return render(request, 'editar_concurso.html', {'formulario_edicion':formulario_edicion , 'concursos':concursos })



def detalle_concurso_locutor(request, id_concurso,id_usuario):
	id_elegido = id_concurso
	print("id_elegido", id_elegido,'id_usuario', id_usuario )
	concurso = Concurso.objects.filter(id = id_elegido, id_administrador=id_usuario)
	return render(request, 'detalle_locutor.html', {'concurso':concurso})

def resolver_url(request, url_usuario):
	print("url_usuario", url_usuario)
	if url_usuario != 'None':
		print("paso este if")
		url_oficial = Concurso.objects.all().filter(url_concurso_custom = str(url_usuario))[0].url_concurso
		print('url_oficial',url_oficial)
		if url_oficial != 'None': # si no es vacia la direccion del usuario, pero no encuentra en la consulta la url oficial
			print("Esta es la url oficial: ", url_oficial )
			return redirect(url_oficial)
		else:
			print("No Existe la direccion configurada")
			return render(request, 'page_not_found.html')
	else:
		print("No se ha configurado esta url por el usuario, por favor intentar la asignada por el sistema")
		return render(request, 'page_not_found.html')

def cargar(request):
	if request.method == 'POST':
		formulario_ingreso = forms.UploadFileForm(data=request.POST)
		if formulario_ingreso.is_valid(): #si el usuario y password son correctos
			foto = formulario_ingreso.save(commit=False)
			foto.save()
	else:
		formulario_ingreso = forms.UploadFileForm()
	return render(request,'upload.html',{'formulario_ingreso':formulario_ingreso})

def RegistrarLocutorView(request):
	if request.method == 'POST':
		form_lista_locutor = forms.FormListaLocutor(data=request.POST)
		if form_lista_locutor.is_valid():
			formulario = form_lista_locutor.save(commit=False)
			formulario.id_administrador = request.user
			formulario.save()
			locutores = ListaLocutores.objects.filter(id_administrador = request.user)
			form_lista_locutor = forms.FormListaLocutor()
			return render(request, 'crear_lista_locutores.html', {'form_lista_locutor':form_lista_locutor, 'locutores':locutores})
	else:
		locutores = ListaLocutores.objects.filter(id_administrador = request.user)
		form_lista_locutor = forms.FormListaLocutor()
	return render(request,'crear_lista_locutores.html',{'form_lista_locutor':form_lista_locutor, 'locutores':locutores})


def EnviarCorreoListaView(request, id_concurso):
	print("Estoy en EnviarCorreoListaView con el metodo", request.method )
	if request.method == 'POST':
		form_mensaje = forms.FormEnviarCorreo(data=request.POST)
		print("Formulario correo valido? : ", form_mensaje.is_valid())
		locutores = ListaLocutores.objects.all().filter(id_administrador = request.user)
		print(locutores.count())
		for indice in range(len(locutores)):
			print('Se enviara el concurso a : ',locutores[indice].email)

		if form_mensaje.is_valid():
			#para = request.POST.get('para')
			asunto = request.POST.get('asunto')
			mensaje = request.POST.get('mensaje')
			for indice in range(len(locutores)):
				email = EmailMessage(
							    asunto,
							    mensaje,
							    to=[locutores[indice].email],
								)
				email.send()
			return redirect('WebConcursos:lista_concursos')
	else:
		print('id_concurso', id_concurso)
		concurso = Concurso.objects.all().filter(id = id_concurso)
		form_mensaje = forms.FormEnviarCorreo()
	return render(request,'enviar_mail.html',{'form_mensaje':form_mensaje, 'concurso':concurso})

def BorrarLocutorView(request, id_locutor):
	id_elegido = id_locutor
	locutor = ListaLocutores.objects.filter(id = id_elegido)
	locutor.delete()
	current_user = request.user
	locutores = ListaLocutores.objects.filter(id_administrador = request.user)
	form_lista_locutor = forms.FormListaLocutor()
	return render(request, 'crear_lista_locutores.html', {'form_lista_locutor':form_lista_locutor, 'locutores':locutores})

def CrearHomeView(request):
	#Crear un div por cada usuario con concursos
	users = User.objects.all().count()
	empresas = EmpresaRol.objects.all().count()
	numero_concursos = Concurso.objects.all().count()
	print(empresas)
	print(numero_concursos)
	usuarios = User.objects.all()
	concursos = Concurso.objects.all()
	empresas = EmpresaRol.objects.all()
	for indice in range(len(empresas)):
		print('Se creara div para : ',empresas[indice].Empresa)
	return render(request,'home.html',{'empresas':empresas ,'concursos':concursos, 'numero_concursos':numero_concursos,
										'usuarios':usuarios})

# YJC

def enviar_audio(request,id_concurso):

    mensaje = "Hemos recibido tu voz y la estamos procesando para que sea publicada en la página del concurso y pueda ser posteriormente revisada por nuestro equipo de trabajo. Tan pronto la voz quede publicada en la página del concurso te notificaremos por email."
    p_id_concurso = id_concurso

    if request.method == 'POST':
        form = forms.FormularioEnvioAudio(request.POST, request.FILES)
        print(form.errors)
        if form.is_valid():
            AudioLocutorNuevo = AudioLocutor(nombre = request.POST['nombre'],
                                             apellidos = request.POST['apellidos'],
                                             email = request.POST['email'],
                                             observaciones = request.POST['observaciones'],
                                             descripcion_audio = request.POST['descripcion_audio'],
                                             archivo_original = request.FILES['archivo_original'],
                                             id_concurso_id = p_id_concurso,)
            AudioLocutorNuevo.save(form)
            print("id audio",AudioLocutorNuevo.id)
            p_id_audio = AudioLocutorNuevo.id
            messages.add_message(request, messages.INFO,mensaje)
            formato_archivo = str(request.FILES['archivo_original']).split('.')[1]
            nombre_archivo = str(request.FILES['archivo_original'])
            if formato_archivo == "mp3":
                print("Dentro del if archivo convertido")
                audio = AudioLocutor.objects.get(id = p_id_audio)
                audio.estado = "Convertido"
                print(audio.archivo_original)
                audio.archivo_convertido = audio.archivo_original
                audio.save()
                #shutil.copy(nombre_archivo,'/procesados')
            # SQS
            else:
                sqs_registrar_mensaje(str(p_id_audio), nombre_archivo)
    else:
        form = forms.FormularioEnvioAudio()

    return render(request, 'upload_audio.html', {'form': form})


def listar_audios(request,id_concurso):
    p_id_concurso = id_concurso
    lista = AudioLocutor.objects.filter(id_concurso = p_id_concurso,estado = 'Convertido').order_by('-fecha_creacion')
    return render(request, 'lista_audios.html', {'lista': lista})

def listar_audios_admin(request,id_concurso):
    p_id_concurso = id_concurso
    lista = AudioLocutor.objects.filter(id_concurso = p_id_concurso).order_by('-fecha_creacion')
    return render(request, 'lista_audios_admin.html', {'lista': lista})

def listar_audios_marketing(request,id_concurso):
    p_id_concurso = id_concurso
    lista = AudioLocutor.objects.filter(id_concurso = p_id_concurso,estado = 'Convertido').order_by('-fecha_creacion')
    return render(request, 'lista_audios_marketing.html', {'lista': lista})

def traer_detalle_concurso_mkt(request, id_concurso):
	id_elegido = id_concurso
	concurso = Concurso.objects.all().filter(id = id_elegido)
	return render(request, 'detalle_concurso_marketing.html', {'concurso':concurso})

def seleccionar_audio (request,id_concurso,id_audio):
	#mensaje = "Audio Seleccionado!"
	p_id_concurso = id_concurso
	p_id_audio = id_audio
	audio = AudioLocutor.objects.get(id = p_id_audio)
	audio.seleccionado = 1
	audio.save()
	lista = AudioLocutor.objects.filter(id_concurso = p_id_concurso,estado = 'Convertido').order_by('-fecha_creacion')
	#messages.add_message(request, messages.INFO,mensaje)
	return render(request, 'lista_audios_marketing.html', {'lista':lista})

def RegistrarEmpresaView(request):
	if request.method == 'POST':
		form_datos_empresa = forms.UserCreationRolEmpresa(data=request.POST)
		if form_datos_empresa.is_valid():
			formulario = form_datos_empresa.save(commit=False)
			configurado = EmpresaRol.objects.all().filter(id_usuario = request.user.id).count()
			if configurado == 1:
				em = EmpresaRol.objects.get(id_usuario = request.user.id)
				em.id_usuario = request.user
				em.Empresa = request.POST.get('Empresa')
				print(em.Empresa)
				em.Rol = request.POST.get('Rol')
				print(em.Rol)
				em.save()
			else:
				formulario = form_datos_empresa.save(commit=False)
				formulario.id_usuario = request.user
				formulario.id = request.POST.get(id)
				formulario.save()
		usuario = User.objects.all().filter(id = request.user.id)
		empresa = EmpresaRol.objects.all().filter(id_usuario = request.user.id)
		return render(request,'empresa_rol.html',{'form_datos_empresa':form_datos_empresa, 'usuario':usuario, 'empresa':empresa})
	else:
		usuario = User.objects.all().filter(id = request.user.id)
		form_datos_empresa = forms.UserCreationRolEmpresa()
		empresa = EmpresaRol.objects.all().filter(id_usuario = request.user.id)
	return render(request,'empresa_rol.html',{'form_datos_empresa':form_datos_empresa, 'usuario':usuario, 'empresa':empresa})

	# Manejo de colas SQS



def sqs_registrar_mensaje(id_audio, archivo_original):
    # Create SQS client
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='sqs_concursos')
    url_queue=queue.url
    # Create a new message
    response = queue.send_message(MessageBody='Registrando Mensaje',
                                  MessageAttributes={
                                                        'id_audio': {
                                                                    'StringValue': id_audio,
                                                                    'DataType': 'Number'
                                                                    },
                                                        'archivo_original': {
                                                                    'StringValue': archivo_original,
                                                                    'DataType': 'String'
                                                                    }
                                                    })
    print(response.get('MessageId'))
    print(response.get('MD5OfMessageBody'))
