#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Lee y procesa los archivos de statistics.json"""

import glob,os, json, math
diccionarioConDatos={}


##https://kodify.net/python/math/truncate-decimals/#truncate-values-in-python-to-a-certain-number-of-decimals
def truncate(number, decimals=2):
    """
    Returns a value truncated to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor



cabecera = """ \\begin{table}[h!]
	\\centering
	\\caption{Resultados Lanzamiento X para XXx}
	\\label{tab:tableXXX-LX}
\\begin{tabular}{|l|cccc|cc|c|}
			\\hline
        & \\multicolumn{4}{c|}{Tiempos de Respuesta} & \\multicolumn{2}{c|}{Ejecuciones} & Rend    \\\\
        & Media      & Min     & Max     & Med     & NºEje            & F            & Trans/s \\\\
        		\\hline"""


pie = """\\end{tabular}
\\end{table} """


for root, dirs, files in os.walk("./"):
    for file in files:
        if file.endswith("statistics.json"):
             correspondea=root.replace('./htmlresultados','')
             correspondea=correspondea.split('-')
             epigrafe="L"+correspondea[1]+" "+correspondea[0]
             lanzamiento=correspondea[1]
             numusuarios=correspondea[0]
             try:
                 test = diccionarioConDatos[lanzamiento]
             except KeyError:
                 diccionarioConDatos[lanzamiento] = {}
             #print(epigrafe)
             #print(os.path.join(root, file))
             #Comenzando procesado de json
             with open(os.path.join(root, file)) as json_file:
                  contenido=json.load(json_file)
                  datosProcesar=contenido["Total"]
                  #print(datosProcesar)
                  dictAux={}
                  dictAux['media'] =datosProcesar['meanResTime']
                  dictAux['min']   =datosProcesar['minResTime']
                  dictAux['max']   =datosProcesar['maxResTime']
                  dictAux['mediana']=datosProcesar['medianResTime']
                  dictAux['numEje'] =datosProcesar['sampleCount']
                  dictAux['f'] =datosProcesar['errorCount']
                  dictAux['transs'] = datosProcesar['throughput']
                  diccionarioConDatos[lanzamiento][numusuarios] = dictAux 


#Aquí tenemos todos los datos en el diccionario
#print (diccionarioConDatos)
#Media      & Min     & Max     & Med     & NºEje            & F            & Trans/s
nLan=(os.path.basename(os.path.normpath(os.getcwd()))).upper() 

#for x in range(1, 5):
#        for  z in ("100","500","1000","2000"):
#            mdic= diccionarioConDatos[str(x)][z]
#            media=str(truncate(mdic['media'])) ;     min=str(truncate(mdic['min'])) ;    max=str(truncate(mdic['max']))
#            median=str(truncate(mdic['mediana'])) ;    numej=str(truncate(mdic['numEje'])) ;    ff=str(math.trunc(mdic['f']))
#            trans=str(truncate(mdic['transs']))
#            print(nLan+" "+str(x)+" "+z+" & "+media+" & "+min+" & "+max+" & "+median+" & "+numej+" & "+ff+" & "+trans+" \\\ " )
#        print("\hline")

print(cabecera)
for z in ("100","500","1000","2000"):
        totMedias=0
        totTranss=0
        for  x in range(1, 5):
            mdic= diccionarioConDatos[str(x)][z]
            media=str(truncate(mdic['media'])) ;     min=str(truncate(mdic['min'])) ;    max=str(truncate(mdic['max']))
            median=str(truncate(mdic['mediana'])) ;    numej=str(math.trunc(mdic['numEje'])) ;    ff=str(math.trunc(mdic['f']))
            trans=str(truncate(mdic['transs']))
            totMedias=totMedias+mdic['media']
            totTranss=totTranss+mdic['transs']
            print(nLan+" "+str(x)+" "+z+" & "+media+" & "+min+" & "+max+" & "+median+" & "+numej+" & "+ff+" & "+trans+" \\\ " )
        totTranss=totTranss/4
        totMedias=totMedias/4
        print("Medias  &  "+str(truncate(totMedias))+"    &         &         &         &                  &              &    "+str(truncate(totTranss))+"     \\\ ")
        print("\hline")

print(pie)
