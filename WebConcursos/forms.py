from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import models, UsuarioCustom, AudioLocutor
from WebConcursos import models
from django.contrib.auth import password_validation, authenticate
from django.utils.text import capfirst
import unicodedata

## UserCreationCustom funciona con nombres y apellidos pero sin empresa ni rol
class UserCreationCustom(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name','last_name','username','password1','password2',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user



class FormCrearConcurso(forms.ModelForm):
	class Meta:
		model = models.Concurso
		fields = ['nombre','fecha_inicio','fecha_fin','valor_pagar','ruta_imagen','texto_voz','recomendaciones','url_concurso_custom']
		widgets = {
		'fecha_fin' : forms.DateTimeInput(attrs={'placeholder': '2006-10-25' , 'id': 'fecha_fin' , 'onchange': 'return validacion(this.value)' }),
		'fecha_inicio' : forms.DateTimeInput(attrs={'placeholder': '2006-10-25' , 'id': 'fecha_inicio' , 'onchange': 'return validacion(this.value)' }),
		'texto_voz' :  forms.Textarea(attrs={'rows':10, 'cols':50}),
		'recomendaciones' :  forms.Textarea(attrs={'rows':10, 'cols':50}),
		}

class FormEditarConcurso(forms.ModelForm):
	class Meta:
		model = models.Concurso
		fields = ['nombre','fecha_inicio','fecha_fin','valor_pagar', 'ruta_imagen', 'texto_voz','recomendaciones','url_concurso_custom']
		widgets = {
		'fecha_fin' : forms.DateTimeInput(attrs={'placeholder': '2006-10-25' , 'id': 'fecha_fin' , 'onchange': 'return validacion(this.value)' }),
		'fecha_inicio' : forms.DateTimeInput(attrs={'placeholder': '2006-10-25' , 'id': 'fecha_inicio' , 'onchange': 'return validacion(this.value)' }),
		'texto_voz' :  forms.Textarea(attrs={'rows':10, 'cols':50}),
		'recomendaciones' :  forms.Textarea(attrs={'rows':10, 'cols':50}),

		}

class FormListaLocutor(forms.ModelForm):
    class Meta:
        model = models.ListaLocutores
        fields = ['nombre','email']

class FormEnviarCorreo(forms.Form):
        fields = ['asunto','mensaje']
        asunto = forms.CharField(max_length=500)
        mensaje = forms.CharField(widget=forms.Textarea)


#usuario con rol y empresa
class UserCreationEmpresa(UserCreationForm):
    class Meta:
        model = UsuarioCustom
        fields = ('first_name','last_name','username', 'Rol','Empresa','password1','password2',)

# YJC

class FormularioEnvioAudio(forms.ModelForm):

    class Meta:
        model = AudioLocutor
        fields = ('nombre','apellidos','email','descripcion_audio','archivo_original','observaciones')
        widgets = {
        'observaciones' :  forms.Textarea(attrs={'rows':10, 'cols':50}),
        }

#modelo para relacionar con empresa y usuario
class UserCreationRolEmpresa(forms.ModelForm):
    class Meta:
        model = models.EmpresaRol
        fields = ['Empresa','Rol']