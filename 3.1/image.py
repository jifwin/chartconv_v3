__author__ = 'grzegorz'

import cv2
import colorsys
from pixel import Pixel
from grouping import group_values
import numpy as np
from neighbour import neighbour, angle
import labels
import os

angles_thr = 25 #parameter, number of angles to calculate mean
line_thr = 10 #parameter, minimum number of pixels to be treated as line

class Image:
    def __init__(self,path):
        self.path = path

    def load(self):
        print "Loading file..."
        self.img = cv2.imread(self.path)
        self.img_shape = self.img.shape
        print "Loaded " + str(self.img_shape[0]) + "x" + str(self.img_shape[1]) + " image.\n"


    def detect_axis(self):
        print "Detecting axis..."
        self.gray = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)
        [self.o_point,self.x_axis_points,self.y_axis_points] = self.contour(self.gray)
        print "Found 0 point " + str(self.o_point) + "\n"

    def contour(self,gray):
        go_next = False
        while not go_next:
            ret,thresh = cv2.threshold(gray,127,255,1)
            contours,h = cv2.findContours(thresh,1,cv2.CHAIN_APPROX_SIMPLE) #find counters with aproximation to n-points
            img_area = gray.shape[0]*gray.shape[1]
            max_area = 0
            for cnt in contours:
                approx = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
                if len(approx)==4:
                    area = cv2.contourArea(cnt)
                    if area > max_area:
                        max_area = area
                        last_shape = approx

            percentage = max_area/float(img_area)*100
            print "Found inside image. " + str(int(percentage)) + "% of image."

            if(percentage > 50): #uznajemy ze to jest kontur wykresu
                go_next = True
            else:
                print "Too small contour. Increasing contrast by 1%"
                gray = cv2.multiply(gray,np.array([0.99])) #contrast change by 1%
                #increase contrast and back to while

        #todo: numpy without loop

        x_points = []
        y_points = []


        for item in last_shape:
            x_points.append(item[0][0])
            y_points.append(item[0][1])

        #todo: make it to be 2-long only! approx to 15=16 etc


        #find 0-point as minimum/maximum value of x and y
        o_point = [min(x_points), max(y_points)]
        return [o_point,x_points,y_points]

    def ocr_labels(self):
        print "Ocring labels..."
        labels.crop(self.gray,self.o_point[0],self.o_point[1]) #improve, don't use files
        [self.x_labels, self.y_labels] = labels.ocr()
        print "Found labels:"
        print "x:\t" + str(self.x_labels)
        print "y:\t" + str(self.y_labels)
        self.labels = [min(self.x_labels),max(self.x_labels),min(self.y_labels),max(self.y_labels)]
        print "\n"

    def crop(self):
        print "Cropping inside image..."


        #corners
        x_min = min(self.x_axis_points)
        x_max = max(self.x_axis_points)
        y_min = min(self.y_axis_points)
        y_max = max(self.y_axis_points)

        shift = 0 #deprecated

        self.inside_img = self.inside_img = self.img[y_min+shift:y_max-shift,x_min+shift:x_max-shift]
        cv2.imwrite('inside.png',self.inside_img) #todo: don't use file

    def find_pixels(self):
        print "Finding pixels..."
        self.pixels = []
        self.colors = [] #all kinds of colors in image
        for x in xrange(self.inside_img.shape[0]):
            for y in xrange(self.inside_img.shape[1]):
                rgb_values = self.inside_img[x,y]
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

                    if rgb_values not in self.colors:
                        self.colors.append(rgb_values)
                    self.pixels.append(new_pixel)

    def remove_border_lines(self):
        print "Removing border lines..."
        x_points = {}
        y_points = {}

        for item in self.pixels:

            x = item.x
            y = item.y

            if x in x_points:
                x_points[x] = x_points[x] + 1
            else:
                x_points[x] = 1

            if y in y_points:
                y_points[y] = y_points[y] + 1
            else:
                y_points[y] = 1

            x_mean = 0
            y_mean = 0

            for key in x_points:
                x_mean += x_points[key]
            x_mean = x_mean/len(x_points)

            for key in y_points:
                y_mean += y_points[key]
            y_mean = y_mean/len(y_points)

            #average points number
            #if a-times more that avg then remove
            #candidates to remove

            thr = 10 #a-times parameter

            new_x = {k: v for k, v in x_points.iteritems() if v > thr*x_mean}.keys()
            new_y = {k: v for k, v in y_points.iteritems() if v > thr*y_mean}.keys()

            new_pixels = []

            #removing points

        for item in self.pixels:
            x = item.x
            y = item.y

            if ((x not in new_x) and (y not in new_y)):
                new_pixels.append(item)

        self.pixels = new_pixels

    def remove_labels_lines(self):
        pass

    def group_pixels(self):
        print "Grouping pixels..."
        new_pixels = []

        for x in xrange(self.img_shape[1]):
            column = [pixel for pixel in self.pixels if pixel.x == x]
            if(len(column) > 0):

                y_values = [pixel.y for pixel in column]
                y_values_grouped = group_values(y_values)
                for group in y_values_grouped:
                    if len(group) > 0:
                        y_mean = np.mean(group)
                        y_middle = min(group, key=lambda y: abs(y-y_mean)) #choose closest to min

                        #todo:
                        pix = next(pixel for pixel in column if pixel.x == x and pixel.y == y_middle)
                        new_pixels.append(pix)
        self.pixels = new_pixels

    def detect_lines(self):
        print "Detecting lines..."
        self.lines = []
        i = 0
        j = 0
        pixels_original = list(self.pixels)
        while(len(self.pixels) > 0):

            line = []
            angles = []
            pixel = self.pixels[i]

            while(pixel is not None):
                line.append(pixel)
                #img[pixel.y,pixel.x] = [pixel.r,pixel.g,pixel.b]
                pixel_old = pixel
                pixel = neighbour(pixel,self.pixels,angles)

                #calculate angle between pixels
                if pixel is not None:
                    ang = angle(pixel_old,pixel)

                    angles.append(ang)
                    if len(angles) > angles_thr:
                        angles.remove(angles[0])

                    #removing pixel between old and new pixel
                    x_borders = [pixel_old.x, pixel.x]
                    y_borders = [min([pixel_old.y,pixel.y]),max([pixel_old.y,pixel.y])]

                    pixels_inside = [item for item in self.pixels if x_borders[0] <= item.x <= x_borders[1] and y_borders[0] <= item.y <= y_borders[1]]

                    for item in pixels_inside:
                        #print str(item)
                        self.pixels.remove(item)

                if pixel_old in self.pixels:
                    self.pixels.remove(pixel_old)

            j += 1
            if len(line) > line_thr:
                self.lines.append(line)

    def change_axis(self):
        print "Chaning axises..."

        max_x_point = 0
        max_y_point = 0

        for line in self.lines:
            for pixel in line:
                if pixel.x > max_x_point:
                    max_x_point = pixel.x
                if pixel.y > max_y_point:
                    max_y_point = pixel.y

        for i in xrange(len(self.lines)): #iterate over lines
            print "new line"
            for j in xrange(len(self.lines[i])): #iterate over line - pixels
                tmp_pix = self.lines[i][j]
                tmp_pix.y = abs(max_y_point-tmp_pix.y)#change y coordinate
                self.lines[i][j] = tmp_pix
                print str(self.lines[i][j])

    def scale_pixels(self):
        print "Scaling pixels..."
        x_range = self.labels[1]-self.labels[0]
        y_range = self.labels[3]-self.labels[2]

        #todo: improve finding max, together with chanign axis
        max_x_point = 0
        max_y_point = 0

        for line in self.lines:
            for pixel in line:
                if pixel.x > max_x_point:
                    max_x_point = pixel.x
                if pixel.y > max_y_point:
                    max_y_point = pixel.y

        #todo: use comprehensive list
        new_pixels = []

        #scaling

        for i in xrange(len(self.lines)): #iterate over lines
            print "new line"
            for j in xrange(len(self.lines[i])): #iterate over line - pixels
                tmp_pix = self.lines[i][j]
                tmp_pix.x = self.labels[0]+x_range*tmp_pix.x/float(max_x_point)
                tmp_pix.y = self.labels[2]+y_range*tmp_pix.y/float(max_y_point)
                self.lines[i][j] = tmp_pix
                print str(self.lines[i][j])

    def write_data_to_file(self):

        self.lines.sort(key= lambda s: len(s)) #sorting plots by length of them
        print "Writing data file..."

        for [i,pixels] in enumerate(self.lines):
            f = open('data' + str(i) + '.dat','w')
            for pixel in pixels:
                f.write(str(pixel.x) + "\t" + str(pixel.y) + "\n")
            f.close()


    def create_ps(self):
        print "Creating ps file"


        addplots_string = ""
        color = ["red", "green", "blue", "black", "yellow", "red", "green", "blue", "black", "yellow", "red", "green", "blue", "black", "yellow", "red", "green", "blue", "black", "yellow"] #todo: imrpveo
        for i in range(0,len(self.lines)):
            addplots_string += "\\addplot[color=" + color[i] + ", mark=none, smooth] file{data" + str(i) + ".dat};\n"
            #addplots_string += "\\addplot[only marks, mark size=0.1] file{data" + str(i) + ".dat};\n"
        '''
        \\addplot[mark=none] file{data.dats}; ,smooth
        only marks
        '''


        test_text = """
            \documentclass{standalone}
            \usepackage{tikz}
            \usepackage{pgfplots}

            \\begin{document}
            \\begin{tikzpicture}

            \\begin{axis}
            [xlabel=x,ylabel=y,
             xmin=""" + str(self.labels[0]) + """, xmax=""" + str(self.labels[1]) + """, ymin=""" + str(self.labels[2]) + """, ymax=""" + str(self.labels[3]) + """,
             width=\\textwidth]
            """

        test_text += addplots_string
        test_text += """
            \end{axis}


            \end{tikzpicture}
            \end{document}
            """


        #todo: obsluga bledow otwarcia plikow itp
        f = open('test.tex','w')
        f.write(test_text)
        f.close()

        #todo: to imporve
        os.system('lualatex test.tex')
        os.system('pdf2ps test.pdf test.ps')
        os.system('rm test.pdf')
        os.system('mv test.ps ' + self.path + ".ps")
        os.system('rm data*.dat')
        print "Done"



    def draw(self):

        print "Drawing..."
        print str(len(self.lines)) + " lines to draw."
        img = np.ones([self.inside_img.shape[0],self.inside_img.shape[1],3]) * 255

        for line in self.lines:
            for pixel in line:
                img[pixel.y,pixel.x] = [pixel.r,pixel.g,pixel.b]

        cv2.imwrite("wynik.bmp",img)


