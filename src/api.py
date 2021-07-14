#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""api.py: Lanza aplicación que contiene un scheduler experimental para Kubernetes"""

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
logging.basicConfig(filename='app.log', level=logging.DEBUG)

valoresNodoRtt={}   # Almacena globalmente los valores rtt por cada nodo

## Funciones auxiliares


def obtRttaNodo(direccion):
    """
    Obtiene en tiempo real el RTT mediante ping a una dirección ipv4
    Actualmente implementado con el paquete MultiPing
    """
    rttTiempos = MultiPing([direccion])
    rttTiempos.send()  
    rst = rttTiempos.receive(100)
    return rst[0][direccion]



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

    dictAux = {}
    datos = json.loads(request.data)
    
    # Copia del diccionario
    dictAux = dict(datos) ; dictAux.pop('Pod', None)
    
 
    pod = datos['Pod'] ;  
    app.logger.info(' Datos  POD CANTIDATO: ')
    app.logger.info(pod)
    app.logger.info(" Fin de datos POD CANDIDATO")

    ## Si el pod es de namespace kube-system, entonces le ponemos 5000 a rtt y 0 a bandwithRequest
    ## No se producirá filtrado después.

    if pod['metadata']['namespace'] != "kube-system":
         podRtt = obtRttPod(pod)
         podBandwithRequest=obtAnchobandaPod(pod) 
    else:
         podRtt = 5000
         podBandwithRequest = 0         
   
    podName = pod['metadata']['name'] 

    ## Datos procesados en formato json por python y datos en bruto de la petición posst
    app.logger.info(" Procesados") ; app.logger.info( datos)
    app.logger.info(" En bruto ") ; app.logger.info(request.data)
    app.logger.info(" Reprocesados") ; app.logger.info(json.dumps(datos))

    ## Estructuras de datos para la respuesta
    miListaNodosFallidos= {} ;  miListaNodos = []

    app.logger.info(" Comenzando evaluacion de nodos: ")
    for i in dictAux['Nodes']['items']:
        nodeName=i['metadata']['name'] ;  app.logger.info(nodeName) 

	## Aquí hay que hacer esto
        # 1.- Obtener el rttToNode desde el master
        # 2.- Rellenar una estructura con los nodos ordenados de mayor a menor en Rtt
        
        for z in  i['status']['addresses']:
            if ( z['type'] == 'InternalIP'):
                nodeAddress=z['address']
                nodeRtt=obtRttaNodo(nodeAddress)       
        nodeRttMs=nodeRtt*1000
        app.logger.info(" RTT DEL NODO ") ;  app.logger.info(nodeRttMs)
        app.logger.info(" RTT DEL POD ") ;  app.logger.info(podRtt)
        status = "valido" if nodeRttMs <= float(podRtt) else "invalido"
       
        if nodeRttMs <= float(podRtt):
            miListaNodos.append(nodeName)
            valoresNodoRtt[nodeName]=nodeRttMs   # Rellenamos el diccionario con los valores de los nodos validos
        else:
            miListaNodosFallidos[nodeName] = "Rtt del nodo no suficiente para este pod"            

        app.logger.info(" STATUS ") ;  app.logger.info(status)        

    ## Una vez aquí disponemos de los nodos no válidos en miListaNodosFallidos. Debemos hacer esto
    ## 1.- Iterar sobre dicha lista y eliminar los nodos de dictAux
    ## 2.- Si no queda ningún nodo, emitir error rellenando 'Error'

    for dName in miListaNodosFallidos.keys():
        app.logger.info(" Nodo a borrar: ") ;  app.logger.info( dName)

        for i in range(len(dictAux['Nodes']['items'])): 
            app.logger.info(i)
            if dictAux['Nodes']['items'][i]['metadata']['name'] == dName :
                app.logger.info(" Encontrado y borrando!! ") 
                del dictAux['Nodes']['items'][i]
                break
        
    error="" 
    if len(dictAux['Nodes']['items']) == 0 : error = "No hay nodos que cumplan los requerimientos RTT" 
    dictAux['NodeNames'] = miListaNodos
    dictAux['FailedNodes']= miListaNodosFallidos

    dictAux['Error'] = error
 
    app.logger.info(" Datos devueltos desde filter: ") ;  app.logger.info(json.dumps(dictAux))

    return json.dumps(dictAux)

