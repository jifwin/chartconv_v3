import sys
from image import Image


image = Image(sys.argv[1])
image.load()
image.detect_axis()
image.ocr_labels()
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




