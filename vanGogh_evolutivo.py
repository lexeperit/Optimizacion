import os
import random
import math
from PIL import Image, ImageDraw
import numpy as np
import matplotlib.pyplot as plt

# parametros del algoritmo (fase 1)
nombre_imagen = "Angie_codigo/vanGogh2.jpeg"
number_imagenes = 10        # poblacion
number_pinceladas = 100     # genes por cromosoma
number_generaciones = 100
hedge_lambda = 0.2
prob_crossover = 0.8
prob_mutation = 0.05
size_torneo = 3
carpeta_salida = "resultados_fase1"

random.seed(1)  # para poder repetir los resultados


with Image.open(nombre_imagen) as imagen_original:
        img_RGB = imagen_original.convert("RGB")
        img_width = imagen_original.width
        img_height = imagen_original.height
        img_original_RGB = np.array(img_RGB)

img_shape = img_original_RGB.shape
img_type = img_original_RGB.dtype


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
    def __init__(self,min_size = 45, max_size = 60,min_angle = 0, max_angle = 240,min_width=15, max_width =20, factor_arco= 0.6):
        self.min_size = min_size
        self.max_size = max_size
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.min_width = min_width
        self.max_width = max_width
        self.factor_arco = factor_arco


    def generate_Random_Pincelada(self, tipo = ""):
        pincelada = Pincelada()
        if(tipo == ""):
            pincelada.tipo = self.random_Tipo()
        else:
            pincelada.tipo = tipo

        pincelada.width = self.random_Value_In_Range(self.min_width, self.max_width)
        pincelada.size = self.random_Value_In_Range(self.min_size, self.max_size)
        pincelada.angle = self.random_Value_In_Range(self.min_angle, self.max_angle)

        # los puntos se eligen despues de determinar size y angle y tipo
        pincelada.points = self.random_Points(pincelada.size, pincelada.angle, pincelada.tipo)

        # el color se toma donde empieza la pincelada (como en el codigo de leo)
        pincelada.color = self.point_Color(pincelada.points[0])

        #start y end se eligen despues de determinar tipo y angle
        if(pincelada.tipo == "arc"):
            pincelada.start, pincelada.end = self.random_Start_End(pincelada.angle)
            pincelada.width = math.ceil(pincelada.width* self.factor_arco)
        return pincelada

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
        return random.choice(shape_types)

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
        self.hedge_array = np.zeros((img_height, img_width))
        #self.image - se inicializa con generate_image

    def add_Pincelada(self,pincelada):
         self.lista_pinceladas.append(pincelada)

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
        self.image = image
        del draw_img, num_pinceladas
        return image


class AlgoritmoEvolutivo:

    def __init__(self,number_imagenes=10,number_pinceladas=100,number_generaciones=100,hedge_lambda=0.2,
                 prob_crossover=0.8,prob_mutation=0.05,size_torneo=3):
        self.number_chromosomes = number_imagenes
        self.number_genes = number_pinceladas
        self.number_generaciones = number_generaciones
        self.hedge_lambda = hedge_lambda
        self.prob_crossover = prob_crossover
        self.prob_mutation = prob_mutation
        self.size_torneo = size_torneo
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
        return hijo

    # mutacion por reemplazo: cada pincelada se cambia por una nueva con probabilidad prob_mutation
    def mutate_Chromosome(self, img_evol, randomizer):
        for j in range(0, len(img_evol.lista_pinceladas)):
            if(random.random() < self.prob_mutation):
                img_evol.lista_pinceladas[j] = randomizer.generate_Random_Pincelada()

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

            self.mutate_Chromosome(hijo, randomizer)
            hijo.update_Hedge_Array()   # el hijo empieza con su hedge en ceros
            nueva_generacion.append(hijo)

        self.list_chromosomes = nueva_generacion

    def evolve(self, randomizer, carpeta = "", cada_cuanto = 10):
        self.historial_fitness = []
        self.calculate_Fitness()

        for g in range(0, self.number_generaciones):
            mejor = min(self.fitness)
            self.historial_fitness.append(mejor)

            if(g % cada_cuanto == 0):
                print("generacion: " + str(g) + "   mejor fitness: " + str(round(mejor, 5)))
                if(carpeta != ""):
                    best_option = self.list_chromosomes[self.fitness.index(mejor)]
                    best_option.image.save(carpeta + "/generacion_" + str(g) + ".png")

            self.create_Next_Generation(randomizer)
            self.calculate_Fitness()

        mejor = min(self.fitness)
        self.historial_fitness.append(mejor)
        print("generacion: " + str(self.number_generaciones) + "   mejor fitness: " + str(round(mejor, 5)))
        if(carpeta != ""):
            best_option = self.list_chromosomes[self.fitness.index(mejor)]
            best_option.image.save(carpeta + "/generacion_" + str(self.number_generaciones) + ".png")


# ---------------- se corre el algoritmo ----------------

os.makedirs(carpeta_salida, exist_ok=True)

randomizer = Pincelada_Randomizer()
algoritmo_evol = AlgoritmoEvolutivo(number_imagenes, number_pinceladas, number_generaciones, hedge_lambda,
                                    prob_crossover, prob_mutation, size_torneo)

algoritmo_evol.create_Chromosomes(randomizer)
algoritmo_evol.evolve(randomizer, carpeta_salida, 10)

# grafica del mejor fitness por generacion
plt.plot(algoritmo_evol.historial_fitness)
plt.xlabel("generacion")
plt.ylabel("mejor fitness")
plt.title("Algoritmo evolutivo - fase 1")
plt.savefig(carpeta_salida + "/fitness.png")

algoritmo_evol.show_Best_Option()
plt.show()
