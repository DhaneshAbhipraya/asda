from os import path
from PIL import Image
import numpy as np

imfrom, imto = input("Image path: ").split('->')

use_palette = bool(input("Use palette? (y/n) ").lower() == 'y')

imtopal = path.join(path.split(imto)[0], '.'.join(path.basename(imto).split('.')[:-1])+'_pal.'+path.basename(imto).split('.')[-1])

img = Image.open(imfrom).convert('RGB')

# Downscale image if needed
if img.width*img.height > 0xffffffff:
    img = img.resize((img.width//2, img.height//2))
# img = img.resize((min(img.size[0], 0xffff), min(img.size[1], 0xffff)))

width, height = img.size

# Convert image to numpy array
img_data = np.array(img)

# Encode the header
data = b"ASD" + bytes([1])  # Asset type 1 for image
pdata = b"ASD" + bytes([2])  # Asset type 2 for palette
data += bytes([0])
data += width.to_bytes(2, 'little')  # Width (2 bytes)
data += height.to_bytes(2, 'little')  # Height (2 bytes)

def split_list(lst, n):
    return [lst[i:i+n] for i in range(0, len(lst), n)]

pdata += split_list(img.getpalette(), 3)
to_be_exhausted = img_data.reshape(-1, img_data.shape[-1]).flatten()

data += to_be_exhausted.tobytes()

# Write the data to the output file
with open(imto, 'wb') as f, open(imtopal, 'wb') as p:
    f.write(data)
    p.write(pdata)