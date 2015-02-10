__author__ = 'grzegorz'

import math
from colormath.color_objects import XYZColor,sRGBColor,LabColor
from colormath.color_conversions import convert_color
import numpy as np

def distance(pixel1, pixel2):
    return math.sqrt(pow(pixel1.x-pixel2.x,2)+pow(pixel1.y-pixel2.y,2))

#deprecated
def color_distance(pixel1,pixel2):

    #pip install colormath
    #pip install networkx

    #rgb to xyz
    #xyz to lab

    #lab metric

    rgb1 = sRGBColor(pixel1.r,pixel1.g,pixel1.b)
    rgb2 = sRGBColor(pixel2.r,pixel2.g,pixel2.b)
    xyz1 = convert_color(rgb1,XYZColor, target_illuminant='d50')
    xyz2 = convert_color(rgb2,XYZColor, target_illuminant='d50')
    lab1 = convert_color(xyz1, LabColor)
    lab2 = convert_color(xyz2, LabColor)

    delta_l = pow(lab1.lab_l-lab2.lab_l,2)
    delta_a = pow(lab1.lab_a-lab2.lab_a,2)
    delta_b = pow(lab1.lab_b-lab2.lab_b,2)

    diff = math.sqrt(delta_l+delta_a+delta_b)
    return diff

def neighbour(pixel,pixels,angles,closest_thr,maximum_distance):
    #remove smaller x and self

    used_pixels = []

    pixels = [item for item in pixels if item.x >= pixel.x and distance(pixel,item) < maximum_distance and item != pixel and [pixel.r,pixel.g,pixel.b] == [item.r,item.g,item.b]]
    if len(pixels) > 0:

        nearest_pixels = sorted(pixels,key=lambda item: distance(pixel,item))[0:closest_thr] #closest pixels
        used_pixels.append(nearest_pixels)
        #print "nirest"
        #print str(pixel)

        if(len(angles) > 0):
            ang = sum(angles)/float(len(angles)) #mean angle
        else: #if no angles yet use mean of 5 closest pixels
            #print "nie mam zadnego, biore sredni"
            angles = [angle(pixel,item) for item in nearest_pixels]
            ang = sum(angles)/float(len(angles))
            #print ang
            #print "sredni"

        #print "correct angle:" + str(ang)


        nearest_pixels = sorted(nearest_pixels,key=lambda item: abs(ang-angle(pixel,item)))

        #for item in nearest_pixels:
        #    print str(item) + "\t" +\
        #          str(abs(ang-angle(pixel,item)))
        #print "wybralem:"
        #print nearest_pixels[0]


        #raw_input()
        return nearest_pixels[0]
        #return min(pixels, key=lambda item: distance(pixel,item))
    else:
        return None

def mean_angle(angles): #weighted mean
    l = len(angles)
    gauss_x = np.linspace(-1,1,l)
    gauss_y = [np.exp(-1*pow(x,2)) for x in gauss_x]

    weighted_angles = gauss_y * np.array(angles)

    return sum(weighted_angles)/float(len(weighted_angles))
    #return sum(angles)/float(len(angles))

def angle(pixel1,pixel2):
    x1 = pixel1.x
    x2 = pixel2.x
    y1 = pixel1.y
    y2 = pixel2.y

    if x2 != x1:
        tan = (y2-y1)/float(x2-x1)
        ang = math.atan(tan)*float(180)/float(math.pi)
    else:
        ang = 90
    return ang