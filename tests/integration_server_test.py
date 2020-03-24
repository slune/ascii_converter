#!/usr/bin/env python

import time
import unittest
import requests

URL = "http://127.0.0.1:8080"


class TestAsciiServer(unittest.TestCase):

    def test_image_upload(self):
        """ Tests uploading an image and testing presence of meta and ascii.
        """

        url = f"{URL}/upload?size=100"
        fl_name = f"./tests/images/github.png"
        with open(fl_name, 'rb') as fd:
            files = {'file': fd}
            response = requests.post(url, files=files)

        img_id = response.json()["image_id"]
        self.assertEqual(response.status_code, 200)

        url = f"{URL}/image/{img_id}/meta"

        for idx in range(5):
            response = requests.get(url)
            self.assertEqual(response.status_code, 200)
            state = response.json()["state"]
            if state == "ready":
                break
            time.sleep(1)
        else:
            raise Exception

        url = f"{URL}/image/{img_id}/ascii"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
