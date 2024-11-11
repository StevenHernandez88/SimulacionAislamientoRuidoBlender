
import bpy

import networkx as nx

import matplotlib.pyplot as plt

import math

class Salon:
    umbralRuido = 65  # Definimos umbralRuido como una constante de clase
    
    def __init__(self, nombre, nombre_objeto_representativo, conexiones=[]):
        self.nombre = nombre
        self.nombre_objeto_representativo = nombre_objeto_representativo
        self.objeto_representativo = bpy.data.objects.get(nombre_objeto_representativo)
        self.conexiones = conexiones
        self.aislamiento_aplicado = 0
    
    def obtener_propiedades(self):
        if self.objeto_representativo:
            propiedades = {}
            propiedades["Material"] = self.objeto_representativo.get("Material")
            propiedades["numPersonas"] = self.objeto_representativo.get("numPersonas")
            propiedades["tiempoDuracion"] = self.objeto_representativo.get("tiempoDuracion")
            propiedades["Actividad"] = self.objeto_representativo.get("Actividad")
            return propiedades
        else:
            print(f"El objeto representativo '{self.nombre_objeto_representativo}' no se encontró.")
            return None
    
    def configurar_propiedades(self, material=None, num_personas=None, tiempo_duracion=None, Actividad=None):
        if self.objeto_representativo:
            if material is not None:
                self.objeto_representativo["Material"] = material
            if num_personas is not None:
                self.objeto_representativo["numPersonas"] = num_personas
            if tiempo_duracion is not None:
                self.objeto_representativo["tiempoDuracion"] = tiempo_duracion
            if Actividad is not None:
                self.objeto_representativo["Actividad"] = Actividad
        else:
            print(f"El objeto representativo '{self.nombre_objeto_representativo}' no se encontró.")
            
    def obtener_color(self):
        ruido_total = calcular_ruido_total(self)
        if ruido_total is not None:
            if ruido_total < 0:
                return "Azul"
            elif ruido_total > 0:
                if ruido_total >= Salon.umbralRuido:
                    return "Rojo"
                elif 50 <= ruido_total <= 64:
                    return "Naranja"
        return "Amarillo"

class Recomendaciones:
    @staticmethod
    def realizar(propiedades, salon):
        recomendaciones = []
        ruido_total = calcular_ruido_total(salon)
        tiempo_duracion = propiedades.get("tiempoDuracion")
        if ruido_total is not None:
            if ruido_total < 0:
                recomendaciones.append("El salón tiene muy buenas condiciones acústicas.")
            elif ruido_total > 0:
                if ruido_total >= Salon.umbralRuido:  # Utilizamos la constante de clase
                    recomendaciones.append("El ruido es alto. Considera medidas de aislamiento acústico.")
                elif 50 <= ruido_total <= 64 and tiempo_duracion > 40:
                    recomendaciones.append("El tiempo de duración es prolongado. Puede afectar el bienestar de las personas.")
        return recomendaciones


class Utilidades:
    materiales = {
        "Ladrillos de arcilla": 45,
        "Ladrillos de hormigón": 40,
        "Ladrillos de vidrio": 35,
        "Concreto convencional": 45,
        "Concreto celular": 45,
        "Concreto reforzado con fibras": 45,
        "Drywall": 35
    }
    
    @staticmethod
    def obtener_aislamiento_acustico(material):
        return Utilidades.materiales.get(material, "Desconocido")
    
    

def imprimir_salones(salones):
    for salon in salones:
        print(f"Salón: {salon.nombre}")
        print(f"Color: {salon.obtener_color()}")
        propiedades_salon = salon.obtener_propiedades()
        if propiedades_salon:
            recomendaciones = Recomendaciones.realizar(propiedades_salon, salon)
            print("Propiedades del salón:", propiedades_salon)
            print("Recomendaciones:", recomendaciones)
            aislamiento_acustico = Utilidades.obtener_aislamiento_acustico(propiedades_salon["Material"])
            print("Aislamiento acústico:", aislamiento_acustico, "decibeles")
            print("Conexiones:", salon.conexiones)
            ruido_total = calcular_ruido_total(salon)
            print("Ruido total:", ruido_total, "decibeles")
            print()


