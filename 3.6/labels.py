__author__ = 'grzegorz'
import cv2
from pytesser import *
import numpy as np


def crop(gray,x_axis,y_axis,arguments):

    extra_shift_x = int(arguments.shift_x)
    extra_shift_y = int(arguments.shift_y)

    extra_zero_shift = int(arguments.shift_zero)

    x_cropped_img = gray[y_axis+extra_shift_x:,x_axis-extra_zero_shift:]
    y_cropped_img = gray[:y_axis+extra_zero_shift,:x_axis-extra_shift_y]

    increase = 5 #parameter, multiply image size to increase accuracy

    x_cropped_img = cv2.resize(x_cropped_img, (0,0), fx=increase, fy=increase)
    y_cropped_img = cv2.resize(y_cropped_img, (0,0), fx=increase, fy=increase)

    cv2.imwrite('x_cropped_img.png',x_cropped_img)
    cv2.imwrite('y_cropped_img.png',y_cropped_img)

    return [x_cropped_img,y_cropped_img]

def ocr(): #input cropped img

    x_labels_str = image_file_to_string('x_cropped_img.png')
    y_labels_str = image_file_to_string('y_cropped_img.png')

    #split labels by spaces and new lines
    x_labels = x_labels_str.split(" ")
    y_labels = y_labels_str.split("\n")

    #remove empty labels
    x_labels = [label for label in x_labels if len(label) > 0]
    y_labels = [label for label in y_labels if len(label) > 0]

    #replace O-letter with 0-digit
    x_labels = [label.replace("O","0") for label in x_labels]
    x_labels = [label.replace("o","0") for label in x_labels]

    #change new line and space to empty
    x_labels = [label.replace("\n","") for label in x_labels]
    x_labels = [label.replace(" ","") for label in x_labels]


    y_labels = [label.replace("O","0") for label in y_labels]
    y_labels = [label.replace("o","0") for label in y_labels]
    y_labels = [label.replace("\n","") for label in y_labels]
    y_labels = [label.replace(" ","") for label in y_labels]

    #log scale check - if  more than 90% labels contain "e+" or "e-"
    #count for x
    count_x = 0
    for label in x_labels:
        if "e+" in label or "e-" in label:
            count_x += 1

    if count_x/float(len(x_labels)) > 0.9:
        print "X LOG"
        x_type = "log"
    else:
        x_type = "lin"

    #count for y
    count_y = 0
    for label in y_labels:
        if "e+" in label or "e-" in label:
            count_y += 1

    if count_y/float(len(y_labels)) > 0.9:
        print "Y LOG"
        y_type = "log"
    else:
        y_type = "lin"

    x = [] #final x labels
    y = [] #final y labels

    for item in x_labels:
        #remove incorrect chars
        if not item.isdigit():
            if x_type == "lin":
                item=''.join(i for [index,i] in enumerate(item) if (i.isdigit() or i == '.' or i == ',' or (i == '-' and index==0))) #remove everything but digit, and special chars
        try:
            if(item == "0-."):
                x.append(float(0.0))
            else:
                x.append(float(item))
        except ValueError:
            print "Unrecognized label: " + str(item) #for debug only

    for item in y_labels:
        #remove incorrect chars
        if not item.isdigit():
            if y_type == "lin":
                item=''.join(i for [index,i] in enumerate(item) if (i.isdigit() or i == '.' or i == ',' or (i == '-' and index==0))) #usun wszystko oprocz cyfr i ,.
            elif y_type == "log":
                if "e+" in item:
                    parts = item.split("e+")
                elif "e-" in item:
                    parts = item.split("e-")

        try:
            if(item == "0-."):
                y.append(float(0.0))
            else:
                y.append(float(item))
        except ValueError:
            print "Unrecognized label: " + str(item) #for debug only

    return [x, y, x_type, y_type]