@app.route('/scheduler/prioritize', methods=['GET','POST'])
def prioritize():
    """ Función principal que almacena la lógica para prioritize """ 

    dictAux = {}
    datos = json.loads(request.data)

    pod = datos['Pod'] ;

    ## Si el pod es de namespace diferente a default, entonces le ponemos 5000 a rtt y 0 a bandwithRequest
    ## No se producirá filtrado después.

    if pod['metadata']['namespace'] != "kube-system":
         podRtt = obtRttPod(pod)
         podBandwithRequest=obtAnchobandaPod(pod)
    else:
         podRtt = 5000
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


    ## En esta sección debemos hacer estos puntos: 
    ## 1.- Obtener el valor de bandwidth del nodo y sumar el ocupado por los actuales pods
    ## 2.- Si está lleno sumando el Pod que llega, un 0 como prioridad, de lo contrario el de menor rtt tiene mayor prioridad
    ## 3.- De filter tiene que existir una lista con los nodos ordenados por rtt  de mayor a menor, el de mayor prioridad
    ## será el que menor rtt tenga 
    ## en filter hemos rellenado: valoresNodoRtt

    valoresAnchoBandaActuales={}
    app.logger.info(" Comenzando obtención de datos del nodo: ")
    for i in dictAux['Nodes']['items']:
        nodeName=i['metadata']['name'] ; app.logger.info(nodeName)
        dictAux=i['metadata']['labels']
        try:
            bandwithNode=dictAux['bandwitdhCapacity']
        except KeyError:
            # Si el nodo no tiene esta label, le asignamos ancho de banda infinito=10000 
            bandwithNode=10000
        bandwithNodeAhora=obtAnchobandaNodeAhora(nodeName)
        
        app.logger.info(" Ancho de banda total del nodo  ") ;  app.logger.info(bandwithNode)
        app.logger.info(" Ancho de banda usado ahora mismo por el nodo  ") ;  app.logger.info(bandwithNodeAhora)

        valoresAnchoBandaActuales[nodeName] = (int(bandwithNode) - bandwithNodeAhora)

    ## En este punto tenemos rellenados valoresNodoRtt y ValoresAnchoBandaActuales
    ## Usaremos max(stats, key=stats.get) para obtener el valor máximo de cada cual.
    app.logger.info(" Valores Ancho Banda actuales  ") ;  app.logger.info(valoresAnchoBandaActuales)
    app.logger.info(" Valores Nodo Rtt  ") ;  app.logger.info(valoresNodoRtt)

    
    prioridadActual=10
    dictRespuesta={}

    while valoresNodoRtt:
        nodoTrabajo=min(valoresNodoRtt,key=valoresNodoRtt.get)
        app.logger.info(" Nodo Mayor ahora  ") ;  app.logger.info(nodoTrabajo)

	## Calculamos lo siguiente
	## Si no tiene ancho de banda disponible, lo eliminamos de las prioridades sin hacer otra cosa
        ## Sólo queremos premiar
       	    
	## Si tiene ancho de banda, le damos prioridad actual , lo incluimos en la estructura de respuesta y lo eliminamos también
        ## Aquí hay que andarse finos con la prioridad, de momento restamos -1 hasta tener una idea más clara de las prioridades


        if not (int(podBandwithRequest) > valoresAnchoBandaActuales[nodoTrabajo] or valoresAnchoBandaActuales[nodoTrabajo] < 0 ) : 
            dictRespuesta[nodoTrabajo] = prioridadActual
            prioridadActual= prioridadActual-1
	
        del valoresNodoRtt[nodoTrabajo] # siempre borramos

    app.logger.info(" Contenido de prioridades asignadas  ") ;  app.logger.info(dictRespuesta)

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