# Diccionario de salones y su ruido externo
ruido_por_salon = {
    2: 90, 16: 90, 17: 90, 8: 90, 9: 90, 24: 90, 25: 90, 26: 90, 23: 90, 10: 90, 7: 90,  # Cerca
    18: 60, 15: 60, 1: 60, 27: 60, 22: 60, 11: 60, 6: 60,  # Próximos
    28: 20, 21: 20, 12: 20, 5: 20, 20: 20, 13: 20, 4: 20, 3: 20, 14: 20, 19: 20  # Lejanos
}


def calcular_suma_logaritmica(ruido_db1, ruido_db2):
    # Convertir de decibelios a intensidad
    ruido1 = 10 ** (ruido_db1 / 10)
    ruido2 = 10 ** (ruido_db2 / 10)

    # Sumar las intensidades
    ruido_total = ruido1 + ruido2

    # Convertir de nuevo a decibelios
    ruido_total_db = 10 * math.log10(ruido_total)

    return ruido_total_db



def calcular_resta_logaritmica(ruido_db1, ruido_db2):
    # Convertir de decibelios a intensidad
    ruido1 = 10 ** (ruido_db1 / 10)
    ruido2 = 10 ** (ruido_db2 / 10)

    # Restar las intensidades
    ruido_total = ruido1 - ruido2

    # Convertir de nuevo a decibelios
    ruido_total_db = 10 * math.log10(abs(ruido_total))

    return ruido_total_db


def calcular_ruido_total(salon):
    ruido_interno_db = 10  # en decibelios
    ruido_externo_db = 0  # en decibelios

    for conexion in salon.conexiones:
        ruido_externo_db = calcular_suma_logaritmica(ruido_externo_db, 5)

    ruido_externo_db = calcular_suma_logaritmica(
        ruido_externo_db, ruido_por_salon[int(salon.nombre.replace("Salon", ""))]
    )

    ruido_total_db = calcular_suma_logaritmica(ruido_interno_db, ruido_externo_db)

    # Aplica la reducción de ruido si existe un aislamiento
    if salon.aislamiento_aplicado > 0:
        ruido_total_db -= ruido_total_db * (salon.aislamiento_aplicado / 100)
        
    return ruido_total_db


def crear_grafo(salones):
    G = nx.Graph()
    for salon in salones:
        G.add_node(salon.nombre)
        for conexion in salon.conexiones:
            G.add_edge(salon.nombre, conexion)
    return G


def dibujar_grafo(G):
    plt.figure()  # Crea una nueva figura
    pos = nx.spring_layout(G, scale=20)  # Aumenta el espacio entre los nodos
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1500, edge_color='black', width=2)  # Dibuja el grafo una vez
    plt.savefig("C:/Users/PC/Downloads/Steven/Proyecto Blender/grafo.png")  # Guarda la gráfica como una imagen PNG
    
    
def dibujar_grafo_con_colores(G, colores):
    # Mapeo de colores en español a inglés
    color_map = {
        'Amarillo': 'yellow',
        'Rojo': 'red',
        'Naranja': 'orange',
        'Azul': 'blue'
    }
    
    plt.figure(figsize=(12, 12))  # Aumenta el tamaño de la figura
    pos = nx.spring_layout(G, scale=20)  # Aumenta el espacio entre los nodos
    nx.draw(G, pos, labels={node:node for node in G.nodes()}, node_color=[color_map[colores[node]] for node in G.nodes()], node_size=1500, edge_color='black', width=2, font_size=8)  # Dibuja el grafo una vez
    plt.savefig("C:/Users/PC/Downloads/Steven/Proyecto Blender/grafo_coloreado.png")  # Guarda la gráfica como una imagen PNG


