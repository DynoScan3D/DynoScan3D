import cv2 
import urllib.request
import os

os.chdir(os.path.dirname(__file__))
print("Saving files to:\n")
print(os.getcwd())

url = "http://192.168.0.60:8080"
url_vid = url + "/video"
cap = cv2.VideoCapture(url_vid)

i = 1;
while(True):
    ret, frame = cap.read()
    frame = cv2.resize(frame, (960, 540))
    if frame is not None:
        cv2.imshow('frame',frame)
    q = cv2.waitKey(1)
    
    if q == ord("c"):
        #Capture stuff
        picture = urllib.request.urlretrieve(url + "/photo.jpg", "Image" + str(i) + ".jpg")
        i += 1
    elif q == ord("q"):
        break
    
cv2.destroyAllWindows()