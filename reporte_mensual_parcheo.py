#!/usr/bin/env python
#-----------------------------------------------------------
#
# Lee el fichero .csv y calcula si la fecha del ultimo parche es mayor a 90 dias y 180 dias para pre/des.
# Genera un .html con una tabla con los datos e envia un mail informando que se ha generado el archivo.
# Se programa en crontab para que se envie mensualmente.
# Los datos del .csv los genera el script last-rhsa-system.bash
#
#-----------------------------------------------------------

from datetime import datetime,timedelta
import time, csv, locale, os

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# leemos el fichero .csv para sacar los campos:
fichero = open('reporte_'+time.strftime("%Y%m%d")+'.csv','r')
entrada = csv.DictReader(fichero, delimiter=';')
lista_servidores = list(entrada)

hoy = datetime.now()
mes = time.strftime("%B")
anio = time.strftime("%Y")

destinatarios_mail = "ejemplo@mail.com"
envio_mail = "echo 'Se ha generado el reporte mensual con las maquinas a parchear en el mes de "+mes+".\n\nPuedes consultar el informe en: reporte_mensual_"+mes+"_"+anio+".html \n\n\nUn saludo,\n' | mail -s 'Reporte estado actualizaciones servidores Linux - "+mes+"' "+destinatarios_mail+""

# Creamos los diccionarios donde iremos indexando los resultados:
lista_TOTAL_pro = {}
lista_NOK_pro = {}
lista_NOK_des_pre = {}
lista_TOTAL_des_pre = {}

for servidor in lista_servidores:

        if servidor['ENTORNO'] == 'xxP' and servidor['STATUS'] == 'Activo':
                lista_TOTAL_pro[servidor['SERVIDOR']] = [servidor['FECHA'], servidor['INFO']]
        if servidor['ENTORNO'] == 'Dxx' and servidor['STATUS'] == 'Activo':
                lista_TOTAL_des_pre[servidor['SERVIDOR']] = [servidor['FECHA'], servidor['INFO']]
        if servidor['ENTORNO'] == 'xIx' and servidor['STATUS'] == 'Activo':
                lista_TOTAL_des_pre[servidor['SERVIDOR']] = [servidor['FECHA'], servidor['INFO']]

# Cogemos los RedHat antiguos que son siempre fijos.
        if servidor['FECHA'] == '' and servidor['KERNEL'] == '2.4.9-e.57' or servidor['KERNEL'] == '2.6.9-55.0.6.ELsmp':
                lista_TOTAL_pro[servidor['SERVIDOR']] = [servidor['FECHA'], servidor['INFO']]

# Servidores que necesitan parches
        if servidor['FECHA'] != 'System is up to date' and servidor['STATUS'] == 'Activo':
                fecha_parche = datetime.strptime(servidor['FECHA'], "%m/%d/%y")
                diferencia = hoy - fecha_parche

                if diferencia > timedelta(days=90) and servidor['ENTORNO'] == 'xxP':
                        lista_NOK_pro[servidor['SERVIDOR']] = [servidor['INFO'], servidor['FECHA']]

                if diferencia > timedelta(days=180) and servidor['ENTORNO'] == 'xIx':
                        lista_NOK_des_pre[servidor['SERVIDOR']] = [servidor['INFO'], servidor['FECHA']]

                if diferencia > timedelta(days=180) and servidor['ENTORNO'] == 'Dxx':
                        lista_NOK_des_pre[servidor['SERVIDOR']] = [servidor['INFO'], servidor['FECHA']]

# Realizamos los calculos:
total_actualizadas = len(lista_TOTAL_pro) - len(lista_NOK_pro)
porcentaje = (total_actualizadas * 100)/len(lista_TOTAL_pro)
total_actualizadas_des_pre = len(lista_TOTAL_des_pre) - len(lista_NOK_des_pre)
porcentaje_des_pre = (total_actualizadas_des_pre * 100)/len(lista_TOTAL_des_pre)

# Generamos el fichero HTML con la info

plantilla_html = open("plantilla.txt", "r")
cabecera = plantilla_html.read()
plantilla_html.close()

html_file = open("/var/www/html/parches_linux/reporte_mensual_"+mes+"_"+anio+".html", "w")
html_file.write(cabecera)

html_file.write("<h1>Reporte Mensual"+" "+ mes +" "+ anio +"</h1>")
html_file.write("<h3>Produccion</h3>")
html_file.write("<p>Porcentaje maquinas actualizadas: " +str(porcentaje) +"%</p>")
html_file.write("<p>Total maquinas: " + str(len(lista_TOTAL_pro))+"</p>")
html_file.write("<p>Sin actualizar: " + str(len(lista_NOK_pro))+"</p>")
html_file.write("<p>Actualizadas: " + str(total_actualizadas)+"</p>")

html_file.write("<h3>Maquinas sin actualizar en 3 meses:</h3>\n")
html_file.write("<table>\n")
html_file.write("<tr><th>Servidor</th><th>Fecha</th><th>Aplicacion</th></tr>\n")

for servidor, info in lista_NOK_pro.items():
        html_file.write("<tr><td>"+ servidor + "</td><td>" +str(info[1])+"</td><td>"+str(info[0])+"</td></td>\n")

html_file.write("</table>\n")

html_file.write("<h3>Pre/Des</h3>")
html_file.write("<p>Porcentaje maquinas actualizadas: " +str(porcentaje_des_pre) +"%</p>")
html_file.write("<p>Total maquinas: " + str(len(lista_TOTAL_des_pre))+"</p>")
html_file.write("<p>Sin actualizar: " + str(len(lista_NOK_des_pre))+"</p>")
html_file.write("<p>Actualizadas: " + str(total_actualizadas_des_pre)+"</p>")
html_file.write("<h3> Maquinas de DES/PRE sin actualizar en 6 meses: </h3>")
html_file.write("<table>\n")
html_file.write("<tr><th>Servidor</th><th>Fecha</th><th>Aplicacion</th></tr>\n")

for servidor, info in lista_NOK_des_pre.items():
        html_file.write("<tr><td>"+ servidor + "</td><td>" +str(info[1])+"</td><td>"+str(info[0])+"</td></td>\n")

html_file.write("</table>\n</body>\n</html>")
html_file.close()

# Mandamos el mail:
os.system(envio_mail)
