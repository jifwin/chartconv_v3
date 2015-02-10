import sys
import argparse
from image import Image

#parsing arguments
parser = argparse.ArgumentParser()
parser.add_argument("--filename")
parser.add_argument("--angles",default=10) #number of angles to calculate mean
parser.add_argument("--line_thr",default=10) #minimum number of pixels per line to be treated as line
parser.add_argument("--colors_thr",default=10) #minimum number of color pixels to be grouped
parser.add_argument("--border_len",default=5) #number of border pixels to search
parser.add_argument("--labels_lines_len",default=50) #number of pixels labels lines (ticks) to search
parser.add_argument("--label_line_len_min",default=5) #minimal length of label line (tick)
parser.add_argument("--neighbours",default=5) #numbers of closest neighbours to search - closest_thr
parser.add_argument("--max_dist",default=70) #max distance between neighbour pixels - maximum_distance

arguments = parser.parse_args()

image = Image(arguments.filename,arguments)
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
image.legend_to_lines()
image.write_data_to_file()
image.create_ps()

sys.exit(0)

