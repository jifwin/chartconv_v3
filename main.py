__author__ = 'grzegorz'

from image import Image
import sys

if __name__ == "__main__": #main function
    if(len(sys.argv) < 2): #todo 1
        print "Filename not specified!"
        sys.exit(1)


    path = sys.argv[1]

    im = Image(path)
    im.import_image()
    im.axis_detection()
    im.ocr_labels() #todo: labels function in class
    im.crop_image()
    im.find_points()
    im.remove_lines()
    im.remove_labels_lines()
    im.change_axis()
    im.scale_points()
    im.round_points()

    im.split_plots()

    im.write_data_to_file()
    im.create_ps()

    sys.exit(0)