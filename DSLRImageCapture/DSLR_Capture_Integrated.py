from sh import gphoto2 as gp
import signal, os, subprocess
import time
import cv2
import screeninfo
import serial

"""
Script should project the gray code images sequentially and a DSLR connected
to the PC/raspberry pi via USB cable should take an image for each projected 
pattern.
These gray code images should be stored in a subfolder to the parent directory
with the folder name GrayCodeImages and named "GrayCodei.jpg" where i is the 
image number counting from 1.
Requires installation of the screeninfo module
https://pypi.org/project/screeninfo/
Requires gphoto2 command line interface, which does not run in windows
http://www.gphoto.org/
Requires installation of the cv2 module
Future improvements:
    Error checking - Monitor numbers, existence of graycode folder
    Implement changing settings from script instead of manually changing from
    camera 
        Limited by the read-only nature of some settings when accessed remotely
    Camera confirmation - If multiple devices are connected
    Addition of date and time stamp to folder names
TAKE NOTE: Linux uses forward slashes '/'
Operational notes:
    The projector, connected as a second screen is taken TO THE RIGHT of the 
    primary screen. This is important for the projected images to show up
    Camera will only be detected when it is on, and past the initial screen.
    If projected images are showing up on primary monitor (which it should not)
    try tweaking the values in the cv2.moveWindow
"""
    
def killgphoto2Process():
    """
    This function kills the current gphoto2 process that is automatically
    started when the camera is plugged in. This existing process prevents
    capture of images
    
    Function taken from:
    https://www.youtube.com/watch?v=1eAYxnSU2aw
    """
    p = subprocess.Popen(['ps', '-A'], stdout = subprocess.PIPE)
    out, err = p.communicate()
    
    # Finds line that has process
    for line in out.splitlines():
        if b'gvfsd-gphoto2' in line:
            pid = int(line.split(None, 1) [0])
            os.kill(pid, signal.SIGKILL)
            print('Process Killed')
            

"""
Commands - To be run using the gp(COMMAND) line
The clear command has a folder structure in the second argument, which 
differs for different cameras. This file directory is where pictures are saved
and can be found by querying (in the terminal):
    gphoto2 --list-folders
    gphoto2 --list-files
"""
clearCommand = ["--folder", "/store_00010001/DCIM/100D5000", "-R", "--delete-all-files"]
triggerCommand = ["--trigger-capture"]
captureCommand = ["--capture-image"]
downloadCommand = ["--get-all-files"]


"""
Settings - Seems to change sometimes and sometimes it does not???
Similarlyl run using the gp(COMMAND) line
List of read-only settings that must be changed from camera:
    Focal length
    Focus mode
Settings are usually in steps. E.g. ISO speed goes from 200, 300, 500 etc.
These values can be found by querying (in the terminal):
    gphoto2 --get-config CONFIGNAME
"""
isoautoCommand = ["--set-config", "isoauto=1"] # 0 for on, 1 for off
isoCommand = ["--set-config", "iso=3200"]
autofocusCommand = ["--set-config", "autofocus=0"] # 0 for off, 1 for on
focallengthCommand = ["--set-config", "focallength=30"] 

def captureImages():
    """
    Single-shot image capture and download
    Use of captureCommand instead of triggerCommand eliminates need for pausing
    but prevents finer adjustments to settings
    
    See gphoto2 manual for more information
    """
    gp(captureCommand)
    tic = time.monotonic() * 1000
    print("Downloading:")
    gp(downloadCommand)
    gp(clearCommand)
    toc = time.monotonic() * 1000
    print("Downloaded in %f miliseconds" %(toc-tic))

def renameFiles():
    for count, filename in enumerate(os.listdir()):
        dst = "Image" + str(count+1).zfill(2) + ".jpg"
        os.rename(filename, dst)

home_folder = os.getcwd()
os.chdir(home_folder)
print("Saving files to:")
print(home_folder)
scan_name = input("Please enter name of new object to scan: ")
scan_set = 1
exp_time_ms = 200 #Image time in miliseconds

#Get monitor resolution sizes
screens = screeninfo.get_monitors()
main_res = screens[0].width, screens[0].height
proj_res = screens[1].width, screens[1].height

#Create window and move window to the second display
cv2.namedWindow("My Window", cv2.WINDOW_NORMAL);
cv2.moveWindow("My Window", main_res[0], 0);
cv2.setWindowProperty("My Window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

killgphoto2Process()
gp(clearCommand)

#Set up serial port for arduino
arduino = serial.Serial('COM1', 115200, timeout=.1)

#Number of angles per full revolution
while True:
    while True:
        try:
            angles = int(input("Please enter number of angles per full rev: "))
        except ValueError:
            print("Sorry, please enter integer.")
            continue
        else:
            break
    if (angles > 50) or (angles < 2):
        print("Please enter integer that is greater than 1 and less than 50")
    else:
        break

arduino.write(str(angles))

while(True): 
    #Create subdirectories
    if not os.path.exists(scan_name):
        os.makedirs(scan_name)
        
    if not os.path.exists(scan_name + "/" + str(scan_set)):
        os.makedirs(scan_name + "/" + str(scan_set))
		
    #Send data to arduino. Start rotation
    rotation = input("[r] to start rotation:")
    if rotation == "r":
        arduino.write("1")
        serial.reset_input_buffer() #Clear input buffer    
        while (arduino.in_waiting() < 0): #Wait for data to be received from arduino.
            time.sleep(1)
	
    #Sequentially projects image and takes a picture
    if arduino.read_until() == "s":
        i = 1
        while (i < len(os.listdir(home_folder + "/GrayCodeImages")) + 1):
			#Display images
            image_path = home_folder + "/GrayCodeImages"
            img = cv2.imread(image_path + "/GrayCode" + str(i) + ".jpg")
            cv2.imshow("My Window" , img)
            cv2.waitKey(exp_time_ms)
            
            os.chdir(home_folder + "/" + scan_name + "/" + str(scan_set))
            captureImages()
            i += 1
        renameFiles()
    
    #User input to decide on choice of action
    key = input("[c] to scan another set, [n] to scan another object, any other button to quit: ")
    if key == "c":
        i = 1
        scan_set += 1
        os.chdir(home_folder)
    elif key == "n":
        i = 1
        scan_set = 1
        scan_name = input("\nPlease enter name of new object to scan: ")
        os.chdir(home_folder)
        while os.path.exists(scan_name):
            scan_name = input("\nPrevious folder already exists!\nPlease enter name of new object to scan: ")
    else:
        cv2.destroyWindow("My Window")
        break