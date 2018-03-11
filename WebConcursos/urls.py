from django.contrib import admin
from django.conf.urls import url
from WebConcursos import views
from django.urls import path

app_name = 'WebConcursos'

urlpatterns = [
	url(r'home/',views.CrearHomeView, name = 'home'),
    url(r'user/login/',views.formulario_ingresar_usuario, name = 'login'),
    url(r'user/logout/',views.logout_view, name = 'logout'),
    url(r'user/signup/',views.form_registrar_usuario, name = 'registro'),
	url(r'concursos/lista/',views.traer_lista_concursos, name = 'lista_concursos'),
	url(r'concursos/crearconcurso/',views.formulario_crear_concurso, name = 'crear_concurso'),
	url(r'^concursos/(?P<id_concurso>[\w-]+)/$',views.traer_detalle_concurso, name = 'detalle_concurso'),
    url(r'^concursos/borrar/(?P<id_concurso>\d+)/$',views.borrar_concurso, name = 'borrar'),
    url(r'^concursos/editar/(?P<id_concurso>\d+)/$',views.formulario_editar_concurso, name = 'editar'),
    url(r'^concursos/locutor/detalle_concurso/(?P<id_concurso>[\w-]+)/(?P<id_usuario>[\w-]+)/$',views.detalle_concurso_locutor, name = 'detalle_locutor'),
	url(r'url/(?P<url_usuario>[\w:/.@+-]+)', views.resolver_url, name='resolver'),
	url(r'user/crearlocutorlista/',views.RegistrarLocutorView, name = 'crear_locutor_lista'),
	url(r'^enviaremail/(?P<id_concurso>\d+)/$',views.EnviarCorreoListaView, name = 'enviaremail'),
	url(r'^locutor/borrar/(?P<id_locutor>\d+)/$',views.BorrarLocutorView, name = 'borrar_locutor'),
	#PABA
	url(r'user/datosadicionales/',views.RegistrarEmpresaView, name = 'empresa'),
	# YJC
	url(r'^concursos/enviar_audio/(?P<id_concurso>[\w-]+)/$',views.enviar_audio, name = 'enviar_audio'),
	url(r'^concursos/lista_de_audios/(?P<id_concurso>[\w-]+)/$',views.listar_audios, name='lista_de_audios'),
	url(r'^concursos/lista_de_audios_admin/(?P<id_concurso>[\w-]+)/$',views.listar_audios_admin, name='lista_de_audios_admin'),
	url(r'^concursos/marketing/lista_de_audios_marketing/(?P<id_concurso>[\w-]+)/$',views.listar_audios_marketing, name='lista_de_audios_marketing'),
	url(r'^concursos/marketing/(?P<id_concurso>[\w-]+)/$',views.traer_detalle_concurso_mkt, name = 'detalle_concurso_marketing'),
	url(r'^concursos/marketing/lista_de_audios_marketing/seleccion/(?P<id_concurso>[\w-]+)/(?P<id_audio>[\w-]+)/$',views.seleccionar_audio, name = 'seleccionar_audio'),
]
