#!/usr/bin/python3

from PIL import Image

img = Image.open('images/test.jpeg');
img.show();
print("original image:", img.size)
cr = img.crop((100,100,300,250))
cr.show()
print("crop image:", cr.size)
