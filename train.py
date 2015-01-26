#facerec.py
import cv2, sys, numpy, os
import pickle
size = 4
fn_haar = 'haarcascade_face.xml'
fn_dir = 'att_faces'
#Part 1: Create fisherRecognizer
print('Training...')
(images, lables, names, id) = ([], [], {}, 0)
for (subdirs, dirs, files) in os.walk(fn_dir):
    for subdir in dirs:
        names[id] = subdir
        subjectpath = os.path.join(fn_dir, subdir)
        for filename in os.listdir(subjectpath):
            path = subjectpath + '/' + filename
            lable = id
            images.append(cv2.imread(path, 0))
            lables.append(int(lable))
        id += 1
(im_width, im_height) = (112, 92)
(images, lables) = [numpy.array(lis) for lis in [images, lables]]
#model = cv2.createFisherFaceRecognizer()
model=cv2.createEigenFaceRecognizer()
model.train(images, lables)
model.save("model_file.p")
print names
pickle.dump(names, open("names_var.p","wb"))