def categorizar_salones_por_color(salones):
    categorias = {
        "Azul": [],
        "Amarillo": [],
        "Naranja": [],
        "Rojo": []
    }

    for salon in salones:
        color = salon.obtener_color()
        categorias[color].append(salon.nombre)

    for color, salones in categorias.items():
        print(f"Salones de color {color}:")
        for salon in salones:
            print(salon)
        print()
        
def cambiar_color_objeto(nombre_objeto, color):
    objeto = bpy.data.objects[nombre_objeto]  # Obtiene el objeto por su nombre
    if objeto.data.materials:
        # Si el objeto ya tiene un material, actualiza su color
        material = objeto.data.materials[0]
    else:
        # Si el objeto no tiene un material, crea uno nuevo
        material = bpy.data.materials.new(name="ColorMaterial")
        objeto.data.materials.append(material)
    material.diffuse_color = color  # Establece el color del material

def actualizar_color_paredes(salones):
    # Crea un diccionario de colores para cada nodo
    colores = {}
    for salon in salones:
        colores[salon.nombre] = salon.obtener_color()
    
    # Cambia el color de las paredes en Blender usando nombre_objeto_representativo
    for salon in salones:
        nombre_pared = salon.nombre_objeto_representativo  # Usa el nombre del objeto representativo del salón
        color = {
            'Amarillo': (1, 1, 0, 1),  # RGBA para amarillo
            'Rojo': (1, 0, 0, 1),  # RGBA para rojo
            'Naranja': (1, 0.5, 0, 1),  # RGBA para naranja
            'Azul': (0, 0, 1, 1)  # RGBA para azul
        }[colores[salon.nombre]]
        
        cambiar_color_objeto(nombre_pared, color)    
 

class HistorialAislamiento:
    def __init__(self):
        self.historial = []  # Lista de cambios realizados
        
    def agregar_cambio(self, salon, ruido_anterior, aislamiento_aplicado):
        self.historial.append({
            'salon': salon,
            'ruido_anterior': ruido_anterior,
            'aislamiento_aplicado': aislamiento_aplicado
        })
        
    def deshacer_ultimo_cambio(self, salones):
        if self.historial:
            ultimo_cambio = self.historial.pop()
            salon = ultimo_cambio['salon']
            
            # Restaurar el ruido anterior
            propiedades = salon.obtener_propiedades()
            salon.configurar_propiedades(
                material=propiedades["Material"],
                num_personas=propiedades["numPersonas"],
                tiempo_duracion=propiedades["tiempoDuracion"],
                Actividad=propiedades["Actividad"]
            )
            
            # Actualizar la visualización
            actualizar_color_paredes(salones)
            
            return ultimo_cambio
        return None

class OpcionAislamiento:
    def __init__(self, nombre, reduccion_db, costo_m2):
        self.nombre = nombre
        self.reduccion_db = reduccion_db
        self.costo_m2 = costo_m2

    def calcular_costo_total(self, area=60):  # Área por defecto de 60m²
        return self.costo_m2 * area

