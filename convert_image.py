#!/usr/bin/env pythono

import sys
import time
import logging
import numpy as np
from PIL import Image
from main import write_meta

chars = np.asarray(list('$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/|()1{}[]?-_+~<>i!lI;:,"^`\'. '))


logger: logging.Logger = logging.getLogger("Ascii_server")
logger.setLevel(logging.DEBUG)
fmt = logging.Formatter(fmt="%(asctime)s %(name)-12s %(levelname)-8s %(message)s")
log_hdlr = logging.StreamHandler()
log_hdlr.setFormatter(fmt)
logger.addHandler(log_hdlr)


def convert_image(fl_original: str, fl_ascii: str, fl_meta: str, width: int = 100):
    '''
    Converts an image to ascii and writes status to meta file.
    Source: https://gist.github.com/cdiener/10567484
    With some minor tweaks and bug fixes
    '''

    logger.info(f"Opening image: {fl_original}")
    ts = time.time()
    with Image.open(fl_original) as img:
        (old_width, old_height) = img.size
        aspect_ratio = float(old_height)/float(old_width)
        new_height = int(aspect_ratio * width)
        img_size = (width, new_height)
        logger.debug(f"New size: {img_size}")

        # Here we resize the image and add up the rgb values of the image to get the overall intensity
        # values for each pixel.
        try:
            # for RGB
            img_array = np.sum(np.asarray(img.resize(img_size)), axis=2)
            # Here we scale the smallest intensity value to zero
            # We divide the intensity values by it maximum so all intensities are now between 0 and 1. We invert
            # the intensity scale by subtracting it from one, so that the whitest pixels map to the space character
            # and the darkest pixels to the @ character. The now scaled intensities are now raised to the power of the
            img_array -= img_array.min()
        except np.AxisError:
            # for BW
            img_array = np.asarray(img.resize(img_size))
            img_array_new = img_array - img_array.min()
            img_array = img_array_new

        # intensity correction factor GCF which alters the intensity histogram of the image and, thus, gives some
        # some freedom to counteract very dark or light images. A CGF of 1 gives the original pixel intensities.
        # Finally the scaled intensities are multiplied with the biggest index of the character array chars (n-1)
        # and, later, truncated to int which basically maps every intensity value of the original image to an index
        # of the ascii character array.
        img_array = (1.0 - img_array/img_array.max())**1*(chars.size-1)

    with open(fl_ascii, "w") as fd:
        # Here we assemble and print our ascii art.
        # The image is truncated to int and the entire image matrix is passed
        # as an index to the character array.
        # This is possible because numpy actually allows indices to be vectors or matrices
        # where the output will have the same dimensions of the matrix "filtered" by the indexed vector. For example, if
        #
        #
        #     v = array(['a', 'b', 'c', 'd']) and M = array( [[0, 1],     it follows that v[M] = [['a', 'b'],
        #                                                     [2, 3]] )                           ['c', 'd']]
        #
        # In the inner generator we combine the characters of each row (r) of
        # the now ascii-mapped image to a single string
        # and in the outer join we combine all of the row characters by gluing
        # them with together with newline characters.
        # All of that is printed and done :)
        fd.write("\n".join(("".join(r) for r in chars[img_array.astype(int)])))

    metadata = {
        "image_type": img.format,
        "image_size": (old_width, old_height),
        "convert_time": time.time() - ts,
        "state": "ready",
    }

    write_meta(fl_meta, metadata)


def main(fl_original, fl_ascii, fl_meta, width=100):

    try:
        convert_image(fl_original, fl_ascii, fl_meta, width=width)
    except Exception as err:

        metadata = {
            "state": "error",
            "error": str(err)
        }

        write_meta(fl_meta, metadata)
        raise err


if __name__ == "__main__":

    fl_original = sys.argv[1]
    fl_ascii = sys.argv[2]
    fl_meta = sys.argv[3]
    width = int(sys.argv[4])

    main(fl_original, fl_ascii, fl_meta, width=100)
