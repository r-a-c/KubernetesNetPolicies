#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""api.py: Lanza aplicación que contiene un scheduler experimental para Kubernetes basado en NAS (Network Aware Scheduler)"""

__author__      = "Raúl Álvarez de Celis"
__copyright__   = "Copyright 2021"
__license__ = "GPL"
__version__ = "1.0.1"
__email__ = "contacto at racpfg.com"
__status__ = "Development"


import flask, json, logging
from multiping import MultiPing
from flask import request 
from kubernetes import client, config

app = flask.Flask(__name__)
app.config["DEBUG"] = True
logging.basicConfig(filename='app.nas.log', level=logging.DEBUG)

valoresNodoRtt={}   # Almacena globalmente los valores rtt por cada nodo

## Funciones auxiliares

def obtAnchobandaPod(pod):
    """
    Abstrae la obtención del ancho de banda requerido por un pod. Utilizamos un try/catch porque 
    con él comprobamos las 3 keys a la vez en caso de que falle alguna. El valor en ese caso es 0
    """
    try:
         return pod['metadata']['labels']['bandwitdthRequest']
    except KeyError:
         return 0


def obtAnchobandaNodeAhora(nodeName):
    """
 Obtiene el valor total de ancho de banda usado en el nodo. En esta función usamos el cliente en python 
 de kubernetes porque no se puede obtener el dato desde los datos que llegan desde el scheduler.

 V1PodList list_pod_for_all_namespaces(allow_watch_bookmarks=allow_watch_bookmarks,_continue=_continue,
 field_selector=field_selector, label_selector=label_selector, limit=limit,
 pretty=pretty, resource_version=resource_version, timeout_seconds=timeout_seconds, watch=watch)

 El equivalente a kubectl get pods  -o wide --field-selector spec.nodeName=node02.racpfg.com -o json

    """
    config.load_kube_config()
    v1=client.CoreV1Api()
    field_selector = 'spec.nodeName='+nodeName
    datos=v1.list_pod_for_all_namespaces(watch=False,field_selector=field_selector)


    totalUsado=0
    for i in datos.items:
        app.logger.info(' i.metadata.name')
        app.logger.info(i.metadata.name)
        #print (i.metadata.name)
        namespace=i.metadata.namespace
        if namespace != "kube-system":
            app.logger.info('NameSpace')
            app.logger.info(namespace)
            #print(namespace)
            try:
                dictAuxLabels=i.metadata.labels
                totalUsado=totalUsado+int(dictAuxLabels['bandwitdthRequest'])
            except KeyError:
                pass

    return totalUsado

def obtRttPod(pod):
    """
    Abstrae la obtención del rtt requerido por un pod. Usamos try/catch para evitar comprobación de las 3 keys.
    Si falla una devolvemos 10000
    """
    try:
        return pod['metadata']['labels']['rtt']
    except KeyError:
        return 10000

## Procesamiento de rutas

@app.route('/', methods=['GET'])
def home():
    """ Funcion dummy que muestra un mensaje de prueba """
    return "<h1>My Test</p>"

