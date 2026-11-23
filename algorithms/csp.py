"""Puntos 1–3. Retroceso, consistencia de arcos y heurísticas."""
from collections import deque
from models.csp import SearchTrace, copy_domains


def backtracking_search(csp, domains=None, select_variable=None,
                        order_values=None, trace=None):
    """Punto 1: retorna {tarea: franja} o None si no hay solución.

    Entradas: csp representa el problema; domains contiene los dominios vigentes,
    reducidos por AC-3 cuando corresponde.
    csp.variables contiene los identificadores de las tareas, en orden.
    domains es {tarea: [franjas enteras]}; assignment es {tarea: franja}.
    El bloque por completar define expand(assignment).

    Tips:
    - choose(csp, assignment, domains) retorna una tarea pendiente;
      ordered(csp, x, assignment, domains) retorna sus valores en orden.
    - consistent(x, valor, assignment) retorna si el candidato es compatible
      con la asignación parcial; es el comprobador suministrado para este bloque.
    - search(nueva_asignacion) es la llamada recursiva suministrada. Recibe
      una asignación independiente y retorna una solución completa o None.
    """
    trace = trace if trace is not None else SearchTrace(False)
    domains = copy_domains(csp.domains if domains is None else domains)
    choose = select_variable or (lambda p, a, d: next(x for x in p.variables if x not in a))
    ordering = order_values or (lambda p, x, a, d: list(d[x]))

    # Registra las decisiones y los cambios de la búsqueda.
    def snapshot(assignment):
        return {x: [assignment[x]] if x in assignment else list(domains[x])
                for x in csp.variables}

    def ordered(problem, variable, assignment, current_domains):
        values = ordering(problem, variable, assignment, current_domains)
        trace.record('select', f'Elegir {variable}. Orden de valores: {values}.',
                     assignment, snapshot(assignment) if trace.enabled else domains, variable)
        return values

    def consistent(variable, value, assignment):
        current = snapshot(assignment) if trace.enabled else domains
        trace.attempt(assignment, current, variable, value)
        valid = csp.consistent(variable, value, assignment)
        if valid and trace.enabled:
            child = {**assignment, variable: value}
            trace.record('assign', f'Asignar {variable} a la franja {value}.',
                         child, snapshot(child), variable, value)
        elif not valid:
            trace.record('reject', 'El valor entra en conflicto con una tarea asignada.',
                         assignment, current, variable, value)
        return valid

    def search(assignment):
        result = expand(assignment)
        if result is None and len(assignment) < len(csp.variables):
            trace.fail(assignment, snapshot(assignment) if trace.enabled else domains)
            if assignment and trace.enabled:
                variable = next(reversed(assignment))
                parent = {x: v for x, v in assignment.items() if x != variable}
                trace.restore(parent, snapshot(parent), variable)
        return result

      
      #Este es el código que le mandé a Claude
      
      #def expand (assignment):
            #if len(assignment)==len(csp.variables):
             # return assignment
            #x=choose(csp, assignment, domains)
            #for v in ordered (csp, x, assignment, domains):
              #if consistent(x, v, assignment):
                #nueva=copy(assignment)
                #resultado=search(nueva)
                #if resultado is not None:
                  #return resultado
            #return None
            
      #Y me respondió esto:
      #nueva=copy(assignment) no agrega x = v. Copias la asignación, pero nunca le pones el valor que acabas de validar. Entonces search(nueva) recibiría la misma asignación de antes, y choose devolvería otra vez la misma x: recursión infinita. Además, copy no está importado.
      #Entonces eso fue lo  que corregí en mi código
      
    def expand (assignment):
      if len(assignment)==len(csp.variables):
        return assignment
      x=choose(csp, assignment, domains)
      for v in ordered (csp, x, assignment, domains):
        if consistent(x, v, assignment):
          nueva=assignment.copy()
          nueva[x]=v
          resultado=search(nueva)
          if resultado is not None:
            return resultado
      return None
            
    # FIN DEL BLOQUE DEL ESTUDIANTE

    return search({})


