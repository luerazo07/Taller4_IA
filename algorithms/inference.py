"""Punto 5. Inferencia mediante encadenamiento hacia adelante."""
from models.logic import match_premises, substitute


def forward_chain(kb):
    """Retorna una tupla con los hechos originales y derivados, sin duplicados.

    Cada ronda usa los hechos disponibles al comenzarla. La base de entrada
    debe conservarse.
    kb.facts contiene objetos Atom; kb.rules contiene objetos Rule con los
    atributos premises y conclusion. Los hechos se comparan directamente.

    Tips:
    - match_premises(regla.premises, hechos) genera (sustitución, hechos usados).
      Si no hay coincidencias, no genera resultados. La sustitución es un
      diccionario, por ejemplo {'?p': 'ana'}.
    - substitute(regla.conclusion, sustitución) retorna un nuevo objeto Atom
      con las variables reemplazadas por los valores de la sustitución.

Version Inicial 
para la primera version se toma como referencia el Listing 10.5 del libro.
 

def forward_chain(kb):
     hechos = list(kb.facts)
     disponibles = tuple(hechos)
     nuevos = []
     for regla in kb.rules:                                     
         for sustitucion, _ in match_premises(regla.premises,
                                              disponibles):     
             conclusion = substitute(regla.conclusion, sustitucion) 
             if conclusion not in hechos and conclusion not in nuevos:  
                 nuevos.append(conclusion)                      

     hechos.extend(nuevos)       
     return tuple(hechos)                               

Sin embargo al ejecutarla salian errores, y al no saber porque se recurrio a la herramienta de inteligencia artificial generativa: Claude
con el siguiente prompt:
- Mira mi codigo, al ejecutarse sale error, porque?
El agente respondio lo siguiente:

~ Defecto: hace una sola pasada sobre las reglas. Omite el ciclo "repetir ... mientras nuevos no esté vacía" (líneas 2 y 17), así que no deriva conclusiones cuyas premisas son, a su vez, hechos derivados.

Luego de arreglar el defecto encontrado por la herramienta, se procedio a arreglar el codigo y se presenta la version final.
    """
    hechos = []
    for hecho in kb.facts:
        if hecho not in hechos:
            hechos.append(hecho)
    while True:
        disponibles = tuple(hechos)
        nuevos = []
        for regla in kb.rules:
            for sustitucion, _usados in match_premises(regla.premises, disponibles):
                conclusion = substitute(regla.conclusion, sustitucion)
                if conclusion not in hechos and conclusion not in nuevos:
                    nuevos.append(conclusion)
        if not nuevos:
            break
        hechos.extend(nuevos)
    return tuple(hechos)
