import cv2 
import os
import screeninfo
import urllib.request

"""
Script should project the gray code images sequentially with a delay of 500ms, and an android phone with
IP Cam installed and running should take the pictures and save them into a subfolder where the script is in

Requires installation of the screeninfo module
https://pypi.org/project/screeninfo/

TO DO:
    Error checking - Monitor numbers, existence of graycode folder
    Error checking - Valid url (or if phone is connected to the online website)
    Secondary screen showing video feed from phone (Not so important)
    Option for user to input initial scan name instead of just "Calibration"
    Let user specify IP address instead!
"""

#Sets url for IP Webcam interface
url = "http://192.168.0.60:8080"
url_vid = url + "/video"
#cap = cv2.VideoCapture(url_vid)

#Sets directory to current folder script is in
os.chdir(os.path.dirname(__file__))
print("Saving files to:")
print(os.getcwd())

#Get monitor resolution sizes
screens = screeninfo.get_monitors()
main_res = screens[0].width, screens[0].height
proj_res = screens[1].width, screens[1].height

#Create window and move window to the second display
cv2.namedWindow("My Window", cv2.WINDOW_NORMAL);
cv2.moveWindow("My Window", main_res[0], main_res[1]);
cv2.setWindowProperty("My Window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

#Constants to set
exp_time_ms = 200 #Exposure time in miliseconds
scan_name = "Calibration" #Name of subfolder to which images are saved
scan_set = 1 #Number of scan rounds

"""
Reads the image from GrayCodeImages folder, takes a picture and saves picture in the directories made
"""

while(True):
    #Create subdirectories
    if not os.path.exists(scan_name):
        os.makedirs(scan_name)
        
    if not os.path.exists(scan_name + "\\" + str(scan_set)):
        os.makedirs(scan_name + "\\" + str(scan_set))
        
    #Sequentially projects image and takes a picture
    i = 1
    while (i < len(os.listdir(os.getcwd() + "\GrayCodeImages")) + 1):
        image_path = os.getcwd() + "\GrayCodeImages"
        img = cv2.imread(image_path + "\GrayCode" + str(i) + ".jpg")
        cv2.imshow("My Window" , img)
        cv2.waitKey(exp_time_ms)
        if i < 10:
            picture = urllib.request.urlretrieve(url + "/photo.jpg", 
                                            os.getcwd() + "\\" + scan_name + 
                                             "\\" + str(scan_set) + "\\Image0" + str(i) + ".jpg")
        else:
            picture = urllib.request.urlretrieve(url + "/photo.jpg", 
                                                os.getcwd() + "\\" + scan_name + 
                                                 "\\" + str(scan_set) + "\\Image" + str(i) + ".jpg")
        i += 1
    
    #User input to decide on choice of action
    key = input("[c] to scan another set, [n] to scan another object, any other button to quit: ")
    if key == "c":
        i = 1
        scan_set += 1
    elif key == "n":
        i = 1
        scan_set = 1
        scan_name = input("\nPlease enter name of new object to scan: ")
        while os.path.exists(scan_name):
            scan_name = input("\nPrevious folder already exists!\nPlease enter name of new object to scan: ")
    else:
        cv2.destroyWindow("My Window")
        break
    




 

    