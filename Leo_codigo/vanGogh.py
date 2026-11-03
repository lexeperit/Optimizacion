import random
import math
from PIL import Image, ImageDraw
from collections import namedtuple
import numpy as np

pincelada_size = 30
pincelada_thickness = 10
number_imagenes = 10
number_pincelada = 100
hedge_lambda = 0.2 

Pincelada = namedtuple('Pincelada', ['position_x', 'position_y', 'angule', 'size', 'thickness', 'color'])

def limit_values(size, angule, random_value, img_array_shape, sin_cos):
    angule_value = math.cos(angule) if sin_cos == "cos" else math.sin(angule)
    if random_value + size * angule_value < img_array_shape and random_value + size * angule_value > 0:
        return random_value + size * angule_value
    elif random_value + size * angule_value <= 0:
        return 0
    elif  random_value + size * angule_value >= img_array_shape:
        return img_array_shape - 1

def generate_pincelada(img_array):
    random_x = random.randint(1,img_array.shape[1]-1)
    random_y = random.randint(1,img_array.shape[0]-1)
    angule = math.radians(random.randint(0,359))
    color_r = int(img_array[random_y, random_x, 0])
    color_g = int(img_array[random_y, random_x, 1])
    color_b = int(img_array[random_y, random_x, 2]) 
    return Pincelada(position_x = random_x, position_y = random_y, angule = angule, size = pincelada_size, thickness = pincelada_thickness, color = (color_r, color_g, color_b))

def draw_pincelada(pincelada, img_evol, hedge_array, shape_x, shape_y):
    draw_image = ImageDraw.Draw(img_evol) 
    draw_image.line([pincelada.position_x, pincelada.position_y, 
                         limit_values(pincelada.size, pincelada.angule, pincelada.position_x, shape_x, "cos"), 
                         limit_values(pincelada.size, pincelada.angule, pincelada.position_y, shape_y, "sin")
                        ], pincelada.color, width = pincelada.thickness)

    if len(hedge_array) != 0:
        img_tmp = Image.new("RGB", [img_evol.width, img_evol.height])
        draw_tmp = ImageDraw.Draw(img_tmp)
        draw_tmp.line([pincelada.position_x, pincelada.position_y, 
                                 limit_values(pincelada.size, pincelada.angule, pincelada.position_x, shape_x, "cos"), 
                                 limit_values(pincelada.size, pincelada.angule, pincelada.position_y, shape_y, "sin")
                                ], (255,255,255), width = pincelada.thickness)
        
        pincel_coverage(hedge_array, np.array(img_tmp))
 
def pincel_coverage(hedge_array, array_tmp):
    filas, columnas = np.where(np.all(array_tmp == 255, axis=-1))
    hedge_array[filas, columnas] = 1
    
def generate_img(cromosome, img_evol, hedge_array, img_shape_x, img_shape_y):
    for i in range(len(list_pincelada)):
        draw_pincelada(cromosome[i], img_evol, hedge_array, img_shape_x, img_shape_y)


def oo_mse(img_orignal, img_offpring, hedge_array):
    filas, columnas = np.where(hedge_array == 1)
    e_contenido = 65025
    porcent_hedge = 0.0
    if len(filas) != 0:
        img_orignal_signo = img_orignal.astype(np.int32)
        img_orignal_signo = img_orignal_signo[filas, columnas]
        img_offpring_signo = img_offpring.astype(np.int32)
        img_offpring_signo = img_offpring_signo[filas, columnas]
        e_contenido = (img_orignal_signo - img_offpring_signo)**2
        e_contenido = np.mean(e_contenido)
        porcent_hedge = len(filas)/((len(hedge_array) * len(hedge_array[0]))) 
    e_contenido = (e_contenido/65025) + (hedge_lambda * (1 - porcent_hedge))
    #print(e_contenido)
    return e_contenido

with Image.open("roger.jpg") as img:
    #img.show()
    img_RGB = img.convert("RGB")
    img_width = img.width
    img_height = img.height
    img_array = np.array(img_RGB)

img_shape = img_array.shape
img_type = img_array.dtype

cromosome = []
for i in range(number_imagenes):
    list_pincelada = []
    for j in range(number_pincelada):
        pincelada = generate_pincelada(img_array)
        list_pincelada.append(pincelada)
    cromosome.append(list_pincelada) 

fitness = []
for i in range(number_imagenes):
    img_evol = Image.new("RGB", [img_width, img_height])
    hedge_array = np.zeros((img_height, img_width))
    generate_img(cromosome[i], img_evol, hedge_array, img_array.shape[1], img_array.shape[0])
    value = oo_mse(img_array, np.array(img_evol), hedge_array)
    fitness.append(value)

best_option = cromosome[fitness.index(min(fitness))]
generate_img(best_option, img_evol, [],img_array.shape[1], img_array.shape[0])
img_evol.show()



