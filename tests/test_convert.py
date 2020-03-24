#!/usr/bin/env python

import unittest
import sys
import json
sys.path.append("..")

import convert_image


class TestConvert(unittest.TestCase):

    def convert_image(self, image_name, width):
        """ Converts image
        """
        fl_original = f"./tests/images/{image_name}"
        fl_ascii = f"./tests/images/{image_name}.ascii"
        fl_meta = f"./tests/images/{image_name}.meta"

        convert_image.main(fl_original, fl_ascii, fl_meta, width=width)

    def check_meta(self, image_name, speed_min=0, speed_max=1):
        """ Checks meta
        """

        fl_ascii_test = f"./tests/images/test_{image_name}.meta"
        with open(fl_ascii_test) as fd:
            meta_test = json.load(fd)

        fl_ascii = f"./tests/images/{image_name}.meta"
        with open(fl_ascii) as fd:
            meta = json.load(fd)

        self.assertEqual(meta["state"], meta_test["state"])
        self.assertTrue(0 <= meta["convert_time"] <= speed_max)

    def compare_images(self, image_name):
        """ Compares images
        """

        fl_ascii_test = f"./tests/images/test_{image_name}.ascii"
        with open(fl_ascii_test) as fd:
            test_image = fd.read()

        fl_ascii = f"./tests/images/{image_name}.ascii"
        with open(fl_ascii) as fd:
            image = fd.read()

        self.assertEqual(image, test_image)

    def test_BW_convert(self):
        """ Tests BW image
        """

        image_name = "github.png"
        width = 100
        self.convert_image(image_name, width)
        self.compare_images(image_name)
        self.check_meta(image_name, speed_max=1)

    def test_RGB_convert(self):
        """ Tests RGB image
        """

        image_name = "planet.png"
        width = 100
        self.convert_image(image_name, width)
        self.compare_images(image_name)
        self.check_meta(image_name, speed_max=1)

    def test_failure(self):
        """ Tests failure
        """

        image_name = "missing.png"
        width = 100
        try:
            self.convert_image(image_name, width)
        except Exception:
            pass

        fl_ascii = f"./tests/images/{image_name}.meta"
        with open(fl_ascii) as fd:
            meta = json.load(fd)

        self.assertEqual(meta["state"], "error")
        self.assertEqual(meta["error"], "[Errno 2] No such file or directory: './tests/images/missing.png'")


if __name__ == '__main__':
    unittest.main()
