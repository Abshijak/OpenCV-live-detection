import cv2 as cv
import numpy as np
from hsvfilter import HsvFilter

class Vision:

    # constants
    TRACKBAR_WINDOW = "Trackbars"

    # properties
    prompt_img = None
    prompt_w = 0
    prompt_h = 0
    method = None


    def __init__(self, prompt_img_path, method=cv.TM_CCOEFF_NORMED):
        self.prompt_img = cv.imread(prompt_img_path)

        # save dimensions for prompt

        self.prompt_w = self.prompt_img.shape[1]
        self.prompt_h = self.prompt_img.shape[0]

        self.method = method


    def findPromptPos(self, main_img, threshold=0.56, max_results=10):


        result = cv.matchTemplate(main_img, self.prompt_img, self.method)




        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))

        # if we found no results, return now
        if not locations:
            return np.array([], dtype=np.int32).reshape(0,4)

        rectangles = []
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]),self.prompt_w, self.prompt_h]
            # Add every box to the list twice in order to retain single (non-overlapping) boxes
            rectangles.append(rect)
            rectangles.append(rect)

        #eps = relative difference between sides of the rectangles to merge into groups
        #prevents overlapping of rectangles
        rectangles, weights = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)

        if len(rectangles) > max_results:
            print('Too many results, raise the threshold')
            rectangles = rectangles[:max_results]

        return rectangles


    def get_click_points(self, rectangles):

        points = []

        # iterate over all rectangles
        for (x,y,w,h) in rectangles:

            # determine the center position of rectangles
            center_x = x+int(w/2)
            center_y = y+int(h/2)



            # save points
            points.append((center_x,center_y))

        return points

    def create_rectangles(self, main_img, rectangles):
        line_color = (0,255,0)
        line_type = cv.LINE_4

        for (x,y,w,h) in rectangles:
            top_left = (x,y)
            bottom_right = (x+w,y+h)

            cv.rectangle(main_img, top_left, bottom_right, line_color, lineType=line_type)

        return main_img

    def create_markers(self, main_img, points):

        marker_color = (255,0,255)
        marker_type = cv.MARKER_CROSS

        for (center_x, center_y) in points:
            cv.drawMarker(main_img, (center_x,center_y), marker_color, marker_type)

        return main_img

    def init_control_gui(self):
        cv.namedWindow(self.TRACKBAR_WINDOW, cv.WINDOW_NORMAL)
        cv.resizeWindow(self.TRACKBAR_WINDOW, 350, 700)

        # required callback
        # runs every time trackbar is modified
        def nothing(position):
            pass

        # create trackbars for bracketing.
        # OpenCV scale for HSV is H: 0-179, S: 0-255, V: 0-255
        cv.createTrackbar('HMin', self.TRACKBAR_WINDOW, 0, 179, nothing)
        cv.createTrackbar('SMin', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('VMin', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('HMax', self.TRACKBAR_WINDOW, 0, 179, nothing)
        cv.createTrackbar('SMax', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('VMax', self.TRACKBAR_WINDOW, 0, 255, nothing)
        # Set default value for Max HSV trackbars
        cv.setTrackbarPos('HMax', self.TRACKBAR_WINDOW, 179)
        cv.setTrackbarPos('SMax', self.TRACKBAR_WINDOW, 255)
        cv.setTrackbarPos('VMax', self.TRACKBAR_WINDOW, 255)

        # trackbars for increasing/decreasing saturation and value
        cv.createTrackbar('SAdd', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('SSub', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('VAdd', self.TRACKBAR_WINDOW, 0, 255, nothing)
        cv.createTrackbar('VSub', self.TRACKBAR_WINDOW, 0, 255, nothing)

    # returns each value on trackbar as an object
    def get_hsv_filter_from_controls(self):
        hsv_filter = HsvFilter()
        trackbars = ['HMin', 'SMin', 'VMin', 'HMax', 'SMax', 'VMax', 'SAdd', 'SSub', 'VAdd', 'VSub']

        for trackbar in trackbars:
            value = cv.getTrackbarPos(trackbar, self.TRACKBAR_WINDOW)
            if value == -1:
                raise Exception(f"Error retrieving position for trackbar '{trackbar}'")
            setattr(hsv_filter, trackbar.lower(), value)

        return hsv_filter

    def apply_hsv_filter(self, original_img, hsv_filter=None):
        # convert image to hsv
        hsv = cv.cvtColor(original_img, cv.COLOR_BGR2HSV)

        # if there is no given filter, default to values from control
        if not hsv_filter:
            hsv_filter = self.get_hsv_filter_from_controls()

        # add/subtract saturation and value
        h, s, v = cv.split(hsv)
        s = self.shift_channel(s, hsv_filter.sAdd)
        s = self.shift_channel(s, -hsv_filter.sSub)
        v = self.shift_channel(v, hsv_filter.vAdd)
        v = self.shift_channel(v, -hsv_filter.vSub)
        hsv = cv.merge([h,s,v])

        # set min and max HSV values to display
        lower = np.array([hsv_filter.hMin, hsv_filter.sMin, hsv_filter.vMin])
        upper = np.array([hsv_filter.hMax,hsv_filter.sMax,hsv_filter.vMax])

        # apply thresholds
        # creating a mask that converts pixels within threshold to 1
        mask = cv.inRange(hsv,lower,upper)

        # creates a 'filter' that darkens any values outside our mask
        result = cv.bitwise_and(hsv,hsv,mask=mask)

        # convert back to BGR for imshow()
        img = cv.cvtColor(result,cv.COLOR_HSV2BGR)
        return img

    # apply adjustments to an HSV channel
    # https://stackoverflow.com/questions/49697363/shifting-hsv-pixel-values-in-python-using-numpy
    def shift_channel(self, c, amount):
        if amount > 0:
            lim = 255 - amount
            c[c >= lim] = 255
            c[c < lim] += amount
        elif amount < 0:
            amount = -amount
            lim = amount
            c[c <= lim] = 0
            c[c > lim] -= amount
        return c
