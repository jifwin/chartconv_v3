import sys
import argparse
from image import Image

#parsing arguments
parser = argparse.ArgumentParser()
parser.add_argument("--filename",required=True)
parser.add_argument("--plotarea",default=50) #percentage of plot area compared to whole image
parser.add_argument("--shift_x",default=15) #pixels to ignore between axis labels and main contour in x axis
parser.add_argument("--shift_y",default=8) #pixels to ignore between axis labels and main contour in y axis
parser.add_argument("--shift_zero",default=20) #pixels to ignore around zero point

parser.add_argument("--legend_tol",default=0.99) #legend - diagonals and lines tolerance
parser.add_argument("--extra_shift_legend",default=1) #legend - extra pixels to ignore
parser.add_argument("--legend_area",default=0.3) #legend area compared to whole image
parser.add_argument("--min_legend_line",default=0.2) #legend - minimum length of line
parser.add_argument("--max_legend_line",default=0.9) #legend - diagonals and lines tolerance
parser.add_argument("--lines_merge",default=0.1) # legend - distance between lines to merge
parser.add_argument("--border_thr",default=10) #n-times larger than other, then remove border line

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
#image.draw() #debug only
image.group_pixels()
image.detect_lines()
image.change_axis()
image.scale_pixels()
image.legend_to_lines()
image.write_data_to_file()
image.create_ps()

sys.exit(0)

