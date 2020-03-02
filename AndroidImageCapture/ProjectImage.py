import cv2 
import os
import screeninfo 

"""
Requires installation of the screeninfo module
https://pypi.org/project/screeninfo/
"""

#Sets directory to current folder script is in
os.chdir(os.path.dirname(__file__))
print("Saving files to:")
print(os.getcwd())

#Get monitor resolution sizes
screens = screeninfo.get_monitors()
main_res = screens[0].width, screens[0].height
proj_res = screens[1].width, screens[1].height

#Reads image from subfolder called GrayCodeImages
i = 1
image_path = os.getcwd() + "\GrayCodeImages"
img = cv2.imread(image_path + "\GrayCode" + str(i) + ".jpg")

#Create window and move window to the second display
cv2.namedWindow("My Window", cv2.WINDOW_NORMAL);
cv2.moveWindow("My Window", main_res[0], main_res[1]);
cv2.setWindowProperty("My Window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

#Show image on window
cv2.imshow("My Window" , img)
cv2.waitKey(0)
cv2.destroyWindow("My Window")