def revise(csp, x, y, domains):
    """Punto 2: revisa X→Y modificando domains[x].

    Retorna True únicamente si cambia ese dominio; False en caso contrario.

    Tips:
    - x e y son identificadores de tareas; domains[x] y domains[y] son listas.
    - csp.compatible(x, valor_x, y, valor_y) comprueba las restricciones
      entre ese par de tareas, respetando la dirección de las precedencias.
    - Si elimina elementos mientras recorre una lista, itere sobre una copia.
    """
  
  #Este es el código que le mandé a Claude
  
  #cambio=False
  #for vx in list(domains[x]):
    #soporte=False
    #for vy in domains[y]:
      #if csp.compatible(x, vx, y, vy):
        #soporte=True
        #break
    #if not soporte:
      #domains[x].remove(vx)
      #cambio=True
  #return cambio
      
    #y me respondió .delete(vx) no existe en las listas. El método de la clase list para quitar un valor es .remove(vx).
    #entonces corregí eso
  
    cambio=False
    for vx in list(domains[x]):
      soporte=False
      for vy in domains[y]:
        if csp.compatible(x, vx, y, vy):
          soporte=True
          break
      if not soporte:
        domains[x].remove(vx)
        cambio=True
    return cambio
    # FIN DEL BLOQUE DEL ESTUDIANTE


def ac3(csp, domains):
    """Punto 2: reduce domains; retorna False si detecta un dominio vacío.

    Un retorno True indica consistencia de arcos, no garantiza una solución.

    Tips:
    - Cada arco es un par (x, y) de identificadores de tareas.
      csp.neighbors[x] contiene los vecinos de x.
    - revise(csp, x, y, domains) retorna si modificó domains[x].
    """
    """
    Este es el código que le mandé a Claude
    
    cola=[]
    for x in csp.variables:
      for y in csp.neighbors[x]:
        cola.append((x,y))
    while len(cola)>0:
      (x,y)=cola.pop(0)
      if revise(csp, x,y,domains):
        if domains[x].isempty():
          return False
        for z in csp.neighbors[x]:
          cola.insert(cola,(z,x))
    return True
    
    me dijo que
    
    1. domains[x].isempty(): las listas no tienen ese método. Se usa len(domains[x]) == 0 o not domains[x].
    2. Falta z != y. El pseudocódigo (línea 9) solo agrega los vecinos distintos de y.
    3. cola.insert(cola,(z,x)) está mal: insert es un método de list que pide una posición. Para agregar al final se usa cola.append((z, x)).
    
    entonces hice esos cambios
    """
    cola=[]
    for x in csp.variables:
      for y in csp.neighbors[x]:
        cola.append((x,y))
    while len(cola)>0:
      (x,y)=cola.pop(0)
      if revise(csp, x,y,domains):
        if len(domains[x])==0:
          return False
        for z in csp.neighbors[x]:
          if z!=y:
            cola.append((z,x))
    return True
  
    # FIN DEL BLOQUE DEL ESTUDIANTE


def select_unassigned_variable(csp, assignment, domains):
    """Punto 3: retorna el identificador de la variable elegida por MRV y grado.

    Tips:
    - csp.consistent(x, valor, assignment) comprueba si un candidato es
      compatible con la asignación parcial. Los dominios deben conservarse.
    - csp.neighbors[x] contiene sus vecinos; csp.variables conserva el orden
      original para los desempates.
    
    Esta fue mi version original
    
    mejorLlave = None
    mejorVar = None
    for i,var in enumerate(csp.variables):
      if var in assignment:
          continue
      legales = [v for v in domains[var] if csp.consistent(var,v,assignment)]
      vecinos = csp.neighbors(var)
      llave = (len(legales),-vecinos,i)
      
      if mejorLlave is None or llave < mejorLlave:
        mejorVar = var
        mejorLlave = llave
        
    return mejorVar
    
    a partir de aqui le pedi a la IA de Claude que revisara mi codigo para verificar que errores podia tener y que cosas podia mejorar, su respuesta fue la siguiente:
    
    Tu versión está casi lista, la lógica es correcta. Tiene dos errores.

    1. csp.neighbors(var) con paréntesis. Los tips dicen csp.neighbors[x], o sea con corchetes: es un diccionario, no una función. Con paréntesis te da TypeError.

    2. vecinos no es un número. Aunque arregles los corchetes, csp.neighbors[var] es la lista de vecinos, y -vecinos sobre una lista también revienta. Necesitas contar solo los que no están en assignment. 
    
    Lo que está bien y no lo toques:

    El filtro de legales con domains[var] y csp.consistent.
    La llave (len(legales), -vecinos, i) y la comparación llave < mejorLlave.
    Iniciar con None y el chequeo mejorLlave is None.    
    
    Una vez entendi esto procedi a realizar los cambios y esta fue mi version final:
    
    """
    
    mejorLlave = None
    mejorVar = None
    for i,var in enumerate(csp.variables):
      if var in assignment:
          continue
      legales = [v for v in domains[var] if csp.consistent(var,v,assignment)]
      vecinos = len([n for n in csp.neighbors[var] if n not in assignment])
      llave = (len(legales),-vecinos,i)
      
      if mejorLlave is None or llave < mejorLlave:
        mejorVar = var
        mejorLlave = llave
          
    return mejorVar
    # FIN DEL BLOQUE DEL ESTUDIANTE

