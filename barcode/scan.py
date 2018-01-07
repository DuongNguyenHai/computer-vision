#!/usr/bin/python3

import zbar
import numpy as np
from PIL import Image

img = Image.open("barcode.jpg").convert('L')
image = np.array(img)

# img2 = np.fromfile("test.jpeg", dtype="uint8")

scanner = zbar.Scanner()
results = scanner.scan(image)
for result in results:
    print(result.type, result.data, result.quality)
