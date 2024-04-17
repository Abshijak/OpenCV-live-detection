import cv2 as cv
import numpy as np

haystack = cv.imread('test_screenshots/test.jpg', cv.IMREAD_UNCHANGED)
prompt = cv.imread('test_screenshots/target.jpg', cv.IMREAD_UNCHANGED)

result = cv.matchTemplate(haystack, prompt, cv.TM_CCOEFF_NORMED)

# (name of window, image of data)
cv.imshow('Result', result)

# pauses the script until a key is pressed
#cv.waitKey()

#min_val = darkest pixel %, max_val = brightest pixel %
#tldr: get best match position
min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

print('Best match top left position: %s' %str(max_loc))
print('Best match confidence: %s' % max_val)

# checks if any pixel is greater than threshold aka highest likelihood found
threshold = 0.4
if max_val >= threshold:
    print('Found prompt')

    # get dimensions of the prompt image
    prompt_w = prompt.shape[1] #y coordinate
    prompt_h = prompt.shape[0] #x coordinate

    top_left = max_loc
    # we can calculate the bottom right by adding the dimensions to the topleft coordinates
    bottom_right = (top_left[0] + prompt_w, top_left[1] + prompt_h)
    # draws a rectangle around the found object
    cv.rectangle(haystack, top_left, bottom_right,
                 color=(0,255,0),thickness=2,lineType=cv.LINE_4)

    cv.imshow('Result', haystack)
    cv.waitKey()
else:
    print('Not found')