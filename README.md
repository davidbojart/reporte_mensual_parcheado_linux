# reporte_mensual_parcheado_linux
Lee el fichero .csv y calcula si la fecha del ultimo parche es mayor a 90 dias y 180 dias para pre/des. Genera un .html con una tabla con los datos e envia un mail informando que se ha generado el archivo. Se programa en crontab para que se envie mensualmente. Los datos del .csv los genera el script last-rhsa-system.bash que saca los datos de Red-Hat Satellite.
