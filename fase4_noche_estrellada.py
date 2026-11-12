import os
import random
import math
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
import numpy as np
import matplotlib.pyplot as plt

# parametros del algoritmo (fase 4: van gogh con cerdas, reproduciendo la noche estrellada)
nombre_imagen = "imagenes/noche_estrellada.jpg"
ancho_trabajo = 400         # la imagen se reduce a este ancho para que sea rapido
number_imagenes = 10        # poblacion
number_pinceladas = 1500    # genes por cromosoma
number_generaciones = 3000
hedge_lambda = 0.2
prob_crossover = 0.8
prob_mutation = 0.002       # mas o menos 3 / number_pinceladas
size_torneo = 3
prob_fusion = 0.5          # probabilidad de intentar una fusion en cada hijo
distancia_fusion = 25      # pixeles: distancia maxima entre extremos para fusionar
max_fusion = 4             # una posicion puede juntar a lo mas 4 pinceladas
cada_cuanto = 50           # cada cuantas generaciones se guarda la mejor imagen
carpeta_salida = "resultados_fase4_noche"

# estilo van gogh (valores "medianas")
saturacion = 1.0           # la imagen ya es de van gogh, no se cambian sus colores
contraste = 1.0
min_size = 40              # largo de las pinceladas
max_size = 60
min_width = 8              # grosor
max_width = 14
prob_arco = 0.4            # 40% arcos, 60% lineas
min_angle = 40             # apertura de los arcos (grados)
max_angle = 120
variacion_angulo = 15      # grados que se puede desviar una pincelada del contorno

random.seed(1)  # para poder repetir los resultados


with Image.open(nombre_imagen) as imagen_original:
        img_RGB = imagen_original.convert("RGB")
        # se reduce la imagen para que el algoritmo no tarde tanto
        alto_trabajo = int(img_RGB.height * ancho_trabajo / img_RGB.width)
        img_RGB = img_RGB.resize((ancho_trabajo, alto_trabajo))
        img_foto_RGB = np.array(img_RGB)   # imagen sin cambios, solo para comparar al final

        # nivel 2: con saturacion = 1 y contraste = 1 la imagen objetivo queda igual a la pintura
        img_RGB = ImageEnhance.Color(img_RGB).enhance(saturacion)
        img_RGB = ImageEnhance.Contrast(img_RGB).enhance(contraste)
        img_width = img_RGB.width
        img_height = img_RGB.height
        img_original_RGB = np.array(img_RGB)

img_shape = img_original_RGB.shape
img_type = img_original_RGB.dtype

# nivel 3: direccion de los contornos en cada pixel
# el gradiente dice hacia donde cambia el brillo; el contorno va perpendicular a el (+90 grados)
img_gris = img_RGB.convert("L").filter(ImageFilter.GaussianBlur(3))
gy, gx = np.gradient(np.array(img_gris).astype(float))
angulo_contorno = (np.degrees(np.arctan2(gy, gx)) + 90) % 359


class Pincelada:

    #inicializar una pincelada
    def __init__(self, points=[], size= 0, width=0, angle =0, color=(0,0,0), tipo = "line"):
        self.points = points        #array de puntos tipo (x,y), points = [(x_0,y_0), (x_1,y_1)...]
        self.size = size
        self.width = width        #ancho de linea
        self.angle = angle        # inclinacion de la linea o medida del arco
        self.color = color        #en formato RGB - (r,g,b)
        self.tipo = tipo          #puede ser "line" o "arc"
        #datos adicionales necesarios para arcos:
        self.start = 0
        self.end = angle


    def print(self):
        if(self.tipo == "line"):
            print("[ points: "+str(self.points)+" , size: "+str(self.size)+
              " , width: "+str(self.width) + ", angle: "+str(self.angle) +
              ", color: "+str(self.color) + ", tipo: "+str(self.tipo) +  "]")
        else:
            print("[ points: "+str(self.points)+" , size: "+str(self.size)+
              " , width: "+str(self.width) + ", angle: "+str(self.angle) +
              ", color: "+str(self.color) + ", tipo: "+str(self.tipo) +
              ", start: "+str(self.start) +  ", end: "+str(self.end) +   "]")