@app.route('/scheduler/filter', methods=['GET','POST'])
def filter():
    """ Funcion principal que almacena la logica para Filter """
    """ En este modelo, filter elimina todos los nodos salvo 1"""
    dictAux = {}
    datos = json.loads(request.data)
    
    # Copia del diccionario
    dictAux = dict(datos) ; dictAux.pop('Pod', None)
    
 
    pod = datos['Pod'] ; app.logger.info(' Datos  POD CANTIDATO: ') ;  app.logger.info(pod) ;    app.logger.info(" Fin de datos POD CANDIDATO")
    podName = pod['metadata']['name'] 

    ## Datos procesados en formato json por python y datos en bruto de la petición posst
    app.logger.info(" Procesados") ; app.logger.info( datos) ;    app.logger.info(" En bruto ") ; app.logger.info(request.data)
    app.logger.info(" Reprocesados") ; app.logger.info(json.dumps(datos))

    ## Si el pod es de namespace diferente a default, entonces le ponemos 5000   a bandwithRequest
    ## No se producirá filtrado después.

    if pod['metadata']['namespace'] != "kube-system":
         podBandwithRequest=obtAnchobandaPod(pod)
    else:
         podBandwithRequest = 0

    app.logger.info(' Datos  POD CANTIDATO peticion bandwith: ') ;  app.logger.info(podBandwithRequest) 


    ## Estructuras de datos para la respuesta
    miListaNodosFallidos= {} ;  miListaNodos = []

    app.logger.info(" Comenzando obtencion de rtt  de nodos: ")
    for i in dictAux['Nodes']['items']:
        nodeName=i['metadata']['name'] ;  app.logger.info(nodeName) 
        rttNodo=i['metadata']['labels']['rtt'] ;  app.logger.info("Rtt estático del nodo");app.logger.info(rttNodo)
	## Aquí hay que hacer esto
        # 1.- Obtener el rtt del dato del label del nodo.
        # 2.- Rellenar una estructura con los nodos ordenados de mayor a menor en Rtt
        
        #miListaNodos.append(nodeName)
        valoresNodoRtt[nodeName]=rttNodo   # Rellenamos el diccionario con los valores de los nodos, todos válidos en esta ocasión.


    valoresAnchoBandaActuales={}
    app.logger.info(" Comenzando obtención de datos de ancho de banda del nodo: ")
    for i in dictAux['Nodes']['items']:
        nodeName=i['metadata']['name'] ; app.logger.info(nodeName)
        dictAux2=i['metadata']['labels']
        try:
            bandwithNode=dictAux2['bandwitdhCapacity']
        except KeyError:
            # Si el nodo no tiene esta label, le asignamos ancho de banda infinito=10000 
            bandwithNode=10000
        bandwithNodeAhora=obtAnchobandaNodeAhora(nodeName)
        
        app.logger.info(" Ancho de banda total del nodo  ") ;  app.logger.info(bandwithNode)
        app.logger.info(" Ancho de banda usado ahora mismo por el nodo  ") ;  app.logger.info(bandwithNodeAhora)

        valoresAnchoBandaActuales[nodeName] = (int(bandwithNode) - bandwithNodeAhora)

    ## En este punto tenemos rellenados valoresNodoRtt y ValoresAnchoBandaActuales
    ## Usaremos max(stats, key=stats.get) para obtener el valor máximo de cada cual posteriormente.
    app.logger.info(" Valores Ancho Banda actuales restantes en los nodos ") ;  app.logger.info(valoresAnchoBandaActuales)
    app.logger.info(" Valores Nodo Rtt estáticos  ") ;  app.logger.info(valoresNodoRtt)



    while valoresNodoRtt:
        nodoTrabajo=min(valoresNodoRtt,key=valoresNodoRtt.get)
        app.logger.info(" Nodo Mayor ahora con menor rtt  ") ;  app.logger.info(nodoTrabajo)

        ## Calculamos lo siguiente
        ## Si no tiene ancho de banda disponible, lo eliminamos
        ## Sólo vamos a devolver 1

        if not (int(podBandwithRequest) > valoresAnchoBandaActuales[nodoTrabajo] or valoresAnchoBandaActuales[nodoTrabajo] < 0 ) :
            miListaNodos.append(nodoTrabajo)
            del valoresNodoRtt[nodoTrabajo] 
            break
        miListaNodosFallidos[nodoTrabajo] = "Eliminado"
        del valoresNodoRtt[nodoTrabajo] # siempre borramos

    # Ahora marcamos todos los demas para borrar
    while valoresNodoRtt:
        nodoTrabajo=min(valoresNodoRtt,key=valoresNodoRtt.get)
        miListaNodosFallidos[nodoTrabajo] = "Eliminado"
        del valoresNodoRtt[nodoTrabajo] # siempre borramos


    for dName in miListaNodosFallidos.keys():
        app.logger.info(" Nodo a borrar: ") ;  app.logger.info( dName)

        for i in range(len(dictAux['Nodes']['items'])):
            app.logger.info(i)
            if dictAux['Nodes']['items'][i]['metadata']['name'] == dName :
                app.logger.info(" Encontrado y borrando!! ")
                del dictAux['Nodes']['items'][i]
                break

    error="" 
    if len(dictAux['Nodes']['items']) == 0 : error = "No hay nodos" 
    dictAux['NodeNames'] = miListaNodos
    dictAux['FailedNodes']= miListaNodosFallidos

    dictAux['Error'] = error
    app.logger.info(" miListaNodos, nodo elegido entre todos: "); app.logger.info( miListaNodos) 
    app.logger.info(" Datos devueltos desde filter: ") ;  app.logger.info(json.dumps(dictAux))

    return json.dumps(dictAux)

