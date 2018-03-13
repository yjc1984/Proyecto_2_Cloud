import os
import pydub
import glob
import shutil
import smtplib

import psycopg2
import time

print(time.strftime("%d/%m/%y"))
print(time.strftime("%H:%M:%S"))

#Paso 1 convertir los archivos wav a mp3
print("-------------------------------------------------------------")
print("Convirtiendo archivos WAV a MP3")
print("-------------------------------------------------------------")
wav_files = glob.glob('/home/ubuntu/media/*.wav')
for wav_file in wav_files:
	print(wav_file)
	mp3_file = os.path.splitext(wav_file)[0] + '.mp3'
	print(mp3_file)
	sound = pydub.AudioSegment.from_wav(wav_file)
	sound.export(mp3_file, format= "mp3")
	shutil.move(wav_file, '/home/ubuntu/media/procesados/')
print("-------------------------------------------------------------")
print("Convirtiendo archivos OGG a MP3")
print("-------------------------------------------------------------")
ogg_files = glob.glob('/home/ubuntu/media/*.ogg')
for ogg_file in ogg_files:
	print(ogg_file)
	mp3_file = os.path.splitext(ogg_file)[0] + '.mp3'
	print(mp3_file)
	sound = pydub.AudioSegment.from_ogg(ogg_file)
	sound.export(mp3_file, format= "mp3")
	#shutil.move(mp3_file, 'D:/01_ESTUDIOS/MAESTRIA/4_APLICACIONES_CLOUD/Proyecto_1_to_mp3/archivos_aplicacion/mp3')
	shutil.move(ogg_file, '/home/ubuntu/media/procesados/')

print("--------------------------------------")
print("FINALIZADO!!!!!!!!!!!")
print("--------------------------------------")


#Paso 2 valido conversiones para cambiar estado en la base de datos y habilitarlos para escuchar
print("-------------------------------------------------------------")
print("VALIDACION DE ARCHIVOS Y COPIAS PARA CAMBIO DE ESTADO EN DB")
print("-------------------------------------------------------------")
path_procesados = '/home/ubuntu/media/procesados/'
lstFilesConvertir = []
lstDirConvertir = os.walk(path_procesados)
for root, dirs, files in lstDirConvertir:
    for fichero in files:
        (nombreFichero, extension) = os.path.splitext(fichero)
        if(extension != ".mp3"):
            lstFilesConvertir.append(nombreFichero+extension)

path_generados = '/home/ubuntu/media/'
lstFilesMP3 = []
lstDirMP3 = os.walk(path_generados)
for root, dirs, files in lstDirMP3:
    for fichero in files:
        (nombreFichero, extension) = os.path.splitext(fichero)
        if(extension == ".mp3"):
            lstFilesMP3.append(nombreFichero+extension)

print("--------------------------------------")
print("Lista archivos procesados")
print("--------------------------------------")
for x in range(0,len(lstFilesConvertir)):
    print(lstFilesConvertir[x])
print("--------------------------------------")
print("Lista archivos MP3 generados")
print("--------------------------------------")
for x in range(0,len(lstFilesMP3)):
    print(lstFilesMP3[x])

print("--------------------------------------")
print("Mostrar en Pagina")
print("--------------------------------------")


user_db = os.environ["RDS_USERNAME"]
pass_db = os.environ["RDS_PASSWORD"]
host_db = os.environ["RDS_HOSTNAME"]
name_db = os.environ["RDS_DB_NAME"]


contador = 0
for i in range(0,len(lstFilesConvertir)): #buscar cada archivo a convertir en
    for j in range(0,len(lstFilesMP3)):   #los ya convertidos
        #print("Ciclo for i (a convertir): " , i)
        #print("Ciclo for j (Convertidos): " , j)
        #print("Nombre archivo a convertir : " , lstFilesConvertir[i].split('.')[0])
        #print("Nombre archivo convertido : " , lstFilesMP3[j].split('.')[0])
        if lstFilesConvertir[i].split('.')[0] == lstFilesMP3[j].split('.')[0]:
            contador = contador+1
            #print("Entra al if comparacion archivos")
            #print(contador)
            if(contador>0):
                print(lstFilesConvertir[i], "ya fue convertido a mp3 y tiene archivo original...cambiar estado en db")
                cnotador=0
                try:
                    db = psycopg2.connect(host=host_db,database=name_db, user=user_db, password=pass_db)
                    print("OK conexion establecida!!!!")
                    cursor=db.cursor()
                except psycopg2.Error as e:
                    print(e.pgerror)
                cursor = db.cursor()
                archivo_original = lstFilesConvertir[i]
                print(archivo_original)
                archivo_convertido = lstFilesMP3[j]
                print(archivo_convertido)

                cursor.execute(""" SELECT archivo_original,archivo_convertido, estado
                                   FROM "WebConcursos_audiolocutor"
                                   WHERE estado = 'En Proceso' AND archivo_original = '%s' """ %(archivo_original))
                for reg in cursor.fetchall():
                   print(reg)
                cursor.execute(""" UPDATE "WebConcursos_audiolocutor"
                                   SET estado = 'Convertido',
                                       archivo_convertido = '%s'
                                   WHERE estado = 'En Proceso'
                                   AND archivo_original = '%s' """ %(archivo_convertido,archivo_original))
                #cursor.execute(""" SELECT * FROM "WebConcursos_audiolocutor" """)
                #for concurso in cursor.fetchall():
                #    print(concurso)
                db.commit()
                # Envio de mail
                cursor.execute(""" SELECT email FROM "WebConcursos_audiolocutor"
                                   WHERE estado = 'Convertido'
                                   AND archivo_convertido = '%s' """ %(archivo_convertido))
                lista = cursor.fetchall()

                for indice in lista:
                    print("Enviando correo a: ", indice[0])
                    email_host=os.environ["SES_EMAIL_HOST"]
                    email_port=os.environ["SES_EMAIL_PORT"]
                    email_user=os.environ["SES_EMAIL_HOST_USER"]
                    email_pass=os.environ["SES_EMAIL_HOST_PASSWORD"]
                    smtp = smtplib.SMTP(email_host, email_port)
                    remitente = 'supervoices.cloud@gmail.com'
                    destinatario = indice[0]
                    asunto = "Aviso de procesamiento de audio"
                    encabezado = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (remitente, destinatario,asunto)
                    email = encabezado + "Hola! Te informamos que tu archivo de audio " + archivo_original + " a sido procesado con exito! "
                    smtp.starttls()
                    smtp.ehlo()
                    try:
                        smtp.login(email_user, email_pass)
                        print("Conectado")
                    except smtplib.SMTPAuthenticationError as e:
                        print(e.SMTPAuthenticationError)
                    print("email: ", email)
                    smtp.sendmail(remitente, destinatario, email)
                    smtp.close()
                db.close()
                print(time.strftime("%d/%m/%y"))
                print(time.strftime("%H:%M:%S"))
