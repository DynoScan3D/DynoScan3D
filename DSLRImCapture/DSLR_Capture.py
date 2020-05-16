from time import sleep
from datetime import datetime
from sh import gphoto2 as gp
import signal, os, subprocess
import time
import cv2
import screeninfo

"""

TAKE NOTE THAT Linux uses forward slashes '/'
"""
    
def killgphoto2Process():
    """
    This function kills the current gphoto2 process that is automatically
    started when the camera is plugged in. This existing process prevents
    capture of images
    """
    p = subprocess.Popen(['ps', '-A'], stdout = subprocess.PIPE)
    out, err = p.communicate()
    
    # Finds line that has process
    for line in out.splitlines():
        if b'gvfsd-gphoto2' in line:
            pid = int(line.split(None, 1) [0])
            os.kill(pid, signal.SIGKILL)
            print('Process Killed')
            
shot_date = datetime.now().strftime("%Y-%m-%d")
shot_time = datetime.now().strftime("%Y-%m-%d %H: %M")

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
downloadCommand = ["--get-all-files"]


"""
Settings - Seems to change sometimes and sometimes it does not???

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
    gp(triggerCommand)
    sleep(0.5)
    tic = time.monotonic() * 1000
    print("Downloading:")
    gp(downloadCommand)
    gp(clearCommand)
    toc = time.monotonic() * 1000
    print("Downloaded in %f miliseconds" %(toc-tic))

def renameFiles():
    for count, filename in enumerate(os.getcwd()):
        dst = "Image" + str(count+1).zfill(2) + ".jpg"
        os.rename(filename, dst)

home_folder = os.getcwd()
os.chdir(home_folder)
print("Saving files to:")
print(home_folder)
scan_name = input("Please enter name of new object to scan:") #Name of subfolder to which images are saved
scan_set = 1 #Number of scan rounds
exp_time_ms = 200 #Image time time in miliseconds

killgphoto2Process()
gp(clearCommand)

while(True):
    #Create subdirectories
    if not os.path.exists(scan_name):
        os.makedirs(scan_name)
        
    if not os.path.exists(scan_name + "/" + str(scan_set)):
        os.makedirs(scan_name + "/" + str(scan_set))
        
    #Sequentially projects image and takes a picture
    i = 1
    while (i < len(os.listdir(home_folder + "/GrayCodeImages")) + 1):
#        image_path = home_folder + "/GrayCodeImages"
#        img = cv2.imread(image_path + "/GrayCode" + str(i) + ".jpg")
#        cv2.imshow("My Window" , img)
#        cv2.waitKey(exp_time_ms)
        os.chdir(home_folder + "/" + scan_name + "/" + str(scan_set))
        #captureImages()
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
        #cv2.destroyWindow("My Window")
        break