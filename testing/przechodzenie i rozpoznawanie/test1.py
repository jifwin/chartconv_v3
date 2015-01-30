__author__ = 'grzegorz'

import cv2
from pixel import Pixel
from grupowanie import group_values
from neighbour import neighbour, angle
import numpy as np
import colorsys
import sys

#parameters:
line_thr = 10 #minimum number of pixels to be treated as line
angles_thr = 15 #number of angles to mean

print "Loading file..."
img = cv2.imread(sys.argv[1])


#incrising level - for inside image #todo:


'''
for item in np.ndenumerate(img):
    print item
    raw_input("stop")
'''

img_shape = img.shape
print img_shape

pixels = []
print "Finding pixels..."
for x in xrange(img_shape[0]):
    for y in xrange(img_shape[1]):
        rgb_values = img[x,y]
        if sum(rgb_values) != 3*255: #white


            #increasing saturation
            rgb =[item/float(255) for item in rgb_values]
            hsv = list(colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2]))

            if hsv[0] == 0 and hsv[1] == 0: #if black or grey shade
                hsv[2] = 0 #set value to 0 (pure black)

            else: #if any color other than black
                hsv[1] = 1 #set saturation to max value
                hsv[2] = 1 #set value to max value

            rgb_values = list(colorsys.hsv_to_rgb(hsv[0],hsv[1],hsv[2]))#convert back to rgb
            rgb_values = [item*255 for item in rgb_values] #normalize to 255

            new_pixel = Pixel(y,x,rgb_values[0],rgb_values[1],rgb_values[2])
            pixels.append(new_pixel)

new_pixels = []

print "Grouping pixels..."
for x in xrange(img_shape[1]):
    column = [pixel for pixel in pixels if pixel.x == x]
    if(len(column) > 0):

        y_values = [pixel.y for pixel in column]
        y_values_grouped =  group_values(y_values)
        for group in y_values_grouped:
            if len(group) > 0:
                y_mean = np.mean(group)
                y_middle = min(group, key=lambda y: abs(y-y_mean)) #choose closest to min

                #todo:
                pix = next(pixel for pixel in column if pixel.x == x and pixel.y == y_middle)
                #print "wybrany\t" + str(pix)
                new_pixels.append(pix)
                #temporary#finding pixel with that coor


img_line = np.ones([img_shape[0],img_shape[1],3]) * 255

'''
print "Writing out.bmp..."
for pixel in new_pixels:
    x = pixel.x
    y= pixel.y
    img_line[y,x] = [pixel.r,pixel.g,pixel.b]
cv2.imwrite("out.bmp",img_line)
'''

    #go lines

    #tutaj posortowac!? #todo:


pixels = new_pixels
pixels_copy = pixels

print "Detecting lines..."

lines = []

tmp = np.ones([img_shape[0],img_shape[1],3]) * 255

i = 0
j = 0

while(len(pixels_copy) > 0):

    line = []
    angles = []

    pixel = pixels_copy[i]
    #print pixel


    while(pixel is not None):
        line.append(pixel)
        #img[pixel.y,pixel.x] = [pixel.r,pixel.g,pixel.b]
        tmp[pixel.y,pixel.x] = [0,0,0]
        pixel_old = pixel
        pixel = neighbour(pixel,pixels,angles)

        #calculate angle between pixels
        if pixel is not None:
            ang = angle(pixel_old,pixel)

            angles.append(ang)
            if len(angles) > angles_thr:
                angles.remove(angles[0])

            #removing pixel between old and new pixel
            x_borders = [pixel_old.x, pixel.x]
            y_borders = [min([pixel_old.y,pixel.y]),max([pixel_old.y,pixel.y])]

            #print "borders"
            #print x_borders, y_borders
            pixels_inside = [item for item in pixels if x_borders[0] <= item.x <= x_borders[1] and y_borders[0] <= item.y <= y_borders[1]]

            for item in pixels_inside:
                #print str(item)
                pixels.remove(item)

        if pixel_old in pixels:
            pixels.remove(pixel_old)

    j += 1
    if len(line) > line_thr:
        #print "Line length: " + str(len(line))
        lines.append(line)


print "Drawing..."
img = np.ones([img_shape[0],img_shape[1],3]) * 255

for line in lines:
    #print len(line)
    for pixel in line:
        img[pixel.y,pixel.x] = [pixel.r,pixel.g,pixel.b]

    #cv2.imshow("test",img)
    #cv2.waitKey()
cv2.imwrite("wynik.bmp",img)





