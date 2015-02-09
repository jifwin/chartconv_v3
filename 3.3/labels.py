__author__ = 'grzegorz'
import cv2
from pytesser import *
import numpy as np


def crop(gray,x_axis,y_axis):

    #todo: improve parameters
    extra_shift_x = 15
    extra_shift_y = 10

    extra_zero_shift = 20#shift for cutting near zero

    x_cropped_img = gray[y_axis+extra_shift_x:,x_axis-extra_zero_shift:]
    y_cropped_img = gray[:y_axis+extra_zero_shift,:x_axis-extra_shift_y]

    #todo: parameter increase! change name
    increase = 5 #parameter, multiply image size

    x_cropped_img = cv2.resize(x_cropped_img, (0,0), fx=increase, fy=increase)
    y_cropped_img = cv2.resize(y_cropped_img, (0,0), fx=increase, fy=increase)

    cv2.imwrite('x_cropped_img.png',x_cropped_img)
    cv2.imwrite('y_cropped_img.png',y_cropped_img)

    return [x_cropped_img,y_cropped_img]

def ocr(): #input cropped img

    x_labels_str = image_file_to_string('x_cropped_img.png')
    y_labels_str = image_file_to_string('y_cropped_img.png')

    '''
    print "x_labels_str:\n"
    for (i,item) in enumerate(x_labels_str):
        print item
        print "---"

    print "y_labels_str:\n"
    print y_labels_str
    '''

    #todo: improve: psm for 7 too?
    #todo: don't use files?

    x_labels = x_labels_str.split(" ")
    y_labels = y_labels_str.split("\n")


    #todo: delete "\n", and " "

    while '' in x_labels:
        x_labels.remove('')

    while '' in y_labels:
        y_labels.remove('')

    #replace O-letter with 0-digit
    x_labels = [label.replace("O","0") for label in x_labels]
    x_labels = [label.replace("o","0") for label in x_labels]
    x_labels = [label.replace("\n","") for label in x_labels]
    x_labels = [label.replace(" ","") for label in x_labels]


    y_labels = [label.replace("O","0") for label in y_labels]
    y_labels = [label.replace("o","0") for label in y_labels]
    y_labels = [label.replace("\n","") for label in y_labels]
    y_labels = [label.replace(" ","") for label in y_labels]

    #improve performence?
    #remove extra chars, starting with minus,
    #usunac wszystko oprcz liczb, znakow i kropki (przecinka)
    #do some regular expressions
    #obcinac do ostatniego poprawnego znaku

    #print x_labels #for debug only
    #print y_labels #for debug only


    x = []
    y = []

    for item in x_labels:

        #remove incorrect chars
        if not item.isdigit():
            item=''.join(i for [index,i] in enumerate(item) if (i.isdigit() or i == '.' or i == ',' or (i == '-' and index==0))) #remove everything but digit, and special chars


        try:
            #todo: improve dirty hack
            if(item == "0-."):#
                x.append(float(0.0))
            else:
                x.append(float(item))
        except ValueError:
            #print "Error with label: " + str(item) #for debug only
            pass


    for item in y_labels:
        #remove incorrect chars
        if not item.isdigit():
            item=''.join(i for [index,i] in enumerate(item) if (i.isdigit() or i == '.' or i == ',' or (i == '-' and index==0))) #usun wszystko oprocz cyfr i ,.


        try:
            if(item == "0-."):#todo: improve dirty hack
                y.append(float(0.0))
            else:
                y.append(float(item))
        except ValueError:
            #print "Error with label: " + str(item) #for debug only
            pass

    return [x, y]

