from Tkinter import *
from tkMessageBox import showinfo
import pickle	
import os, shutil
import sys
import winsound
import time
import os.path
import cv2
import numpy as np
import serial 


ser = serial.Serial('COM7', 9600)

def capture():
    cam = cv2.VideoCapture(0)

    img_counter = 0

    winsound.PlaySound('audio/5secs.wav', winsound.SND_FILENAME)
    timeout = time.time() + 5

    while True:
        ret, frame = cam.read()
        cv2.imshow("Eye", frame)
        if not ret:
            break
        k = cv2.waitKey(1)

        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        
        elif time.time() > timeout:
            while(os.path.isfile("eyes/{}.png".format(img_counter)) == True):
                img_counter = img_counter + 1
            img_name = "eyes/{}.png".format(img_counter)
            cv2.imwrite(img_name, frame)
            print("written!")
            img_counter += 1
            winsound.PlaySound('audio/beep.wav', winsound.SND_FILENAME)
            break

    cam.release()
    cv2.destroyAllWindows()
    
def compare(match):
    cam = cv2.VideoCapture(0)

    cv2.namedWindow("Eye")

    img_counter = 0

    winsound.PlaySound('audio/5secs.wav', winsound.SND_FILENAME)
    timeout = time.time() + 5

    while True:
        ret, frame = cam.read()
        cv2.imshow("Iris Capture", frame)
        if not ret:
            break
        k = cv2.waitKey(1)

        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        
        elif time.time() > timeout:
            ID = sift(frame)
            if int(match) == int(ID):
                print match
                print ID
                names = pickle.load( open("names.p", "rb" ) )
                ages = pickle.load( open("ages.p", "rb" ) )
                winsound.PlaySound('audio/beep.wav', winsound.SND_FILENAME)
                ser.write("G")
                i = 1
                while(1):
                    ser.write("G")
                    if(i==1):
                        sList=['Authentication Successful-\nName: {}\n', 'Age: {} years']
                        valueList=[names[ID],ages[ID]]
                        lines = [s.format(value) for s,value in zip(sList,valueList)]
                        msg = ''.join(lines)
                        showinfo(title='Success', message = "%s" % msg)
                        i = i + 1
            else:
                i = 1
                while(1):
                    ser.write("R")
                    if(i==1):
                        showinfo(title='Failed', message='Authentication Failure. Please adjust lighting conditions.')
                        i = i + 1
            break

    cam.release()
    cv2.destroyAllWindows()

def sift(frame):
    list = os.listdir('eyes/') # dir is your directory path
    number_of_files = len(list)

    ideal = 0
    ideal_score = np.inf

    for i in range(0,number_of_files): 
        img1 = frame
        img2 = cv2.imread('eyes/'+str(i)+'.png',0) # trainImage
         
        # Initiate ORB detector
        orb = cv2.ORB_create()
         
        # find the keypoints and descriptors with ORB
        kp1, des1 = orb.detectAndCompute(img1,None)
        kp2, des2 = orb.detectAndCompute(img2,None)
        # create BFMatcher object
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
         
        # Match descriptors.
        matches = bf.match(des1,des2)
         
        # Sort them in the order of their distance.
        matches = sorted(matches, key = lambda x:x.distance)
        # Draw first 10 matches.
        n = 0

        corr = []
        for n in range (0,10):
            corr.append(matches[n].distance)
         
        img3 = cv2.drawMatches(img1,kp1,img2,kp2,matches[:10],None,flags=2)

        average_match_score = np.mean(corr)
        print average_match_score

        if average_match_score < ideal_score:
            ideal = i
            ideal_score = average_match_score
        
    return ideal
    
def reset():
    names = []
    ages = []
    pickle.dump(names, open( "names.p","wb"))
    pickle.dump(ages, open( "ages.p","wb"))

    folder = 'eyes/'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
    
def reply1():
    enroll = Tk()
    enroll.resizable(width=False, height=False)
    enroll.geometry('{}x{}'.format(350,100))
    enroll.title('Enroll')
    Label(enroll, text="Please enroll your fingerprint in the adjacent window\n BEFORE Entering your NAME and AGE in the boxes below:").pack(side=TOP)

    ent1 = Entry(enroll)
    ent1.pack(fill=BOTH, expand = 1)

    ent2 = Entry(enroll)
    ent2.pack(fill=BOTH, expand = 1)
        
    btn3 = Button(enroll, text="ENTER", command=(lambda: reply3(ent1.get(),ent2.get())))
    btn3.pack(fill=BOTH, expand = 1)


def reply2():
    valid = Tk()
    valid.resizable(width=False, height=False)
    valid.geometry('{}x{}'.format(600,200))
    valid.title('Authentication')

    Label(valid, text="Please verify your fingerprint in the adjacent window\n AND THEN\n Enter your name and Unique Fingerprint ID:").pack(side=TOP)
    Label(valid, text="If you do not get a Unique Fingerprint ID, please retry verification.\n Else, you may not be in the database and need to ENROLL first:").pack(side=BOTTOM)

    ent2 = Entry(valid)
    ent2.pack(side=TOP)
    
    btn4 = Button(valid, text="ENTER", command=(lambda: reply4(ent2.get(), ent3.get())))
    btn4.pack(side=BOTTOM)
    
    ent3 = Entry(valid)
    ent3.pack(side=BOTTOM)
    

def reply3(name, age):
    try:
        names = pickle.load( open("names.p", "rb" ) )
        ages = pickle.load( open("ages.p", "rb" ) )
    except IOError:
        names = []
        ages = []
    names.append(name)
    ages.append(age)
    
    pickle.dump(names, open( "names.p","wb"))
    pickle.dump(ages, open( "ages.p","wb"))
    ser.write("B")
    showinfo(title='Finger Enrolled', message='Hello %s! Please proceed to Iris Enrollment\nby clicking OK' % name)
    capture()
    showinfo(title='Iris Enrolled', message='New User Enrolled: %s' % name)
    
def reply4(name, numb):
    names = pickle.load( open("names.p", "rb" ) )
    try:
        if names[int(numb)] == name:
            sList=['Authentication Successful-\nName: {}\nPress OK to continue to iris verification.']
            valueList=[names[int(numb)]]
            lines = [s.format(value) for s,value in zip(sList,valueList)]
            msg = ''.join(lines)
            showinfo(title='Fingerprint ID', message="%s" % msg)
            compare(int(numb))
        else:
            i = 1
            while(1):
                ser.write("R")
                if(i==1):
                    showinfo(title='Fingerprint ID', message='Rejected')
                    i = i + 1


    except IndexError:
        i = 1
        while(1):
            ser.write("R")
            if(i ==1):
                showinfo(title='Reply', message='Rejected')
                i = i + 1


        
root = Tk()
root.resizable(width=False, height=False)
root.geometry('{}x{}'.format(800,400))
root.title('Authentication System')

btn1 = Button(root, text="Enroll", fg="blue", command=(lambda: reply1()))
btn2 = Button(root, text="Authenticate", fg="red", command=(lambda: reply2()))
btn1.pack(fill=BOTH, expand = 1)
btn2.pack(fill=BOTH, expand = 1)

reset_button = Button(root, text="Reset DB", command=(lambda: reset()))
reset_button.pack(fill=X)
    
root.mainloop()
root.quit()
