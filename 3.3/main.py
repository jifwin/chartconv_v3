import sys
from image import Image
import argparse

#parsing arguments
parser = argparse.ArgumentParser()
parser.add_argument("--filename")
parser.add_argument("--parameter1",default=5) #todo:
arguments = parser.parse_args()

image = Image(arguments.filename)
image.load()
image.detect_axis()
image.ocr_labels()
image.analyze_legend()
image.crop()
image.find_pixels()
image.remove_border_lines()
image.remove_labels_lines()
image.draw()
image.group_pixels()
image.detect_lines()
image.change_axis()
image.scale_pixels()
image.write_data_to_file()
image.create_ps()