def order_domain_values(csp, variable, assignment, domains):
    """Punto 3: retorna los valores compatibles ordenados por LCV.

    Retorne una lista nueva sin modificar domains y conserve el orden original
    en los empates.

    Tips:
    - Use valores de domains compatibles con assignment, tanto para los
      candidatos como para los vecinos pendientes; compruébelos con
      csp.consistent(x, valor, assignment).
    - csp.compatible(variable, valor, vecino, valor_vecino) comprueba cada par
      sin modificar los dominios.
    
    esta fue mi version inicial del codigo

    candidatos = [v for v in domains[variable] if csp.consistent(variable, v, assignment)]
    descartados = 0
    for v in candidatos:
      for y in csp.neighbors[variable]:
        if y in assignment:
          continue
        for w in domains[y]:
          if not csp.compatible(variable, v, y, w):
            descartados += 1
            
            
            
    En este momento decidi pedirle a la IA de Claude que me diera un poco de orientación pues no tenia del todo claro como manejar el tema de los descartados y el retorno de la funcion, su respuesta fue la siguiente:
    
    Vas bien con la estructura (candidatos, vecinos sin asignar, csp.compatible), pero tiene dos errores y le falta el cierre.

    1. descartados es uno solo para todos los candidatos. Lo inicializas una vez antes del for v, entonces va acumulando: el conteo del segundo candidato incluye el del primero. LCV necesita un número por cada v. Hay dos formas:

    Un diccionario descartados = {} y asignas descartados[v] = ... al terminar cada candidato.
    Reiniciar el contador en 0 dentro del for v, y guardar el par (descartados, v) al final de cada vuelta.

    2. Estás contando todos los w de domains[y]. El enunciado dice que de los vecinos cuentes solo los valores compatibles con la asignación parcial. Entonces el for w debe filtrar primero con el mismo csp.consistent que ya usaste, pero aplicado al vecino:

    python
    for w in domains[y]:
        if not csp.consistent(y, w, assignment):
            continue
        ...

    Piensa por qué: un w que ya choca con la asignación actual no es un valor que v "te quite", porque ese valor ya estaba perdido.

    3. Falta el final. Después del conteo, tienes que devolver una lista nueva de candidatos ordenada de menor a mayor por descartados. Con sorted(candidatos, key=...) te sirve, y como sorted es estable, los empates conservan el orden original sin que hagas nada más.
    Eso sí, candidatos ya sale en el orden de domains[variable], que es lo que quieres conservar.
    
    Una vez entendido esto, esta fue mi version final del codigo:
        """

    candidatos = [v for v in domains[variable] if csp.consistent(variable, v, assignment)]
    descartados = {}
    for v in candidatos:
      descartados[v] = 0
      for y in csp.neighbors[variable]:
        if y in assignment:
          continue
        for w in domains[y]:
          if not csp.consistent(y, w, assignment):
                      continue
          if not csp.compatible(variable, v, y, w):
            descartados[v] += 1
    return sorted(candidatos, key=lambda v: descartados[v])
    # FIN DEL BLOQUE DEL ESTUDIANTE
    
    
    
