import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--filename")
parser.add_argument("--pixels",default=5)
arguments = parser.parse_args()
print arguments.filename
print arguments.pixels
