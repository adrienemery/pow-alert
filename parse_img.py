#! /usr/bin/env python

import os
import cv2
import calibrate
import collections


Params = collections.namedtuple('Params', ['a', 'b', 'c'])  # to store equation of a line
NBR_OF_THRESHOLD = 10
WHITE_THRESHOLD = 0.5 * 255
LIST_OF_THRESHOLDS = ('50', '45', '40', '35', '30', '25', '20', '15', '10', '5', '0')
CYPRESS = "Cypress"
WHISTLER = "Whistler - Blackomb"


def calc_params(point1, point2):  # line's equation Params computation aX + bY + c
    if point2[1] - point1[1] == 0:
        a = 0
        b = -1.0
    elif point2[0] - point1[0] == 0:
        a = -1.0
        b = 0
    else:
        a = (point2[1] - point1[1]) / (point2[0] - point1[0])
        b = -1.0

    c = (-a * point1[0]) - b * point1[1]
    return Params(a, b, c)


def lines_intersection_pt(params1, params2, point1, point2, img, dbg):
    det = params1.a * params2.b - params2.a * params1.b
    if det == 0:
        return False  # lines are parallel
    else:
        x = round(((params2.b * -params1.c - params1.b * -params2.c)/det), 12)  # floating imprecision
        y = round(((params1.a * -params2.c - params2.a * -params1.c)/det), 12)  # floating imprecision
        if min(point1[0], point2[0]) <= x <= max(point1[0], point2[0]) \
                and min(point1[0], point2[0]) <= y <= max(point1[1], point2[1]):
            if dbg:
                cv2.circle(img, (int(x), int(y)), 10, (255, 255, 255), -1)  # intersecting point
            return int(x), int(y)  # lines are intersecting inside the line segment
        else:
            return  # lines are intersecting but outside of the line segment


