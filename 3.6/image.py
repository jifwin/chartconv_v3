import cv2
import colorsys
from pixel import Pixel
from grouping import group_values
import numpy as np
from neighbour import neighbour, angle
import labels
import os
import math
from pytesser import *

class Image:
    def __init__(self,path,arguments):
        self.path = path
        self.arguments = arguments

        #parameters for image class
        self.plotarea = float(arguments.plotarea)
        self.legend_tol = float(arguments.legend_tol)
        self.legend_area = float(arguments.legend_area)
        self.extra_shift_legend = float(arguments.extra_shift_legend)
        self.lines_merge = float(arguments.lines_merge)
        self.border_thr = float(arguments.border_thr)
        self.angles_thr = float(arguments.angles)
        self.line_thr = float(arguments.line_thr)
        self.colors_thr = float(arguments.colors_thr)
        self.border_len = float(arguments.border_len)
        self.labels_lines_len = float(arguments.labels_lines_len)
        self.label_line_len_min = float(arguments.label_line_len_min)
        self.min_line = float(arguments.min_legend_line)
        self.max_line = float(arguments.max_legend_line)


        #parameters for neighbour:
        self.neighbours = int(arguments.neighbours)
        self.max_dist = float(arguments.max_dist)

    def load(self):
        print "Loading file..."
        self.img = cv2.imread(self.path)
        self.img_shape = self.img.shape #image dimensions
        print "Loaded " + str(self.img_shape[0]) + "x" + str(self.img_shape[1]) + " image.\n"


    def detect_axis(self):
        print "Detecting axis..."
        self.gray = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY) #converting to gray
        [self.o_point,self.x_axis_points,self.y_axis_points] = self.contour(self.gray) #finding 0-point and axis points
        print "Found 0 point " + str(self.o_point) + "\n"

    def contour(self,gray):
        go_next = False #correct contour found flag
        self.legend_cnt = None #legend contour

        #whole image area
        img_area = gray.shape[0]*gray.shape[1]

        thr = 0.005 #minimal contour size, used to remove really small contours

        while not go_next: #while not found
            #detecting contours
            ret,thresh = cv2.threshold(gray,127,255,1)
            contours,h = cv2.findContours(thresh,1,cv2.CHAIN_APPROX_SIMPLE) #find contours with aproximation

            contours = [cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True) for cnt in contours] #approx contour
            contours = [cnt for cnt in contours if len(cnt) == 4] #rectangles only
            contours = [cnt for cnt in contours if cv2.contourArea(cnt)/float(img_area)*100 > thr] #remove small contours

            last_shape = max(contours,key=lambda cnt: cv2.contourArea(cnt)) #contour with max area - border
            max_area = cv2.contourArea(last_shape) #max area of contour

            percentage = max_area/float(img_area)*100 #max area compared to whole image
            print "Found inside image. " + str(int(percentage)) + "% of image."

            if(percentage > self.plotarea): #if more than 50% than this is the main rectangle
                contours = [cnt for cnt in contours if not np.array_equal(last_shape,cnt)] #all except currently used

                #legend
                #calculate diagonals

                for cnt in contours:

                    #diagonals of contour
                    dig1 = self.points_distance(cnt[0],cnt[2])
                    dig2 = self.points_distance(cnt[1],cnt[3])

                    #contour lines length
                    l0 = self.points_distance(cnt[0],cnt[1])
                    l1 = self.points_distance(cnt[1],cnt[2])
                    l2 = self.points_distance(cnt[2],cnt[3])
                    l3 = self.points_distance(cnt[3],cnt[0])



                    #if diagonals and sides equal
                    if(min([dig1,dig2])/float(max([dig1,dig2])) >= self.legend_tol and
                        min([l1,l3])/float(max([l1,l3])) >= self.legend_tol and
                        min([l0,l2])/float(max([l0,l2])) >= self.legend_tol and
                        cv2.contourArea(cnt) < float(self.legend_area)*cv2.contourArea(last_shape) #if legend smaller than main contour
                    ):

                        self.legend_cnt = cnt

                        #for debug only
                        #cv2.drawContours(gray, [self.legend_cnt], 0, (0,255,0), 3)
                        #cv2.imshow("gray",gray)
                        #cv2.waitKey()

                        break #found correct legend

                go_next = True
            else:
                #increase contrast and back to while
                print "Too small contour. Increasing contrast by 1%"

        x_points = []
        y_points = []

        for item in last_shape:
            x_points.append(item[0][0])
            y_points.append(item[0][1])

        #find 0-point as minimum/maximum value of x and y
        o_point = [min(x_points), max(y_points)] #0 point
        return [o_point,x_points,y_points]

    def points_distance(self,point1,point2):
        return math.sqrt(math.pow(point1[0][0]-point2[0][0],2)+math.pow(point1[0][1]-point2[0][1],2))

    def ocr_labels(self):
        print "Ocring labels..."
        labels.crop(self.gray,self.o_point[0],self.o_point[1],self.arguments)
        [self.x_labels, self.y_labels,self.x_type,self.y_type] = labels.ocr()
        print "Found labels:"
        print "x:\t" + str(self.x_labels) + "\t type: " + self.x_type
        print "y:\t" + str(self.y_labels) + "\t type: " + self.y_type
        self.labels = [min(self.x_labels),max(self.x_labels),min(self.y_labels),max(self.y_labels)]
        print "\n"

    def analyze_legend(self):
        self.legend = []
        #if legend detected:
        if self.legend_cnt != None:
            print "Analyzing legend..."
            x_legend = []
            y_legend = []

            #find correct legend contours
            for item in self.legend_cnt:
                x_legend.append(item[0][0])
                y_legend.append(item[0][1])

            #legend corners
            self.x_min_legend = min(x_legend)
            self.x_max_legend = max(x_legend)
            self.y_min_legend = min(y_legend)
            self.y_max_legend = max(y_legend)

            extra_shift = int(self.extra_shift_legend) #pixels to ignore

            #inside legend image
            self.legend = self.img[self.y_min_legend+extra_shift:self.y_max_legend-extra_shift,self.x_min_legend+extra_shift:self.x_max_legend-extra_shift]

            #cv2.imwrite('legend.png',self.legend) #debug only
            legend_img = cv2.imread('legend.png') #debug only

            #detect straigh horizontal lines and colors
            legend_img = self.legend
            legend_size = legend_img.shape #legend dimensions
            horizontal_size = legend_size[1]
            vertical_size = legend_size[0]

            #detect lines
            gray = cv2.cvtColor(legend_img,cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray,50,150,apertureSize = 3)


            minLineLength = float(self.min_line)*horizontal_size
            maxLineLength = float(self.max_line)*horizontal_size


            lines = cv2.HoughLinesP(edges,1,np.pi/180,50) #hough transform - find lines


            legend_lines = []

            for x1,y1,x2,y2 in lines[0]:

                length = math.sqrt(pow(x2-x1,2)+pow(y2-y1,2)) #length of line

                if (minLineLength < length < maxLineLength and #if appropriate length
                    abs(x1-x2)) > 2: #and if not vertical (2 - tolerance parameter)
                        legend_lines.append([x1,y1,x2,y2])

            legend_lines.sort(key=lambda item: item[1]) #sort by y


            y_min = min(legend_lines, key=lambda line: line[0])[0] #min value
            y_max = max(legend_lines, key=lambda line: line[2])[2] #max value


            #averaging lines:
            avg_thr = float(self.lines_merge)*float(vertical_size)

            new_lines = []
            for line in legend_lines:
                y = line[1]

                #find closest
                rest = [item for item in legend_lines if y != item[1]] #all but not current
                closest = min(rest ,key=lambda item: abs(item[1]-y)) #closest line


                if abs(closest[1]-y) < avg_thr: #if close enough
                    avg_line = []
                    for i in xrange(len(closest)):#build closest line
                        avg_line.append((closest[i]+line[i])/2.0) #avg line
                    new_lines.append(avg_line) #add avg line
                else:
                    new_lines.append(line)

            legend_lines = new_lines

            legend_lines.sort(key=lambda item: item[1]) #sort by y
            legend_lines = [list(x) for x in set(tuple(x) for x in new_lines)] #make unique


            #find colors of each lines
            new_lines = []
            for line in legend_lines:

                #take avg point of line
                avg_x = int(np.mean([line[0],line[2]]))
                avg_y = int(np.mean([line[1],line[3]]))
                #color of line
                color = legend_img[avg_y,avg_x]


                white = 3*255
                if sum(color) == white: #wrong color,check above and below pixel
                    color = legend_img[avg_y-1,avg_x] #below
                    print "Fixed color below:" + str(color)
                if sum(color) == white: #if still white
                    color = legend_img[avg_y+1,avg_x] #above
                    print "Fixed color above:" + str(color)
                if sum(color) == white:
                    print "Error with finding color of legend line!"

                #debug only
                '''
                cv2.circle(gray,(avg_x,avg_y),5,(0,255,255))
                cv2.imshow("gray",gray)
                cv2.waitKey()
                '''

                #increase color saturation:
                hsv = list(colorsys.rgb_to_hsv(color[2]/float(255), color[1]/float(255), color[0]/float(255)))

                if hsv[0] == 0 and hsv[1] == 0: #if black or grey shade
                    hsv[2] = 0 #set value to 0 (pure black)

                else: #if any color other than black
                    hsv[1] = 1 #set saturation to max value
                    hsv[2] = 1 #set value to max value

                color = list(colorsys.hsv_to_rgb(hsv[0],hsv[1],hsv[2]))#convert back to rgb
                color = [round(item*255) for item in color] #round and normalize to 255

                new_lines.append([[avg_x,avg_y],color])
            legend_lines = new_lines #with color and single pixel

            legend_lines.sort(key=lambda item: item[0][1]) #sort by y reversed

            #remove lines before OCR
            #lines on left or right?
            if y_max > 0.5*(self.y_max_legend-self.y_min_legend): #on right in more than half of image
                legend_texts_img = legend_img[:,:y_min-1]
            else:
                legend_texts_img = legend_img[:,y_max+1:]


            #increase size for better recognition
            legend_texts_img = cv2.resize(legend_texts_img, (0,0), fx=5, fy=5)
            cv2.imwrite("legend_texts.png",legend_texts_img)

            #detect strings
            legend_string = image_file_to_string('legend_texts.png').split("\n")
            legend_string = [string for string in legend_string if len(string) > 0] #remove empty

            self.legend = [] #string + color
            if len(legend_string) == len(legend_lines):
                for i in xrange(len(legend_string)):
                    self.legend.append([legend_string[i],legend_lines[i][1]]) #1 - line color
            else:
                print "Length of strings and lines not equal!"

            print "Legend:"
            print self.legend

    def crop(self):
        print "Cropping inside image..."

        #corners
        x_min = min(self.x_axis_points)
        x_max = max(self.x_axis_points)
        y_min = min(self.y_axis_points)
        y_max = max(self.y_axis_points)

        #if legend detected:
        if self.legend_cnt != None:
            print "Removing legend pixels..."
            for y in xrange(self.img.shape[0]):
                for x in xrange(self.img.shape[1]):
                    #if inside legend
                    border_tolerance = 3 #in pixels#parameter: thr border padding
                    if (self.x_min_legend-border_tolerance <= x <= self.x_max_legend+border_tolerance and
                        self.y_min_legend-border_tolerance <= y <= self.y_max_legend+border_tolerance
                        ):
                        self.img[y,x] = [255,255,255] #paint white


        #inside image - main area of plot
        self.inside_img = self.img[y_min:y_max,x_min:x_max]
        cv2.imwrite('inside.png',self.inside_img)

    def find_pixels(self):
        print "Finding pixels..."
        self.pixels = []
        self.colors = {} #all kinds of colors in image
        for x in xrange(self.inside_img.shape[0]):
            for y in xrange(self.inside_img.shape[1]):
                rgb_values = self.inside_img[x,y]
                if sum(rgb_values) != 3*255: #if not white

                    #increasing saturation
                    rgb =[item/float(255) for item in rgb_values]
                    hsv = list(colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2]))

                    if hsv[0] == 0 and hsv[1] == 0: #if black or grey shade
                        hsv[2] = 0 #set value to 0 (pure black)

                    else: #if any color other than black
                        hsv[1] = 1 #set saturation to max value
                        hsv[2] = 1 #set value to max value

                    rgb_values = list(colorsys.hsv_to_rgb(hsv[0],hsv[1],hsv[2]))#convert back to rgb
                    rgb_values = [round(item*255) for item in rgb_values] #round and normalize to 255

                    new_pixel = Pixel(y,x,rgb_values[0],rgb_values[1],rgb_values[2]) #declare new pixel with coordinates and rgb values

                    #add color to dict
                    rgb_tuple = tuple(rgb_values)
                    if rgb_tuple not in self.colors:
                        self.colors[rgb_tuple] = 1
                    else:
                        self.colors[rgb_tuple] += 1

                    self.pixels.append(new_pixel) #add new pixel to pixel list

    def remove_border_lines(self):
        print "Removing border lines..."
        x_points = {}
        y_points = {}

        #corners of main image
        self.x_min = min(self.pixels, key=lambda pixel: pixel.x).x
        self.x_max = max(self.pixels, key=lambda pixel: pixel.x).x
        self.y_min = min(self.pixels, key=lambda pixel: pixel.y).y
        self.y_max = max(self.pixels, key=lambda pixel: pixel.y).y

        #count pixels on borders
        for item in self.pixels:
            x = item.x
            y = item.y

            #if pixel in checking area
            if ((x <= self.x_min+self.border_len or
                x >= self.x_max-self.border_len or
                y <= self.y_min+self.border_len or
                y >= self.y_max-self.border_len) and
                item.rgb() == [0,0,0]): #only black borders

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

                thr = self.border_thr
                #candidates to remove
                new_x = {k: v for k, v in x_points.iteritems() if v > thr*x_mean}.keys() #if thr-times more that avg then remove
                new_y = {k: v for k, v in y_points.iteritems() if v > thr*y_mean}.keys()

        new_pixels = []

        #removing points
        for item in self.pixels:
            x = item.x
            y = item.y

            if ((x not in new_x) and (y not in new_y)):
                new_pixels.append(item)

        self.pixels = new_pixels #replace with new pixels

    def remove_labels_lines(self):
        new_pixels = []

        black = [0,0,0]

        #find border pixels (black)
        left = [pixel for pixel in self.pixels if pixel.x < self.x_min+self.labels_lines_len and black == pixel.rgb()]
        right = [pixel for pixel in self.pixels if pixel.x > self.x_max-self.labels_lines_len and black == pixel.rgb()]
        up = [pixel for pixel in self.pixels if pixel.y < self.y_min+self.labels_lines_len and black == pixel.rgb()]
        down = [pixel for pixel in self.pixels if pixel.y > self.y_max-self.labels_lines_len and black == pixel.rgb()]

        y_left_points = {}
        y_right_points = {}
        x_up_points = {}
        x_down_points = {}


        #count number of pixel instances in line
        for pixel in left:
            if pixel.y in y_left_points:
                y_left_points[pixel.y] += 1
            else:
                y_left_points[pixel.y] = 0

        for pixel in right:
            if pixel.y in y_right_points:
                y_right_points[pixel.y] += 1
            else:
                y_right_points[pixel.y] = 0

        for pixel in up:
            if pixel.x in x_up_points:
                x_up_points[pixel.x] += 1
            else:
                x_up_points[pixel.x] = 0

        for pixel in down:
            if pixel.x in x_down_points:
                x_down_points[pixel.x] += 1
            else:
                x_down_points[pixel.x] = 0


        #choose distance label - choosing most frequent
        y_left_distance = self.choose_label_distance(y_left_points)
        y_right_distance = self.choose_label_distance(y_right_points)
        x_up_distance = self.choose_label_distance(x_up_points)
        x_down_distance = self.choose_label_distance(x_down_points)

        #removing labels:
        to_remove = []
        for [key,value] in y_left_points.items():
            if value == y_left_distance:
                to_remove.extend([pixel for pixel in left if pixel.y == key and pixel.rgb() == black])

        for [key,value] in y_right_points.items():
            if value == y_right_distance:
                to_remove.extend([pixel for pixel in right if pixel.y == key and pixel.rgb() == black])

        for [key,value] in x_up_points.items():
            if value == x_up_distance:
                to_remove.extend([pixel for pixel in up if pixel.x == key and pixel.rgb() == black])

        for [key,value] in x_down_points.items():
            if value == x_down_distance:
                to_remove.extend([pixel for pixel in down if pixel.x == key and pixel.rgb() == black])


        #removing in all pixels
        print "Removing label pixels..."
        for pixel in to_remove:
            self.pixels.remove(pixel)

    def choose_label_distance(self,labels_dict):

        l = []
        for [key,value] in labels_dict.items():
            if value > self.label_line_len_min:
                l.append(value)
        if len(l) > 0:
            #most frequent
            most_frequent = max(set(l), key=l.count)
            return most_frequent
        return None

    def group_pixels(self):
        print "Grouping pixels..."
        new_pixels = []

        #removing single colors (not very common)
        colors = [key for key in self.colors if self.colors[key] > self.colors_thr]

        for color in colors:
            print "\tFinding group of pixels for color " + str(color)
            for x in xrange(self.img_shape[1]):
                #find all pixels in this color in this column
                column = [pixel for pixel in self.pixels if pixel.x == x and tuple([pixel.r,pixel.g,pixel.b]) == color]
                if(len(column) > 0):

                    y_values = [pixel.y for pixel in column]
                    y_values_grouped = group_values(y_values)
                    for group in y_values_grouped:
                        if len(group) > 0:
                            y_mean = np.mean(group)
                            y_middle = min(group, key=lambda y: abs(y-y_mean)) #choose closest to min

                            pix = next(pixel for pixel in column if pixel.x == x and pixel.y == y_middle)
                            new_pixels.append(pix)
        self.pixels = new_pixels

    def detect_lines(self):
        print "Detecting lines..."
        self.lines = []
        i = 0
        j = 0
        #pixels_original = list(self.pixels) #debug only
        while(len(self.pixels) > 0):

            line = []
            angles = []
            pixel = self.pixels[i]

            while(pixel is not None): #while neighbour found
                line.append(pixel)
                pixel_old = pixel
                pixel = neighbour(pixel,self.pixels,angles,self.neighbours,self.max_dist)

                #calculate angle between pixels
                if pixel is not None:
                    ang = angle(pixel_old,pixel)

                    angles.append(ang)
                    if len(angles) > self.angles_thr:
                        angles.remove(angles[0])

                    #removing pixel between old and new pixel
                    x_borders = [pixel_old.x, pixel.x]
                    y_borders = [min([pixel_old.y,pixel.y]),max([pixel_old.y,pixel.y])]

                    pixels_inside = [item for item in self.pixels if x_borders[0] <= item.x <= x_borders[1] and y_borders[0] <= item.y <= y_borders[1]]

                    for item in pixels_inside:
                        self.pixels.remove(item)

                if pixel_old in self.pixels:
                    self.pixels.remove(pixel_old)

            j += 1

            if len(line) > int(self.line_thr): #if line longer than threshold
                self.lines.append(line)

    def change_axis(self):
        print "Chaning axises..."

        max_y_point = self.y_max

        for i in xrange(len(self.lines)): #iterate over lines
            for j in xrange(len(self.lines[i])): #iterate over line - pixels
                tmp_pix = self.lines[i][j]
                tmp_pix.y = abs(max_y_point-tmp_pix.y)#change y coordinate

    def  scale_pixels(self):
        print "Scaling pixels..."
        x_range = self.labels[1]-self.labels[0]
        y_range = self.labels[3]-self.labels[2]

        #calculated before
        max_x_point = self.x_max
        max_y_point = self.y_max

        scale_x = x_range/float(max_x_point)
        scale_y = y_range/float(max_y_point)

        '''
        if self.x_type == "log":
            pass

        if self.y_type == "log":
            y_min = self.labels[2]
            y_max = self.labels[3]
            y = y_min
            y_scale = []
            #building lin-log scale to convert
            while y <= y_max:
                y_scale.append(y)
                y *= 10

            for i in xrange(len(y_scale)):
                y_scale[i] = [y_scale[i],y_min+i*y_range/float(len(y_scale)-1)]

            print y_scale
        '''

        #scaling
        for i in xrange(len(self.lines)): #iterate over lines
            for j in xrange(len(self.lines[i])): #iterate over line - pixels
                tmp_pix = self.lines[i][j]

                tmp_pix.x = self.labels[0]+scale_x*tmp_pix.x
                tmp_pix.y = self.labels[2]+scale_y*tmp_pix.y

                '''
                if self.y_type == "log":

                    print "punkt:\t" + str(tmp_pix.y)
                    print "zakres w ktory wpada:"
                    range_lin = []
                    for k in xrange(len(y_scale)):
                        if (y_scale[k][1] <= tmp_pix.y and
                            y_scale[k+1][1] >= tmp_pix.y):
                            range_lin = [y_scale[k][1],y_scale[k+1][1]]
                            range_log = [y_scale[k][0],y_scale[k+1][0]]
                    print range_lin
                    print range_log

                    distance = (tmp_pix.y-range_lin[0])/float(range_lin[1]-range_lin[0])
                    print "distance:\t" + str(distance)

                    print "log value:\t " + str(range_log[0]) + " do potegi 1 + " + str(distance)
                    log_value = range_log[0]*pow(range_log[0],distance)/10
                    #log_value = pow(range_log[1],distance)

                    print "log value:\t" + str(log_value)
                    tmp_pix.y = log_value
                '''

                self.lines[i][j] = tmp_pix

    def legend_to_lines(self):

        self.lines.sort(key= lambda s: len(s)) #sorting plots by length of them

        print "Legend to lines..."
        new_legend = []
        for item in self.legend:
            color = item[1]

            for line in self.lines:
                #if line[0].rgb() == color: #if first pixel of line matches color
                if line[0].rgb() == color[::-1]: #if first pixel of line matches color #reserved todo: #!!
                    index = self.lines.index(line)#posititon in lines list
                    new_legend.append([item[0],item[1],index]) #name and index

        self.legend = new_legend


    def write_data_to_file(self):
        #self.lines.sort(key= lambda s: len(s)) #sorting plots by length of them
        print "Writing data file..."
        for [i,pixels] in enumerate(self.lines):
            print "Writing line " + str(i)
            f = open('data' + str(i) + '.dat','w')
            for pixel in pixels:
                #write pixel coordinates
                f.write(str(pixel.x) + "\t" + str(pixel.y) + "\n")
            f.close()


    def create_ps(self):
        print "Creating ps file..."
        legend_string = ""
        addplots_string = ""

        #debug only
        '''
        for item in self.legend:
            print item
        raw_input("stop")
        '''

        if len(self.legend) > 0: #if legend exists
            #adding legend and colors
            for [i,entry] in enumerate(self.legend):
                color = entry[1]
                addplots_string += "\definecolor{color" + str(entry[2]) + "}{RGB}{" + str(color[0]) +"," + str(color[1]) + "," + str(color[2]) + "}\n"#declaring rgb color

            self.legend.sort(key=lambda item: item[2])

            for entry in self.legend:
                legend_string += ("\\addlegendentry{" + entry[0] + "}") #entry[0] - legend string
            for i in range(0,len(self.lines)):
                addplots_string += "\\addplot[color=color" + str(i) + ", mark=none, smooth] file{data" + str(i) + ".dat};\n" #adding plot
        else: #no legend
            for i in range(0,len(self.lines)):
                color = self.lines[i][0].rgb()[::-1]
                addplots_string += "\definecolor{color" + str(i) + "}{RGB}{" + str(color[0]) +"," + str(color[1]) + "," + str(color[2]) + "}\n"#declaring rgb color
                addplots_string += "\\addplot[color=color" + str(i) + ", mark=none, smooth] file{data" + str(i) + ".dat};\n" #adding plot

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
        test_text += legend_string
        test_text += """
            \end{axis}


            \end{tikzpicture}
            \end{document}
            """


        f = open('generate.tex','w')
        f.write(test_text)
        f.close()

        os.system('lualatex generate.tex')
        os.system('pdf2svg generate.pdf generate.svg')
        os.system('rm generate.pdf')
        os.system('mv generate.svg ' + self.path + ".svg")
        os.system('rm data*.dat')
        os.system('rm inside.png')
        if os.path.isfile("./legend_texts.png"):
            os.system('rm legend_texts.png')
        if os.path.isfile("./legend.png"):
            os.system('rm legend.png')
        os.system('rm x_cropped_img.png')
        os.system('rm y_cropped_img.png')
        os.system('rm generate.tex')
        #os.system('rm generate.log') #debug only
        print "Done"

    def draw(self):

        print "Drawing..."
        img = np.ones([self.inside_img.shape[0],self.inside_img.shape[1],3]) * 255


        for pixel in self.pixels:
            img[pixel.y,pixel.x] = [pixel.r,pixel.g,pixel.b]

        cv2.imwrite("wynik.bmp",img)
