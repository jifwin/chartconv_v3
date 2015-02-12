__author__ = 'grzegorz'

import numpy as np

class Pixel:

    def __init__(self,x,y,r,g,b):
        self.x = x
        self.y = y
        self.r = r
        self.g = g
        self.b = b

    def __str__(self):
        return str([self.x,self.y]) + str([self.r,self.g,self.b])

    def find_vertical_neighbours(self,pixels):
        x = self.x
        y = self.y

        pixels_coor = [[pixel.x, pixel.y] for pixel in pixels]#coordinates only

        self.neighbours = []
        self.neighbours.append([x,y])

        y2 = y+1 #up
        while([x,y2] in pixels_coor):
            self.neighbours.append([x,y2])
            y2 += 1

        y2 = y-1 #down
        while([x,y2] in pixels_coor):
            self.neighbours.append([x,y2])
            y2 -= 1

        self.neighbours.sort()
        print self.neighbours

    def find_mean_vertical_pixel(self):
        y_values = [coor[1] for coor in self.neighbours]
        y_mean = np.mean(y_values)
        self.y_middle = min(y_values, key=lambda y: abs(y-y_mean)) #choose closest to min

    def vertical_pixel(self,pixels):
        self.find_vertical_neighbours(pixels)
        self.find_mean_vertical_pixel()
        pixel = next(pixel for pixel in pixels if (pixel.x == self.x and pixel.y == self.y_middle))
        return pixel

    def change_to_mean_vertical(self):
        self.y = self.y_middle

    def find_horizontal_neighbours(self,pixels):
        pixels_coor = [[pixel.x, pixel.y] for pixel in pixels]#coordinates only
        #first horizontal


        #then cross

    def find_next(self,pixels):
        self.vertical_pixel(pixels)
        pixel = next(pixel for pixel in pixels if (pixel.x == self.x+159 and pixel.y == self.y_middle))
        print pixel

        return pixel

    def rgb(self):
        return [self.r,self.g,self.b]