class Pincelada_Randomizer:

    # inicializa los parametros para poder usar los metodos random
    def __init__(self,min_size = 45, max_size = 60,min_angle = 0, max_angle = 240,min_width=15, max_width =20, factor_arco= 0.6,
                 prob_arco = 0.5, variacion_angulo = 15):
        self.min_size = min_size
        self.max_size = max_size
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.min_width = min_width
        self.max_width = max_width
        self.factor_arco = factor_arco
        self.prob_arco = prob_arco
        self.variacion_angulo = variacion_angulo


    def generate_Random_Pincelada(self, tipo = ""):
        pincelada = Pincelada()
        if(tipo == ""):
            pincelada.tipo = self.random_Tipo()
        else:
            pincelada.tipo = tipo

        pincelada.width = self.random_Value_In_Range(self.min_width, self.max_width)
        pincelada.size = self.random_Value_In_Range(self.min_size, self.max_size)

        # van gogh: primero se elige el punto y el angulo sale del contorno en ese punto
        if(pincelada.tipo == "line"):
            pincelada.points, pincelada.angle = self.contour_Line(pincelada.size)
            pincelada.color = self.point_Color(pincelada.points[0])
        else:
            pincelada.angle = self.random_Value_In_Range(self.min_angle, self.max_angle)   # apertura del arco
            pincelada.points, pincelada.start, pincelada.end, punto_medio = self.contour_Arc(pincelada.size, pincelada.angle)
            pincelada.color = self.point_Color(punto_medio)
            pincelada.width = math.ceil(pincelada.width* self.factor_arco)
        return pincelada

    # linea que sigue el contorno: empieza en (x_0,y_0) y va en la direccion del contorno de ese punto
    def contour_Line(self, size):
        x_0 = random.randint(0, img_width-1)
        y_0 = random.randint(0, img_height-1)
        angle = (angulo_contorno[y_0][x_0] + random.randint(-self.variacion_angulo, self.variacion_angulo)) % 359

        x_1 = self.clamp(x_0 + size*math.cos(math.radians(angle)), 0, img_width-1)
        y_1 = self.clamp(y_0 + size*math.sin(math.radians(angle)), 0, img_height-1)
        return [(x_0,y_0),(x_1,y_1)], angle

    # arco que sigue el contorno: su punto medio cae en (x_0,y_0)
    # en un circulo la direccion del trazo es perpendicular al radio, por eso el -90
    def contour_Arc(self, size, apertura):
        x_0 = random.randint(0, img_width-1)
        y_0 = random.randint(0, img_height-1)
        direccion = angulo_contorno[y_0][x_0] + random.randint(-self.variacion_angulo, self.variacion_angulo)
        medio = direccion - 90

        r = size / 2
        centro_x = x_0 - r*math.cos(math.radians(medio))
        centro_y = y_0 - r*math.sin(math.radians(medio))
        points = [(centro_x - r, centro_y - r), (centro_x + r, centro_y + r)]

        start = (medio - apertura/2) % 359
        end = (medio + apertura/2) % 359
        return points, start, end, (x_0, y_0)

    # asigna color dado un punto aleatorio en la imagen
    # toma como referencia el color en la imagen original
    def random_Color(self):
        x = random.randint(0,img_width-1)
        y = random.randint(0,img_height-1)
        color = img_original_RGB[y][x]

        return tuple(color)

    # color de la imagen original en un punto (x,y)
    def point_Color(self, point):
        x = int(self.clamp(point[0], 0, img_width-1))
        y = int(self.clamp(point[1], 0, img_height-1))
        color = img_original_RGB[y][x]

        return tuple(color)

    # regresa un valor aleatorio en un rango [a,b]
    def random_Value_In_Range(self, a, b):
        if(a < b):
            return random.randint(a,b)
        else:
            return a

    def random_Tipo(self):
        shape_types = ["line", "arc"]
        if(random.random() < self.prob_arco):
            return shape_types[1]
        return shape_types[0]

    def random_Start_End(self, angle):
        start = random.randint(0,359)
        end = (start + angle)% 359
        return start, end

    def random_Points(self, size, angle, tipo):
        #convertir a radianes
        angle = math.radians(angle)

        #encontramos la proyeccion en x y y de la pincelada para ese angulo y r = size
        x_length = size*math.cos(angle)
        y_length = size*math.sin(angle)

        #inicializamos puntos random dentro de una caja para que no se salgan las cosas
        x_0 = random.randint(math.floor(abs(x_length) +1), math.floor(img_width - abs(x_length)))
        y_0 = random.randint(math.floor(abs(y_length) +1), math.floor(img_height - abs(y_length)))

        #se elige segundo punto hacia adelante o hacia atras - no se sale por nuestra eleccion del primer punto
        x_1 = x_0 + x_length
        y_1 = y_0 + y_length

        #regresamos el conjunto de dos puntos
        if(tipo == "line"):
            #para lineas no importa el orden
            return [(x_0,y_0),(x_1,y_1)]
        else:
            #para arcos, las coordenadas deben estar ordenadas de menor a mayor
            x_min, x_max = sorted([x_0,x_1])
            y_min, y_max = sorted([y_0,y_1])
            return [(x_min, y_min), (x_max + 15, y_max + 10)]


    def clamp(self,x, minimum, maximum):
        if x < minimum:
            return minimum
        if x > maximum:
            return maximum
        return x


