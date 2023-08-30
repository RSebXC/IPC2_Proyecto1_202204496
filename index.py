import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from graphviz import Digraph

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.length = 0

    def insert(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.length += 1

    def exists(self, data):
        current = self.head
        while current:
            if current.data == data:
                return True
            current = current.next
        return False

    def __getitem__(self, index):
        current = self.head
        count = 0
        while current:
            if count == index:
                return current.data
            count += 1
            current = current.next
        raise IndexError("Index out of range")

    def __setitem__(self, index, data):
        current = self.head
        count = 0
        while current:
            if count == index:
                current.data = data
                return
            count += 1
            current = current.next
        raise IndexError("Index out of range")
    
    def __len__(self):
        return self.length

def imprimir_matriz(matriz):
    for fila in matriz:
        fila_str = ' '.join(map(str, fila))
        print(fila_str)


def imprimir_grupos(grupos):
    for grupo_num, filas in grupos.items():
        filas_str = ', '.join(map(str, filas))
        print(f"Grupo {grupo_num}: Filas [{filas_str}]")


def cargar_archivo():
    tree = ET.parse('prueba.xml')
    root = tree.getroot()

    max_amplitud = 0
    max_tiempo = 0

    for elemento in root.findall('senal'):
        for item in elemento.findall('dato'):
            tiempo = int(item.get('t'))
            amplitud = int(item.get('A'))

            max_amplitud = max(max_amplitud, amplitud)
            max_tiempo = max(max_tiempo, tiempo)

    matriz = LinkedList()
    for _ in range(max_tiempo):
        fila = LinkedList()
        for _ in range(max_amplitud):
            fila.insert(0)
        matriz.insert(fila)

    for elemento in root.findall('senal'):
        for item in elemento.findall('dato'):
            tiempo = int(item.get('t')) - 1
            amplitud = int(item.get('A')) - 1
            valor = int(item.text)
            fila = matriz[tiempo]
            fila[amplitud] = valor

    return matriz

def aplicar_umbral(matriz):
    matriz_umbral = LinkedList()
    for fila in matriz:
        fila_umbral = LinkedList()
        for valor in fila:
            fila_umbral.insert(1 if valor > 0 else 0)
        matriz_umbral.insert(fila_umbral)
    print(matriz_umbral)
    return matriz_umbral

def agrupar_filas(matriz_umbral):
    grupos = {}
    fila_indices = {} 
    
    for fila_num, fila in enumerate(matriz_umbral):
        fila_str = ''.join(map(str, fila))
        if fila_str in fila_indices:
            grupo_id = fila_indices[fila_str]
            grupos[grupo_id].append(fila_num)
        else:
            nuevo_grupo_id = len(grupos) + 1
            grupos[nuevo_grupo_id] = [fila_num]
            fila_indices[fila_str] = nuevo_grupo_id
            
    return grupos

def sumar_valores_por_grupo(matriz_valores, grupos):
    valores_agrupados = LinkedList()
    num_columnas = len(matriz_valores[0])
    
    for grupo_num, filas in grupos.items():
        suma_grupo = [0] * num_columnas
        for fila_num in filas:
            suma_grupo = [a + b for a, b in zip(suma_grupo, matriz_valores[fila_num])]
        valores_agrupados.insert(suma_grupo)
        
    return valores_agrupados

def guardar_en_xml(filename, matriz_valores, grupos, valores_agrupados):
    root = ET.Element('senalesReducidas')

    for grupo_num, filas in grupos.items():
        atributos_grupo = {'nombre': f'Grupo {grupo_num + 1}'}
        grupo = ET.SubElement(root, 'senal', atributos_grupo)
        grupo.set('A', str(len(matriz_valores[0])))
        grupo.set('a', str(grupo_num + 1))

        grupo_element = ET.SubElement(grupo, 'grupo', g=str(grupo_num + 1))
        tiempos_element = ET.SubElement(grupo_element, 'tiempos')
        tiempos_element.text = ','.join(str(fila + 1) for fila in filas)

        datos_grupo_element = ET.SubElement(grupo_element, 'datosGrupo')
        for amplitud, valor in enumerate(valores_agrupados[grupo_num - 1]):
            dato_element = ET.SubElement(datos_grupo_element, 'dato', A=str(amplitud + 1))
            dato_element.text = str(valor)

    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    with open(filename, "w", encoding="utf-8") as xml_file:
        xml_file.write(pretty_xml)

def generar_grafica_matriz_original(matriz, titulo):
    dot = Digraph(titulo)
    dot.attr(rankdir='TB')

    dot.node('inicio', titulo, shape='ellipse')

    t_filas = LinkedList()
    t_filas.insert(len(matriz))
    dot.node('t_filas', label=f't={t_filas.head.data}', shape='ellipse')
    dot.edge('inicio', 't_filas')

    A_columnas = LinkedList()
    A_columnas.insert(len(matriz[0]))
    dot.node('A_columnas', label=f'A={A_columnas.head.data}', shape='ellipse')
    dot.edge('inicio', 'A_columnas')

    for i in range(A_columnas.head.data):
        columna_node_ids = LinkedList()
        for j in range(t_filas.head.data):
            node_id = f'fila_{j}_col_{i}'
            label = LinkedList()
            label.insert(str(matriz[j][i]))
            dot.node(node_id, label=label.head.data, shape='ellipse', style='filled', fillcolor='white')
            columna_node_ids.insert(node_id)

        dot.edge('inicio', columna_node_ids.head.data)

        current_node = columna_node_ids.head
        while current_node.next:
            dot.edge(current_node.data, current_node.next.data)
            current_node = current_node.next

    dot.view()

def generar_grafica_valores_agrupados(valores_agrupados, titulo):
    dot = Digraph(titulo)
    dot.attr(rankdir='TB')

    dot.node('inicio', titulo, shape='ellipse')

    t_grupos = LinkedList()
    t_grupos.insert(len(valores_agrupados))
    dot.node('t_grupos', label=f'Grupos={t_grupos.head.data}', shape='ellipse')
    dot.edge('inicio', 't_grupos')

    A_columnas = LinkedList()
    A_columnas.insert(len(valores_agrupados[0]))
    dot.node('A_columnas', label=f'A={A_columnas.head.data}', shape='ellipse')
    dot.edge('inicio', 'A_columnas')

    for i in range(A_columnas.head.data):
        columna_node_ids = LinkedList()
        for j in range(t_grupos.head.data):
            node_id = f'grupo_{j}_col_{i}'
            label = LinkedList()
            label.insert(str(valores_agrupados[j][i]))
            dot.node(node_id, label=label.head.data, shape='ellipse', style='filled', fillcolor='white')
            columna_node_ids.insert(node_id)

        dot.edge('inicio', columna_node_ids.head.data)

        current_node = columna_node_ids.head
        while current_node.next:
            dot.edge(current_node.data, current_node.next.data)
            current_node = current_node.next

    dot.view()

def procesar_archivo():
    print("Procesando archivo...")

def escribir_archivo_salida():
    print("Escribiendo archivo de salida...")

def mostrar_datos_estudiante():
    print("Nombre: Rodrigo Sebastian Castro Aguilar")
    print("Carné: 202204496")
    print("Curso: Introduccion a la Computacion y Programacion 2")
    print("Carrera: Ingenieria en Ciencias y Sistemas")
    print("Semestre: Cuarto Semestre")

def generar_grafica():
    print("Generando gráfica...")

signal_list = LinkedList()

while True:
    print("Menú principal:")
    print("1. Cargar archivo")
    print("2. Procesar archivo")
    print("3. Escribir archivo salida")
    print("4. Mostrar datos del estudiante")
    print("5. Generar gráfica")
    print("6. Salida")

    opcion = input("Selecciona una opción: ")

    if opcion == "1":
        cargar_archivo()
        print("Archivo cargado exitosamente...")
    elif opcion == "2":
        procesar_archivo()
        matriz_valores = cargar_archivo()
        matriz_umbral = aplicar_umbral(matriz_valores)
        grupos = agrupar_filas(matriz_umbral)
        valores_agrupados = sumar_valores_por_grupo(matriz_valores, grupos)
        print("Matriz de valores original:")
        imprimir_matriz(matriz_valores)
        print("______________________________________________________________")
        print("\nMatriz umbral:")
        imprimir_matriz(matriz_umbral)
        print("______________________________________________________________")
        print("\nGrupos:")
        imprimir_grupos(grupos)
        print("\nValores agrupados:")
        imprimir_matriz(valores_agrupados)
        print("______________________________________________________________")
    elif opcion == "3":
        escribir_archivo_salida()
        xml_filename = 'senales_reducidas.xml'
        guardar_en_xml(xml_filename, matriz_valores, grupos, valores_agrupados)
        print(f"Archivo XML '{xml_filename}' guardado exitosamente.")
    elif opcion == "4":
        mostrar_datos_estudiante()
    elif opcion == "5":
        print("Generar gráficas:")
        print("1. Matriz Valores")
        print("2. Valores Agrupados")
        opcion_grafica = input("Selecciona una opción de gráfica: ")

        if opcion_grafica == "1":
            generar_grafica_matriz_original(matriz_valores, "Matriz Valores")
        elif opcion_grafica == "2":
            generar_grafica_valores_agrupados(valores_agrupados, "Valores Agrupados")
        else:
            print("Opción no válida. Selecciona una opción válida.")
    elif opcion == "6":
        print("Saliendo del programa.")
        break
    else:
        print("Opción no válida. Por favor, selecciona una opción válida.")