class GestorAislamiento:
    def __init__(self):
        self.opciones = [
            OpcionAislamiento("Complejo multicapa básico", 20, 124996),
            OpcionAislamiento("Lámina viscoelástica delgada", 30, 97324),
            OpcionAislamiento("Lámina viscoelástica gruesa", 35, 479708),
            OpcionAislamiento("Sistema mixto multicapa", 40, 350000)
        ]
        self.historial = HistorialAislamiento()
    
    def mostrar_opciones(self):
        print("\nOpciones de aislamiento disponibles:")
        for i, opcion in enumerate(self.opciones, 1):
            print(f"{i}. {opcion.nombre}")
            print(f"   Reducción: {opcion.reduccion_db} %")
            print(f"   Costo por m² (60m² total): ${opcion.costo_m2:,} COP")
            print(f"   Costo total: ${opcion.calcular_costo_total():,} COP")
            print()

    def aplicar_aislamiento(self, salon, opcion_index, salones):
        if 0 <= opcion_index < len(self.opciones):
            opcion = self.opciones[opcion_index]
            area = 60  # Área fija de 60m²
            costo_total = opcion.calcular_costo_total(area)
            
            # Obtener el ruido actual y propiedades
            ruido_actual = calcular_ruido_total(salon)
            propiedades = salon.obtener_propiedades()
            
            # Guardar el cambio en el historial antes de modificar
            self.historial.agregar_cambio(salon, ruido_actual, opcion)
            
            # Calcular el nuevo ruido y aplicar la reducción como porcentaje
            salon.aislamiento_aplicado = opcion.reduccion_db
            nuevo_ruido = calcular_ruido_total(salon)
            
            # Actualizar la visualización en Blender
            actualizar_color_paredes(salones)
            
            return {
                'opcion': opcion.nombre,
                'area_tratada': area,
                'costo_total': costo_total,
                'ruido_anterior': ruido_actual,
                'ruido_nuevo': nuevo_ruido,
                'reduccion_total': ruido_actual - nuevo_ruido,
                'material_anterior': propiedades["Material"],
            }
        

        return None

def menu_aislamiento(salones):
    gestor = GestorAislamiento()
    while True:
        print("\n=== MENÚ DE AISLAMIENTO ACÚSTICO ===")
        print("1. Ver salones y sus niveles de ruido")
        print("2. Aplicar aislamiento a un salón")
        print("3. Ver opciones de aislamiento")
        print("4. Deshacer último cambio")
        print("5. Salir")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            imprimir_salones(salones)
        elif opcion == "2":
            print("\nSalones disponibles:")
            for i, salon in enumerate(salones, 1):
                ruido = calcular_ruido_total(salon)
                print(f"{i}. {salon.nombre} - Ruido actual: {ruido:.1f} dB")
            
            try:
                salon_index = int(input("\nSeleccione el número de salón: ")) - 1
                if 0 <= salon_index < len(salones):
                    salon = salones[salon_index]
                    
                    # Mostrar opciones de aislamiento
                    gestor.mostrar_opciones()
                    opcion_index = int(input("Seleccione el número de opción de aislamiento: ")) - 1
                    
                    resultado = gestor.aplicar_aislamiento(salon, opcion_index, salones)
                    if resultado:
                        print("\nResultados de la aplicación del aislamiento:")
                        print(f"Opción seleccionada: {resultado['opcion']}")
                        print(f"Área tratada: {resultado['area_tratada']} m²")
                        print(f"Costo total: ${resultado['costo_total']:,.2f} COP")
                        print(f"Ruido anterior: {resultado['ruido_anterior']:.1f} dB")
                        print(f"Ruido nuevo: {resultado['ruido_nuevo']:.1f} dB")
                        print(f"Reducción total: {resultado['reduccion_total']:.1f} dB")
                        
                        # Mostrar el nuevo color del salón
                        print(f"Nuevo color del salón: {salon.obtener_color()}")
            except ValueError:
                print("Por favor, ingrese valores numéricos válidos")
        
        elif opcion == "3":
            gestor.mostrar_opciones()
            
        elif opcion == "4":
            ultimo_cambio = gestor.historial.deshacer_ultimo_cambio(salones)
            if ultimo_cambio:
                print("\nSe ha deshecho el último cambio:")
                print(f"Salón: {ultimo_cambio['salon'].nombre}")
                print(f"Ruido restaurado: {ultimo_cambio['ruido_anterior']:.1f} dB")
                print(f"Aislamiento removido: {ultimo_cambio['aislamiento_aplicado'].nombre}")
            else:
                print("\nNo hay cambios para deshacer")
        
        elif opcion == "5":
            break
        
        else:
            print("Opción no válida")