class ImagenEvolutiva:

    def __init__(self):
        self.lista_pinceladas =[]
        self.particion = []   # cuantas pinceladas originales hay en cada posicion
        self.hedge_array = np.zeros((img_height, img_width))
        #self.image - se inicializa con generate_image

    def add_Pincelada(self,pincelada):
         self.lista_pinceladas.append(pincelada)
         self.particion.append(1)

    def update_Hedge_Array(self):
        img_temp = Image.new("RGB", [img_width, img_height])
        draw_img = ImageDraw.Draw(img_temp)
        num_pinceladas = len(self.lista_pinceladas)

        # dibuja todas las pinceladas en la lista pero las dibuja en blanco
        for pincelada in self.lista_pinceladas:
            if(pincelada.tipo == "line"):
                draw_img.line(xy=pincelada.points, fill = (255,255,255), width = pincelada.width)
            else:
                draw_img.arc(xy=pincelada.points, start = pincelada.start, end=pincelada.end, fill = (255,255,255), width = pincelada.width)


        array_temp = np.array(img_temp)
        #actualiza el hedge array con los nuevos 1's
        filas, columnas = np.where(np.all(array_temp == 255, axis=-1))
        self.hedge_array[filas, columnas] = 1

        del img_temp, draw_img, num_pinceladas,filas, columnas, array_temp

    # cerdas del pincel: dos lineas delgadas dentro del trazo, una mas clara y otra mas oscura
    def draw_Cerdas(self, draw_img, pincelada):
        claro = tuple(min(255, int(c * 1.25)) for c in pincelada.color)
        oscuro = tuple(int(c * 0.75) for c in pincelada.color)
        grosor = max(1, pincelada.width // 5)
        d = pincelada.width / 4
        (x_0, y_0), (x_1, y_1) = pincelada.points
        if(pincelada.tipo == "line"):
            largo = max(math.dist((x_0, y_0), (x_1, y_1)), 1)
            n_x, n_y = -(y_1 - y_0) / largo * d, (x_1 - x_0) / largo * d   # perpendicular al trazo
            draw_img.line(xy=[(x_0 + n_x, y_0 + n_y), (x_1 + n_x, y_1 + n_y)], fill = claro, width = grosor)
            draw_img.line(xy=[(x_0 - n_x, y_0 - n_y), (x_1 - n_x, y_1 - n_y)], fill = oscuro, width = grosor)
        else:
            # en arcos: un arco un poco mas chico (claro) y otro un poco mas grande (oscuro)
            if(x_1 - x_0 > 2*d and y_1 - y_0 > 2*d):
                draw_img.arc(xy=[(x_0 + d, y_0 + d), (x_1 - d, y_1 - d)], start = pincelada.start, end=pincelada.end, fill = claro, width = grosor)
            draw_img.arc(xy=[(x_0 - d, y_0 - d), (x_1 + d, y_1 + d)], start = pincelada.start, end=pincelada.end, fill = oscuro, width = grosor)

    def generate_image(self):
        #crea image
        image = Image.new("RGB", [img_width, img_height])
        draw_img = ImageDraw.Draw(image)
        num_pinceladas = len(self.lista_pinceladas)

        # dibuja todas las pinceladas en la lista
        for pincelada in self.lista_pinceladas:
            if(pincelada.tipo == "line"):
                draw_img.line(xy=pincelada.points, fill = pincelada.color, width = pincelada.width)
            else:
                draw_img.arc(xy=pincelada.points, start = pincelada.start, end=pincelada.end, fill = pincelada.color, width = pincelada.width)
            self.draw_Cerdas(draw_img, pincelada)
        self.image = image
        del draw_img, num_pinceladas
        return image


class AlgoritmoEvolutivo:

    def __init__(self,number_imagenes=10,number_pinceladas=100,number_generaciones=100,hedge_lambda=0.2,
                 prob_crossover=0.8,prob_mutation=0.05,size_torneo=3,prob_fusion=0.5,distancia_fusion=25,max_fusion=3):
        self.number_chromosomes = number_imagenes
        self.number_genes = number_pinceladas
        self.number_generaciones = number_generaciones
        self.hedge_lambda = hedge_lambda
        self.prob_crossover = prob_crossover
        self.prob_mutation = prob_mutation
        self.size_torneo = size_torneo
        self.prob_fusion = prob_fusion
        self.distancia_fusion = distancia_fusion
        self.max_fusion = max_fusion
        self.fusiones_intentadas = 0
        self.fusiones_aceptadas = 0
        self.fitness = []
        self.list_chromosomes = []
        self.historial_fitness = []   # mejor fitness de cada generacion

    def mean_square_error(self,img_evolutiva):
        filas, columnas = np.where(img_evolutiva.hedge_array == 1)
        max_error_posible = 65025
        error_contenido = max_error_posible
        porcent_hedge = 0.0
        # si al menos un pixel fue coloreado
        if len(filas) != 0:
            img_original_signo = img_original_RGB.astype(np.int32) #para evitar negativos cuando haces la resta
            img_original_signo = img_original_signo[filas, columnas]
            img_evol_signo = np.array(img_evolutiva.image).astype(np.int32)
            img_evol_signo = img_evol_signo[filas, columnas]
            error_contenido = (img_original_signo - img_evol_signo)**2
            error_contenido = np.mean(error_contenido)
            porcent_hedge = len(filas)/((len(img_evolutiva.hedge_array) * len(img_evolutiva.hedge_array[0])))
        error_contenido = (error_contenido/max_error_posible) + (self.hedge_lambda * (1 - porcent_hedge))
        #print(error_contenido)
        return error_contenido

    def calculate_Fitness(self):
        self.fitness = []
        for i in range(self.number_chromosomes):
            img_evol = self.list_chromosomes[i]
            img_evol.generate_image()
            value = self.mean_square_error(img_evol)
            self.fitness.append(value)

    def show_Best_Option(self):
        best_option = self.list_chromosomes[self.fitness.index(min(self.fitness))]
        img_evol = best_option.generate_image()
        img_evol.show()
        return img_evol

    #Crea una lista de chromosomas-imagenes
    def create_Chromosomes(self,randomizer):

        for i in range(0,self.number_chromosomes): # numero de imagenes
            #Crea una imagen
            img_evol = ImagenEvolutiva()

            for j in range(0,self.number_genes):# numero de pinceladas por imagen
                # agregar pinceladas a la imagen
                pincelada = randomizer.generate_Random_Pincelada()
                img_evol.add_Pincelada(pincelada)

            img_evol.update_Hedge_Array()
            #agrega la imagen a la lista de imagenes/chromosomas
            self.list_chromosomes.append(img_evol)

    # ---------------- parte evolutiva ----------------

    # torneo: se escogen size_torneo imagenes al azar y gana la de menor fitness
    def tournament_Selection(self):
        competidores = random.sample(range(0, self.number_chromosomes), self.size_torneo)
        ganador = competidores[0]
        for i in competidores:
            if(self.fitness[i] < self.fitness[ganador]):
                ganador = i
        return self.list_chromosomes[ganador]

    # cruza de un punto: el hijo toma las pinceladas [0,punto) del padre 1 y [punto,n) del padre 2
    def crossover_One_Point(self, padre_1, padre_2):
        hijo = ImagenEvolutiva()
        punto = random.randint(1, self.number_genes - 1)
        hijo.lista_pinceladas = padre_1.lista_pinceladas[0:punto] + padre_2.lista_pinceladas[punto:]
        hijo.particion = padre_1.particion[0:punto] + padre_2.particion[punto:]   # la particion se corta igual
        return hijo

    # mutacion por reemplazo: cada pincelada se cambia por una nueva con probabilidad prob_mutation
    def mutate_Chromosome(self, img_evol, randomizer):
        for j in range(0, len(img_evol.lista_pinceladas)):
            if(random.random() < self.prob_mutation):
                img_evol.lista_pinceladas[j] = randomizer.generate_Random_Pincelada()
                img_evol.particion[j] = 1

    def create_Next_Generation(self, randomizer):
        nueva_generacion = []

        # elitismo: la mejor imagen pasa sin cambios
        mejor = self.list_chromosomes[self.fitness.index(min(self.fitness))]
        nueva_generacion.append(mejor)

        while(len(nueva_generacion) < self.number_chromosomes):
            padre_1 = self.tournament_Selection()
            padre_2 = self.tournament_Selection()

            if(random.random() < self.prob_crossover):
                hijo = self.crossover_One_Point(padre_1, padre_2)
            else:
                hijo = ImagenEvolutiva()
                hijo.lista_pinceladas = list(padre_1.lista_pinceladas)  # copia de la lista, no la misma
                hijo.particion = list(padre_1.particion)

            self.mutate_Chromosome(hijo, randomizer)
            hijo.update_Hedge_Array()   # el hijo empieza con su hedge en ceros

            if(random.random() < self.prob_fusion):
                hijo = self.merge_Chromosome(hijo, randomizer)
            nueva_generacion.append(hijo)

        self.list_chromosomes = nueva_generacion

    # ---------------- fusion de pinceladas (fase 2) ----------------

    # fitness de una sola imagen, para comparar antes y despues de fusionar
    def fitness_Image(self, img_evol):
        img_evol.generate_image()
        return self.mean_square_error(img_evol)

    def center_X(self, pincelada):
        return (pincelada.points[0][0] + pincelada.points[1][0]) / 2

    # cada extremo de p_a se empareja con el extremo mas cercano de p_b (directo o cruzado)
    # y regresa la distancia del par mas alejado
    def distance_Pinceladas(self, p_a, p_b):
        directo = max(math.dist(p_a.points[0], p_b.points[0]), math.dist(p_a.points[1], p_b.points[1]))
        cruzado = max(math.dist(p_a.points[0], p_b.points[1]), math.dist(p_a.points[1], p_b.points[0]))
        return min(directo, cruzado)

    # promedio de dos angulos en grados (350 y 10 dan 0, no 180)
    def angle_Average(self, a, b):
        diferencia = (b - a) % 360   # la diferencia se mide en la vuelta completa
        if(diferencia > 180):
            diferencia = diferencia - 360
        return round(a + diferencia / 2) % 359

    # busca las dos pinceladas mas cercanas del mismo tipo
    # se ordena una copia de los indices por x, la lista de pinceladas no se mueve
    def find_Pair_To_Merge(self, img_evol):
        mejor_par = None
        mejor_distancia = self.distancia_fusion
        for tipo in ["line", "arc"]:
            indices = []
            for i in range(0, len(img_evol.lista_pinceladas)):
                if(img_evol.lista_pinceladas[i].tipo == tipo):
                    indices.append(i)
            indices.sort(key=lambda i: self.center_X(img_evol.lista_pinceladas[i]))

            for a in range(0, len(indices)):
                i = indices[a]
                for b in range(a + 1, len(indices)):
                    j = indices[b]
                    p_i = img_evol.lista_pinceladas[i]
                    p_j = img_evol.lista_pinceladas[j]
                    # estan ordenadas por x: si esta ya queda lejos, las siguientes tambien
                    if(self.center_X(p_j) - self.center_X(p_i) > self.distancia_fusion):
                        break
                    if(img_evol.particion[i] + img_evol.particion[j] > self.max_fusion):
                        continue
                    d = self.distance_Pinceladas(p_i, p_j)
                    if(d <= mejor_distancia):
                        mejor_distancia = d
                        mejor_par = (min(i, j), max(i, j))
        return mejor_par

    # union de dos pinceladas: un trazo mas grande que cubre a las dos
    def merge_Pincelada(self, p_a, p_b):
        nueva = Pincelada()
        nueva.tipo = p_a.tipo
        nueva.width = max(p_a.width, p_b.width)

        # color promedio pesado por el tamaño de cada pincelada
        total = p_a.size + p_b.size
        color = []
        for k in range(0, 3):
            color.append(int((int(p_a.color[k])*p_a.size + int(p_b.color[k])*p_b.size) / total))
        nueva.color = tuple(color)

        if(nueva.tipo == "line"):
            # de los 4 extremos se toman los dos mas alejados
            extremos = [p_a.points[0], p_a.points[1], p_b.points[0], p_b.points[1]]
            mayor = -1
            for m in range(0, 4):
                for n in range(m + 1, 4):
                    if(math.dist(extremos[m], extremos[n]) > mayor):
                        mayor = math.dist(extremos[m], extremos[n])
                        nueva.points = [extremos[m], extremos[n]]
            nueva.size = mayor
            nueva.angle = round(math.degrees(math.atan2(nueva.points[1][1] - nueva.points[0][1],
                                                        nueva.points[1][0] - nueva.points[0][0]))) % 359
        else:
            # para arcos la caja que contiene a las dos cajas
            x_min = min(p_a.points[0][0], p_b.points[0][0])
            y_min = min(p_a.points[0][1], p_b.points[0][1])
            x_max = max(p_a.points[1][0], p_b.points[1][0])
            y_max = max(p_a.points[1][1], p_b.points[1][1])
            nueva.points = [(x_min, y_min), (x_max, y_max)]
            nueva.size = max(p_a.size, p_b.size)
            nueva.angle = max(p_a.angle, p_b.angle)
            nueva.start = self.angle_Average(p_a.start, p_b.start)
            nueva.end = self.angle_Average(p_a.end, p_b.end)
        return nueva

    # fusion: junta el par mas cercano en la posicion i, quita la j y agrega una pincelada nueva al final
    # solo se acepta si el fitness no empeora
    def merge_Chromosome(self, img_evol, randomizer):
        par = self.find_Pair_To_Merge(img_evol)
        if(par == None):
            return img_evol
        i, j = par
        self.fusiones_intentadas = self.fusiones_intentadas + 1
        fitness_antes = self.fitness_Image(img_evol)

        nueva_img = ImagenEvolutiva()
        nueva_img.lista_pinceladas = list(img_evol.lista_pinceladas)
        nueva_img.particion = list(img_evol.particion)
        nueva_img.lista_pinceladas[i] = self.merge_Pincelada(img_evol.lista_pinceladas[i], img_evol.lista_pinceladas[j])
        nueva_img.particion[i] = img_evol.particion[i] + img_evol.particion[j]
        del nueva_img.lista_pinceladas[j]
        del nueva_img.particion[j]
        nueva_img.add_Pincelada(randomizer.generate_Random_Pincelada())   # entra con particion 1
        nueva_img.update_Hedge_Array()

        fitness_despues = self.fitness_Image(nueva_img)
        if(fitness_despues <= fitness_antes):
            self.fusiones_aceptadas = self.fusiones_aceptadas + 1
            return nueva_img
        return img_evol

    def evolve(self, randomizer, carpeta = "", cada_cuanto = 10):
        self.historial_fitness = []
        self.calculate_Fitness()

        for g in range(0, self.number_generaciones):
            mejor = min(self.fitness)
            self.historial_fitness.append(mejor)

            if(g % cada_cuanto == 0):
                print("generacion: " + str(g) + "   mejor fitness: " + str(round(mejor, 5)) +
                      "   fusiones aceptadas: " + str(self.fusiones_aceptadas) + " de " + str(self.fusiones_intentadas))
                if(carpeta != ""):
                    best_option = self.list_chromosomes[self.fitness.index(mejor)]
                    best_option.image.save(carpeta + "/generacion_" + str(g) + ".png")

            self.create_Next_Generation(randomizer)
            self.calculate_Fitness()

        mejor = min(self.fitness)
        self.historial_fitness.append(mejor)
        print("generacion: " + str(self.number_generaciones) + "   mejor fitness: " + str(round(mejor, 5)) +
              "   fusiones aceptadas: " + str(self.fusiones_aceptadas) + " de " + str(self.fusiones_intentadas))
        if(carpeta != ""):
            best_option = self.list_chromosomes[self.fitness.index(mejor)]
            best_option.image.save(carpeta + "/generacion_" + str(self.number_generaciones) + ".png")


# ---------------- se corre el algoritmo ----------------

os.makedirs(carpeta_salida, exist_ok=True)
img_RGB.save(carpeta_salida + "/objetivo_noche.png")

randomizer = Pincelada_Randomizer(min_size, max_size, min_angle, max_angle, min_width, max_width, 0.6,
                                  prob_arco, variacion_angulo)
algoritmo_evol = AlgoritmoEvolutivo(number_imagenes, number_pinceladas, number_generaciones, hedge_lambda,
                                    prob_crossover, prob_mutation, size_torneo,
                                    prob_fusion, distancia_fusion, max_fusion)

algoritmo_evol.create_Chromosomes(randomizer)
algoritmo_evol.evolve(randomizer, carpeta_salida, cada_cuanto)

# resumen de la particion de la mejor imagen
best_option = algoritmo_evol.list_chromosomes[algoritmo_evol.fitness.index(min(algoritmo_evol.fitness))]
print("posiciones con fusion: " + str(len(best_option.particion) - best_option.particion.count(1)) +
      "   pinceladas originales representadas: " + str(sum(best_option.particion)))
best_option.generate_image().save(carpeta_salida + "/resultado.png")


# medicion del estilo de la mejor imagen
def medir_estilo(img_evol):
    largo_total = 0
    arcos = 0
    lineas = 0
    lineas_contorno = 0
    for pincelada in img_evol.lista_pinceladas:
        largo_total = largo_total + pincelada.size
        if(pincelada.tipo == "arc"):
            arcos = arcos + 1
        else:
            lineas = lineas + 1
            x = min(int(pincelada.points[0][0]), img_width-1)
            y = min(int(pincelada.points[0][1]), img_height-1)
            # una linea a 0 y a 180 grados es la misma, por eso se compara modulo 180
            diferencia = abs(pincelada.angle - angulo_contorno[y][x]) % 180
            if(diferencia < 20 or diferencia > 160):
                lineas_contorno = lineas_contorno + 1

    img = np.array(img_evol.image).astype(float)
    error = np.mean((img - img_original_RGB)**2)
    psnr = 10*math.log10(255**2 / error)   # parecido con toda la imagen objetivo, mas alto es mejor
    saturacion_img = np.mean(np.array(img_evol.image.convert("HSV"))[:,:,1])
    saturacion_foto = np.mean(np.array(Image.fromarray(img_foto_RGB).convert("HSV"))[:,:,1])

    print("largo promedio: " + str(round(largo_total / len(img_evol.lista_pinceladas), 1)) + " px")
    print("arcos: " + str(round(100 * arcos / len(img_evol.lista_pinceladas), 1)) + " %")
    print("lineas que siguen el contorno (+-20 grados): " + str(round(100 * lineas_contorno / max(lineas, 1), 1)) + " %")
    print("saturacion promedio: " + str(round(saturacion_img, 1)) + "   (pintura original: " + str(round(saturacion_foto, 1)) + ")")
    print("PSNR contra la noche estrellada: " + str(round(psnr, 2)) + " dB")

medir_estilo(best_option)

# grafica del mejor fitness por generacion
plt.plot(algoritmo_evol.historial_fitness)
plt.xlabel("generacion")
plt.ylabel("mejor fitness")
plt.title("Algoritmo evolutivo - fase 4 (noche estrellada)")
plt.savefig(carpeta_salida + "/fitness.png")

algoritmo_evol.show_Best_Option()
plt.show()
