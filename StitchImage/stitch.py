import numpy as np
from PIL import Image


def stitch_images(photos, rectangular_shape: tuple[int, int],
                  bg=(255, 255, 255), sep=3):
    photos.sort()
    x, y = rectangular_shape
    ph_x, ph_y = Image.open(photos[0]).size
    arr_size = (ph_y * y + sep * (y - 1), ph_x * x + sep * (x - 1), 3)
    arr = np.empty(arr_size, dtype=np.uint8)
    arr[:, :] = bg

    for index, (np_x, np_y) in zip(range(len(photos)), np.ndindex(y, x)):
        a = np.array(Image.open(photos[index]))
        arr[np_x * (ph_y + sep): np_x * (ph_y + sep) + ph_y,
            np_y * (ph_x + sep): np_y * (ph_x + sep) + ph_x] = a

    return Image.fromarray(arr)
