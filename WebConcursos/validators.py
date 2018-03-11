from django.core.exceptions import ValidationError

def validar_formato(value):

    print(value.name.endswith)

    if (not value.name.endswith('.wav') and
        not value.name.endswith('.mp3') and
        not value.name.endswith('.ogg')):

        raise ValidationError("Archivos permitidos: .mp3, .wav, .ogg")
