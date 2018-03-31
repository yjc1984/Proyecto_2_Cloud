import os
import pydub
import glob
import shutil
import smtplib
import psycopg2
import time
#import sqlite3


print("Inicio de la Ejecucion de batchMP3.py")
print(time.strftime("%d/%m/%y %H:%M:%S"))

#variables de entorno produccion
user_db = os.environ["RDS_USERNAME"]
pass_db = os.environ["RDS_PASSWORD"]
host_db = os.environ["RDS_HOSTNAME"]
name_db = os.environ["RDS_DB_NAME"]
email_host=os.environ["SES_EMAIL_HOST"]
email_port=os.environ["SES_EMAIL_PORT"]
email_user=os.environ["SES_EMAIL_HOST_USER"]
email_pass=os.environ["SES_EMAIL_HOST_PASSWORD"]

#variables de entorno DESARROLLO
#Prueba de correo
#email_host = 'smtp.gmail.com'
#email_user = 'supervoices.cloud@gmail.com'
#email_port = 587
#email_pass = ''

#rutas DESARROLLO
#path_media = 'D:/01_ESTUDIOS/MAESTRIA/4_APLICACIONES_CLOUD/Proyecto_1_to_mp3/media/'
#path_procesados = 'D:/01_ESTUDIOS/MAESTRIA/4_APLICACIONES_CLOUD/Proyecto_1_to_mp3/procesados/'

#rutas PRODUCCION
path_media = '/home/ubuntu/media/'
path_procesados = '/home/ubuntu/media/procesados/'

#conexion a la base de datos
try:
	db = psycopg2.connect(host=host_db,database=name_db, user=user_db, password=pass_db)
	#db = sqlite3.connect('archivosmp3.sqlite')
	print("OK conexion establecida!!!!")
	cursor=db.cursor()
except psycopg2.Error as e:
	print(e.pgerror)

#Valida si hay archivos por procesar
cursor.execute(""" SELECT count(archivo_original)
		           FROM "WebConcursos_audiolocutor"
	               WHERE estado = 'En Proceso' """)
for reg in cursor.fetchall():
	print("Archivos a convertir: ", reg[0])

if reg[0]>0:
	print("Cambiando estado para bloqueo de archivos")
	cursor.execute(""" UPDATE "WebConcursos_audiolocutor"
					   SET estado = 'Esperando Conversion',
						   inicio_proceso = '%s'
					   WHERE estado = 'En Proceso' """ %(time.strftime("%d/%m/%y %H:%M:%S")))
	db.commit()
	print("-------------------------------------------------------------")
	print("Convirtiendo archivos WAV a MP3")
	print("-------------------------------------------------------------")
	#se usa la fecha maxima dentro del filtro ya que corresponde a los registros que se bloquearon en la ejecucion del ultimo batchMP3, en el caso
	#de que exista autoescaling y se activen las instancias maximas disponibles
	cursor.execute(""" SELECT archivo_original
					   FROM "WebConcursos_audiolocutor"
					   WHERE estado = 'Esperando Conversion'
					   AND UPPER(archivo_original) LIKE '%.WAV'
					   AND inicio_proceso = (SELECT MAX(inicio_proceso) FROM "WebConcursos_audiolocutor" WHERE estado = 'Esperando Conversion') """)

	for reg in cursor.fetchall():
		print("Archivo WAV en conversion: ", reg[0])
		msplit = reg[0].split(".")
		mp3_file = msplit[0] + '.mp3'
		wav_file = path_media+reg[0]
		sound = pydub.AudioSegment.from_wav(wav_file)
		sound.export(mp3_file, format= "mp3")
		shutil.move(mp3_file, path_media)
		shutil.move(wav_file, path_procesados )
		cursor.execute(""" UPDATE "WebConcursos_audiolocutor"
						   SET estado = 'Convertido',
						       archivo_convertido = '%s'
						   WHERE estado = 'Esperando Conversion'
						   AND archivo_original = '%s' """ %(mp3_file,reg[0]))
		db.commit()

		#envio de correo
		cursor.execute(""" SELECT email FROM "WebConcursos_audiolocutor"
						   WHERE estado = 'Convertido'
						   AND estado_mail = '0'
						   AND archivo_convertido = '%s' """ %(mp3_file))

		lista = cursor.fetchall()
		for indice in lista:
			print("Enviando correo a: ", indice[0])
			smtp = smtplib.SMTP(email_host, email_port)
			remitente = 'supervoices.cloud@gmail.com'
			destinatario = indice[0]
			asunto = "Aviso de procesamiento de audio"
			encabezado = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (remitente, destinatario,asunto)
			email = encabezado + "Hola! Te informamos que tu archivo de audio " + mp3_file + " a sido procesado con exito! "
			smtp.starttls()
			smtp.ehlo()
			try:
				smtp.login(email_user, email_pass)
				print("Conectado smpt para correo")
				smtp.sendmail(remitente, destinatario, email)
				smtp.close()
			except smtplib.SMTPAuthenticationError as e:
				print(e.SMTPAuthenticationError)
			print("Cambiando estado_mail en el archivo", mp3_file)
			cursor.execute(""" UPDATE "WebConcursos_audiolocutor"
							   SET estado_mail = '1'
							   WHERE estado = 'Convertido'
							   AND archivo_convertido = '%s' """ %(mp3_file))
			db.commit()
