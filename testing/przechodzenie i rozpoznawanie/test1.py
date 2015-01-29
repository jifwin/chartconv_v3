__author__ = 'grzegorz'

import cv2
from pixel import Pixel
from line import Line
import numpy as np

img = cv2.imread("test.bmp")

'''
for item in np.ndenumerate(img):
    print item
    raw_input("stop")
'''

img_shape = img.shape
print img_shape

pixels = []

for y in xrange(img_shape[0]):
    for x in xrange(img_shape[1]):
        rgb_values = img[x,y]
        if sum(rgb_values) != 3*255: #white
            #print rgb_values
            new_pixel = Pixel(y,x,rgb_values[0],rgb_values[1],rgb_values[2])
            pixels.append(new_pixel)

'''
for item in pixels:
    print item
'''

used_pixels = []


for pixel in pixels:
    new_line = Line(pixel, pixels)
    new_line.go()

    raw_input("stop")

