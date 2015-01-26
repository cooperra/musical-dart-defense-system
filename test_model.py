import cv2, sys, numpy, os
import pickle
import pyttsx
import time
import pyspotify_login_1
import threading
from webcam_turret import WebcamTurret
glb_flg=0
#Load train libraries
print('Testing')
model=cv2.createEigenFaceRecognizer()
model.load("model_file.p")
names=pickle.load(open("names_var.p","rb"))
print names

#variables
zero_turret = False
selection=2
webcam_device=0 # 0 for default webcam, 1 for usb
threshold_light=3500
threshold_tight=3200
ngbd=8
greetings={'Anuteja': 'Welcome. How about some of your favorite music. ', 'TJ': 'Welcome. How about some of your favorite music.', 'Robbie' :'Welcome. How about some of your favorite music.','Lorinda':'Welcome. How about some of your favorite music. ' , 'default': 'Intruder Alert'}

#predefinedtext
size=4
(im_width, im_height) = (112, 92)
fn_haar = 'haarcascade_face.xml'
fn_dir = 'att_faces'

global most_recent_greetee
most_recent_greetee = None
def init_espeak():
        global engine
        global speech_thread
        global most_recent_greetee
        engine=pyttsx.init()
        class SpeechLoop(threading.Thread):
                def run(self):
                        engine.startLoop()
        speech_thread = SpeechLoop()
        speech_thread.daemon = True
        speech_thread.start()
        def new_timer():
                global most_recent_greetee
                most_recent_greetee = None
                reset_most_recent = threading.Timer(7.0, lambda: new_timer().start())
                reset_most_recent.daemon = True
                return reset_most_recent
        new_timer().start()

def init_turret():
        # This is where one would specify how the camera and turret are positioned relative to each other
        global turret
        turret = WebcamTurret()
        if zero_turret:
                try:
                        turret.zero()
                except KeyboardInterrupt:
                        pass
                turret.aim_center()
        else:
                turret.set_centered()
        # set this to true if we duct tape the camera onto the turret
        #turret.lock_mode = True

def do_talk(text):
        global most_recent_greetee
        global engine
	global glb_flg
        if text == most_recent_greetee:
                # Don't repeat yourself
                return
	if text in greetings.keys():
		engine.say(greetings[text])
		engine.say(text)
		
		#time.sleep(2)
		if glb_flg==0:
			status=pyspotify_login_1.spotify_stub(text.lower())
		else:
			status=-1
		print greetings[text]+text
		if status==0:
			engine=pyttsx.init()
			engine.say("please sign up with spotify for a musical entry")
		else: 
			glb_flg=1

                most_recent_greetee = text
	else:
                if 'default' != most_recent_greetee:
                        engine.say(greetings['default'])
                most_recent_greetee = 'default'

def do_play(name):
	do_talk(name)
	status=pyspotify_login_1.spotify_stub(name.lower())
	if status==0:
		engine=pyttsx.init()
		engine.say("please sign up with spotify for a musical entry")
		engine.runAndWait()

def do_something(i):
	if selection==1:
		print i, names[i]
	elif selection==2:
		do_talk(names[i])
		return 1
	elif selection==3:
		do_play(names[i])
	return 0

def draw_face_box(face, frame, text="", color=(0,255,0)):
        (x, y, w, h) = [v * size for v in face]
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
        #print text
        cv2.putText(frame,'%s' % text,(x-10, y-10), cv2.FONT_HERSHEY_PLAIN,1, color)

def attack_face(face):
        turret.attack_face(face)

def Call_Cam():
        init_espeak()
        engine.say("Calibrating!")
        init_turret()
        engine.say("Ready!")
	haar_cascade = cv2.CascadeClassifier(fn_haar)
	webcam = cv2.VideoCapture(webcam_device)

	#Part 2: Use fisherRecognizer on camera stream
	previous=0;
	count_alm=0
	while True:
    		(rval, frame) = webcam.read()
    		frame=cv2.flip(frame,1,0)
    		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    		mini = cv2.resize(gray, (gray.shape[1] / size, gray.shape[0] / size))
    		faces = haar_cascade.detectMultiScale(mini)
		current_prediction={}
		count=0
    		for i in range(len(faces)):
        		face_i = faces[i]
        		(x, y, w, h) = [v * size for v in face_i]
        		face = gray[y:y + h, x:x + w]
        		face_resize = cv2.resize(face, (im_width, im_height))
        		prediction = model.predict(face_resize)
			#print prediction
			#If threshold conditions are met and atleast one prediction is possible
        		if prediction[0]!=-1 and prediction[1]<threshold_light:
				current_prediction[prediction[0]]=(prediction[1],frame,(x,y,w,h))
		
		if bool(current_prediction) and previous in current_prediction.keys():
			print 'previous detected'			
			continue
		elif bool(current_prediction)==False and len(faces)>0:
			print 'no conf light'
			count_alm=count_alm+1
                        for face in faces:
                                draw_face_box(face, frame, "Unknown", (0, 0, 255))
                        if count_alm>ngbd:
                                count_alm=ngbd
                                print("count_alm>ngbd!")
			if count_alm==ngbd:
				count_alm=0
				do_something(0)
                                # Shooting things here
				def face_area(face):
                                        return face[2] * face[3]
                                def expand_face(face):
                                        # I don't know why I need to do this
                                        return [v * size for v in face]
                                attack_face(max(map(expand_face,faces), key=face_area)) # attack the biggest target
                                print(expand_face(face))
		elif bool(current_prediction):
			for i in current_prediction.keys():
				(conf,frame,(x,y,w,h))=current_prediction[i]
				cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            			#print prediction
      	    			cv2.putText(frame,'%s' % (names[i]),(x-10, y-10), cv2.FONT_HERSHEY_PLAIN,1,(0, 255, 0))
				#code to do something when a candidate hit is detected
				#what to do when you detect faces
				if conf<threshold_tight:
					success=do_something(i)
					print 'detect'
					count=1
					count_alm=0
					previous= i
			if count==0:
				print 'no conf tight'
				count_alm=count_alm+1
				if count_alm==ngbd:
					count_alm=0				
					do_something(0)
						

        		#print prediction
    		cv2.imshow('OpenCV', frame)
    		key = cv2.waitKey(10)
    		if key == 27:
        		break

if __name__=="__main__":
	glb_flg=0
	Call_Cam()
