#! /usr/bin/env python3

import os
import cv2
import calibrate


def main(image):

    with open(".env", 'r') as env:
        if "TOP_LEFT_OFFSET" not in env.read():  # calibration has not been done, calibration is done once in a lifetime
            calibrate.main()
        # else no need to calibrate > already done

    img = image
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template1 = cv2.imread('templates/50.jpg', 0)
    template1 = cv2.resize(template1, (0, 0), fx=0.5, fy=0.5)
    h1, w1 = template1.shape

    method = eval('cv2.TM_CCOEFF_NORMED')

    res1 = cv2.matchTemplate(img, template1, method)
    min_val1, max_val1, min_loc1, max_loc1 = cv2.minMaxLoc(res1)
    top_left1 = max_loc1
    bottom_right1 = (top_left1[0] + w1, top_left1[1] + h1)

    top_left_offset = eval(str(os.environ.get("TOP_LEFT_OFFSET")))
    top_right_offset = eval(str(os.environ.get("TOP_RIGHT_OFFSET")))
    bottom_right_offset = eval(str(os.environ.get("BOTTOM_LEFT_OFFSET")))
    bottom_left_offset = eval(str(os.environ.get("BOTTOM_RIGHT_OFFSET")))

    roi_top_left = tuple(x + y for x, y in zip(top_left1, top_left_offset))
    roi_top_right = tuple(x + y for x, y in zip(top_left1, top_right_offset))
    roi_bottom_right = tuple(x + y for x, y in zip(top_left1, bottom_right_offset))
    roi_bottom_left = tuple(x + y for x, y in zip(top_left1, bottom_left_offset))