def main():
    salones = [
        Salon("Salon1", "SalonRepresentativo1", conexiones=["Salon2", "Salon15", "Salon3"]),
        Salon("Salon2", "SalonRepresentativo2", conexiones=["Salon16", "Salon1"]),
        Salon("Salon3", "SalonRepresentativo3", conexiones=["Salon1", "Salon14", "Salon4"]),
        Salon("Salon4", "SalonRepresentativo4", conexiones=["Salon3", "Salon13"]),
        Salon("Salon5", "SalonRepresentativo5", conexiones=["Salon20", "Salon12", "Salon6"]),
        Salon("Salon6", "SalonRepresentativo6", conexiones=["Salon5", "Salon11", "Salon19", "Salon7"]),
        Salon("Salon7", "SalonRepresentativo7", conexiones=["Salon10", "Salon6", "Salon8", "Salon18"]),
        Salon("Salon8", "SalonRepresentativo8", conexiones=["Salon9", "Salon7", "Salon17"]),
        Salon("Salon9", "SalonRepresentativo9", conexiones=["Salon8", "Salon24", "Salon10"]),
        Salon("Salon10", "SalonRepresentativo10", conexiones=["Salon7", "Salon23", "Salon9", "Salon11"]),
        Salon("Salon11", "SalonRepresentativo11", conexiones=["Salon6", "Salon22", "Salon10", "Salon12"]),
        Salon("Salon12", "SalonRepresentativo12", conexiones=["Salon5", "Salon21", "Salon11"]),
        Salon("Salon13", "SalonRepresentativo13", conexiones=["Salon4", "Salon20", "Salon14"]),
        Salon("Salon14", "SalonRepresentativo14", conexiones=["Salon3", "Salon19", "Salon13", "Salon15"]),
        Salon("Salon15", "SalonRepresentativo15", conexiones=["Salon1", "Salon18", "Salon14", "Salon16"]),
        Salon("Salon16", "SalonRepresentativo16", conexiones=["Salon2", "Salon17", "Salon15"]),
        Salon("Salon17", "SalonRepresentativo17", conexiones=["Salon16", "Salon8", "Salon18"]),
        Salon("Salon18", "SalonRepresentativo18", conexiones=["Salon15", "Salon17", "Salon7", "Salon19"]),
        Salon("Salon19", "SalonRepresentativo19", conexiones=["Salon14", "Salon18", "Salon6", "Salon20"]),
        Salon("Salon20", "SalonRepresentativo20", conexiones=["Salon13", "Salon19", "Salon5"]),
        Salon("Salon21", "SalonRepresentativo21", conexiones=["Salon12", "Salon28", "Salon22"]),
        Salon("Salon22", "SalonRepresentativo22", conexiones=["Salon11", "Salon27", "Salon21", "Salon23"]),
        Salon("Salon23", "SalonRepresentativo23", conexiones=["Salon10", "Salon26", "Salon22", "Salon24"]),
        Salon("Salon24", "SalonRepresentativo24", conexiones=["Salon9", "Salon25", "Salon23"]),
        Salon("Salon25", "SalonRepresentativo25", conexiones=["Salon24", "Salon26"]),
        Salon("Salon26", "SalonRepresentativo26", conexiones=["Salon23", "Salon25", "Salon27"]),
        Salon("Salon27", "SalonRepresentativo27", conexiones=["Salon22", "Salon26", "Salon28"]),
        Salon("Salon28", "SalonRepresentativo28", conexiones=["Salon21", "Salon27"])
    ]
    """
    
    # Modificar las propiedades del Salon1
    salon_modificar = "Salon1"
    for salon in salones:
        if salon.nombre == salon_modificar:
            salon.configurar_propiedades(material="Concreto convencional", num_personas=25, tiempo_duracion=45, Actividad="Musica")
            print(f"Se han modificado las propiedades del {salon_modificar}:")
    """
    
    G = crear_grafo(salones)
    #dibujar_grafo(G)
    
    
    colores = {}
    for salon in salones:
        colores[salon.nombre] = salon.obtener_color()
    
    # Dibuja el grafo con los colores de los nodos
    #dibujar_grafo_con_colores(G, colores)
    
    menu_aislamiento(salones)
    
    actualizar_color_paredes(salones)
    

if __name__ == "__main__":
    main()
