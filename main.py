import cv2 as cv
from window_capture import Window_Capture
from vision import Vision







# basically taking a bunch of screenshots and processing each screenshot with CV


#Window_Capture.list_window_names()
#exit()


capture = Window_Capture("Roblox")
roblox_Vision = Vision('test_screenshots/target.jpg')



while True:
    screenshot = capture.get_screenshot()
    output_img = roblox_Vision.apply_hsv_filter(screenshot)

    # object detection
    #rectangles = roblox_Vision.findPromptPos(screenshot, 0.5)

    #draw results onto the original image
    #output_img = roblox_Vision.create_rectangles(screenshot, rectangles)

    cv.imshow('Detection', output_img)


    #cv.imshow('Computer Vision', screenshot)



    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print('Done')

