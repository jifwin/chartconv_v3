__author__ = 'grzegorz'

import numpy as np
import sys
import math

data = np.linspace(0.005,12345,1000)
print data

data_min_log = math.log(min(data),10)
data_max_log = math.log(max(data),10)
print data_min_log,data_max_log


y_min = math.floor(data_min_log)
y_max = math.ceil(data_max_log)


print y_min
print y_max


log_scale = []
y = y_min
while y <= y_max:
    log_scale.append(pow(10,y))
    y += 1

print "got log scale"

print log_scale



for point in data:

    smaller = [item for item in log_scale if item <= point]
    larger = [item for item in log_scale if item >= point]

    smaller = min(smaller,key=lambda item: abs(item-point))
    larger = min(larger,key=lambda item: abs(item-point))

    if smaller != larger:
        percent = (point-smaller)/float(larger-smaller)
    else:
        percent = 0

    smaller_log = math.log(smaller,10)
    larger_log = math.log(larger,10)

    distance = smaller_log+percent

    log_value = pow(10,distance)
    print point,smaller,larger,distance, log_value
