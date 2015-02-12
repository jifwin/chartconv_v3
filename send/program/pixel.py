import numpy as np

class Pixel:

    def __init__(self,x,y,r,g,b): #constructor
        self.x = x
        self.y = y
        self.r = r
        self.g = g
        self.b = b

    def __str__(self): #printing pixel
        return str([self.x,self.y]) + str([self.r,self.g,self.b])

    def find_vertical_neighbours(self,pixels):
        x = self.x
        y = self.y

        pixels_coor = [[pixel.x, pixel.y] for pixel in pixels]#coordinates only

        self.neighbours = []
        self.neighbours.append([x,y])

        y2 = y+1 #up searching
        while([x,y2] in pixels_coor):
            self.neighbours.append([x,y2])
            y2 += 1

        y2 = y-1 #down searching
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

    def rgb(self): #return rgb color of pixel
        return [self.r,self.g,self.b]