def read_height(image, resort, debug_option=False):

    if debug_option:
        from matplotlib import pyplot as plt

    if resort == CYPRESS:
        with open(".env", 'r') as env:
            if "TOP_LEFT_OFFSET" not in env.read():  # calibration has not been done, calibration is done once in a lifetime
                calibrate.cypress_img(debug_option)
            # else no need to calibrate > already done

        img = image
        img2 = img.copy()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Otherwise the difference of encoding with cv2 and skimage will cause problems with matchTemplate
        template1 = cv2.imread('templates/50.jpg', 0)
        template1 = cv2.resize(template1, (0, 0), fx=0.5, fy=0.5)  # MacOS grab.app changes resolution x2
        h1, w1 = template1.shape
        h, w = img.shape

        method = eval('cv2.TM_CCOEFF_NORMED')

        res1 = cv2.matchTemplate(img, template1, method)
        min_val1, max_val1, min_loc1, max_loc1 = cv2.minMaxLoc(res1)
        top_left1 = max_loc1
        bottom_right1 = (top_left1[0] + w1, top_left1[1] + h1)

        top_left_offset = eval(str(os.environ.get("TOP_LEFT_OFFSET")))
        top_right_offset = eval(str(os.environ.get("TOP_RIGHT_OFFSET")))
        bottom_left_offset = eval(str(os.environ.get("BOTTOM_LEFT_OFFSET")))
        bottom_right_offset = eval(str(os.environ.get("BOTTOM_RIGHT_OFFSET")))

        # Get 4 corners of ROI
        roi_top_left = tuple(x + y for x, y in zip(top_left1, top_left_offset))
        roi_top_right = tuple(x + y for x, y in zip(top_left1, top_right_offset))
        roi_bottom_right = tuple(x + y for x, y in zip(top_left1, bottom_right_offset))
        roi_bottom_left = tuple(x + y for x, y in zip(top_left1, bottom_left_offset))

        _50_mark_line = int((top_left1[1] + bottom_right1[1]) / 2)  # middle of the template (50cm) (y axis) Used as patient0
        _0_mark_line = roi_bottom_left[1]  # y axis on the ground
        # if we increase Y by thickness_scale, we get to the next threshold (5-10-15..50)

        # Since the template is not perfectly centered we need an offset to align the center of the template and the line
        # with 9 here some kind of visual magic number as an correction offset (sorry)
        thickness_scale = int(abs(_50_mark_line - _0_mark_line) / 10) + 9

        # Get the function of the 2 vertical ROI limits
        roi_left_line = calc_params(roi_top_left, roi_bottom_left)
        roi_right_line = calc_params(roi_top_right, roi_bottom_right)

        if debug_option:  # plots threshold lines
            scale = thickness_scale
            for i in range(NBR_OF_THRESHOLD):
                if i > 4:  # black magic to counter difference of scale due to angle of camera
                    scale -= 1
                if i > 7:
                    scale -= 0.5
                cv2.line(img,
                         (5, int(_50_mark_line + i * scale)),
                         (1020, int(_50_mark_line + i * scale)),
                         (255, 255, 255),
                         5)
            plt.subplot(111), plt.imshow(img, cmap='gray')
            plt.title('Thresholds'), plt.xticks([]), plt.yticks([])
            plt.show()

        # extract points on both side of ROI where thresholds are
        threshold_points_list = list()
        scale = thickness_scale
        for i in range(NBR_OF_THRESHOLD):
            if i > 4:  # black magic to counter the difference of scale due to angle of camera and may be also fish-eye
                scale -= 1
            if i > 7:
                scale -= 0.5

            threshold_points = ((0, int(_50_mark_line + i * scale)), (w-1, int(_50_mark_line + i * scale)))
            threshold_line = calc_params((0, int(_50_mark_line + i * scale)), (w-1, int(_50_mark_line + i * scale)))

            img_dbg = img if debug_option else None
            point_a = lines_intersection_pt(roi_left_line, threshold_line, threshold_points[0], threshold_points[1],
                                            img_dbg, debug_option)
            point_b = lines_intersection_pt(roi_right_line, threshold_line, threshold_points[0], threshold_points[1],
                                            img_dbg, debug_option)

            threshold_points_list.append((point_a, point_b))

        if debug_option:
            plt.subplot(111), plt.imshow(img, cmap='gray')
            plt.title('Thresholds ROI limits'), plt.xticks([]), plt.yticks([])
            plt.show()

        if debug_option:
            img3 = img2.copy()

        # Extract ROI around threshold
        local_roi = list()
        for i in range(NBR_OF_THRESHOLD):
            # the ROI ends halfway between the current threshold and the next. two last ROIs are identical size
            if i < NBR_OF_THRESHOLD - 1:
                thick = abs(int((threshold_points_list[i][0][1] - threshold_points_list[i + 1][0][1]) / 2))
            local_roi.append(img[int(threshold_points_list[i][0][1] - thick):int(threshold_points_list[i][1][1] + thick),
                             threshold_points_list[i][0][0]:threshold_points_list[i][1][0]])
            if debug_option:
                cv2.rectangle(img3, (threshold_points_list[i][0][0], int(threshold_points_list[i][0][1] - thick)),
                              (threshold_points_list[i][1][0], int(threshold_points_list[i][1][1] + thick)), 255, 3)
        if debug_option:
            plt.subplot(111), plt.imshow(img3, cmap='gray')
            plt.title('ROI'), plt.xticks([]), plt.yticks([])
            plt.show()

        # Average value of pixels in the ROI
        avg_pix_roi = [int(roi.mean()) for roi in local_roi[:NBR_OF_THRESHOLD]]

        # Now scale it for snow fall
        for threshold_val, white_val in zip(LIST_OF_THRESHOLDS, avg_pix_roi):
            if white_val > WHITE_THRESHOLD:
                return threshold_val

        return LIST_OF_THRESHOLDS[-1]