@app.route('/scheduler/prioritize', methods=['GET','POST'])
def prioritize():
    """ Función principal que almacena la lógica para prioritize , nunca se llega a ejecutar"""

    dictAux = {}
    datos = json.loads(request.data)

    pod = datos['Pod'] ;

    ## Si el pod es de namespace diferente a default, entonces le ponemos 5000   a bandwithRequest
    ## No se producirá filtrado después.

    if pod['metadata']['namespace'] != "kube-system":
         podBandwithRequest=obtAnchobandaPod(pod)
    else:
         podBandwithRequest = 0

    podName = pod['metadata']['name']


    # Copia del diccionario
    dictAux = dict(datos)

    ## Datos procesados en formato json por python y datos en bruto de la petición posst

    app.logger.info(" Procesados PRIORITIZE ") ;  app.logger.info(datos)
    app.logger.info(" En bruto PRIORITIZE ") ;  app.logger.info(request.data)
    app.logger.info(" Reprocesados PRIORITIZE ") ;  app.logger.info(json.dumps(datos))

    ## Estructura de retorno, una lista de esto
    ## // HostPriority represents the priority of scheduling to a particular host, higher priority is better.
    ##   type HostPriority struct {
    ##    Host string
    ##  Score int }


    prioridadActual=10
    dictRespuesta={}

    while valoresNodoRtt:
        nodoTrabajo=min(valoresNodoRtt,key=valoresNodoRtt.get)
        app.logger.info(" Nodo Mayor ahora con menor rtt  ") ;  app.logger.info(nodoTrabajo)

	## Calculamos lo siguiente
	## Si no tiene ancho de banda disponible, lo eliminamos 
        ## Sólo vamos a devolver 1
       	    
	## Si tiene ancho de banda, le damos prioridad 10 , lo incluimos en la estructura de respuesta y salimos. Sólo devolvemos 1


        if not (int(podBandwithRequest) > valoresAnchoBandaActuales[nodoTrabajo] or valoresAnchoBandaActuales[nodoTrabajo] < 0 ) : 
            dictRespuesta[nodoTrabajo] = prioridadActual
            break	
        del valoresNodoRtt[nodoTrabajo] # siempre borramos

    app.logger.info(" Contenido de prioridades asignadas, solo uno debe tener  ") ;  app.logger.info(dictRespuesta)

    #nodePriorityList={}
    #for i in dictRespuesta.keys():
    #     nodePriorityList[i] = dictRespuesta[i]
 
    nodePriorityList=[]
    for i in dictRespuesta:
         aux={}
         aux[i]=dictRespuesta[i]
         nodePriorityList.append(aux)

    app.logger.info(" Node priority list") ; app.logger.info(nodePriorityList)
    app.logger.info(" Node priority list json dumps") ; app.logger.info(json.dumps(nodePriorityList))
    return json.dumps(nodePriorityList)


if __name__ == '__main__':

    app.run(port=12346,host='0.0.0.0')

