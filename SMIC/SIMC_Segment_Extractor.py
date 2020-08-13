import os
import cv2
import dlib
import numpy
from keras.utils import np_utils
from keras import backend as K
import matplotlib.pyplot as plt

K.set_image_dim_ordering('th')

# DLib Face Detection path setup
predictor_path = "shape_predictor_68_face_landmarks.dat"
predictor = dlib.shape_predictor(predictor_path)
detector = dlib.get_frontal_face_detector()


class TooManyFaces(Exception):
    pass


class NoFaces(Exception):
    pass


def get_landmark(img):
    rects = detector(img, 1)
    if len(rects) > 1:
        pass
    if len(rects) == 0:
        pass
    ans = numpy.matrix([[p.x, p.y] for p in predictor(img, rects[0]).parts()])
    return ans


def annotate_landmarks(img, landmarks, font_scale=0.4):
    for idx, point in enumerate(landmarks):
        pos = (point[0, 0], point[0, 1])
        cv2.putText(img, str(idx), pos, fontFace=cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, fontScale=font_scale,
                    color=(0, 0, 255))
        cv2.circle(img, pos, 3, color=(0, 255, 255))
    return img

path='../../SIMC_E_categorical/'
negativepath = path+'Negative/'
positivepath =path+'Positive/'
surprisepath = path+'Surprise/'

segmentName='FullFace'
sizeH=68
sizeV=2
sizeD=141

paths=[negativepath,positivepath,surprisepath]
segment_training_list = []
counting = 0
for typepath in (paths):
    directorylisting = os.listdir(typepath)
    print(typepath)

    for video in directorylisting:
        videopath = typepath + video
        segment_frames = []
        framelisting = os.listdir(videopath)
        if sizeD<len(framelisting):
            val=int((len(framelisting)/2)-(sizeD/2))
            framerange = [x+val for x in range(sizeD)]
        else:
            tempD1=sizeD//len(framelisting)
            tempD2 = sizeD%len(framelisting)
            framerange = []
            for y in range (tempD1):
                framerange.extend([x for x in range(len(framelisting))])
            framerange.extend([y for y in range(tempD2)])
        for frame in framerange:
            imagepath = videopath + "/" + framelisting[frame]
            image = cv2.imread(imagepath)
            landmarks = get_landmark(image)
            segment_frames.append(landmarks)

        segment_frames = numpy.asarray(segment_frames)
        # print(1, segment_frames.shape)
        segment_videoarray = numpy.rollaxis(numpy.rollaxis(segment_frames, 2, 0), 2, 0)
        # print(2, segment_videoarray.shape)
        segment_training_list.append(segment_videoarray)

segment_training_list = numpy.asarray(segment_training_list)
print(3, segment_training_list.shape)
segment_trainingsamples = len(segment_training_list)

segment_traininglabels = numpy.zeros((segment_trainingsamples,), dtype=int)

count=0
for pi in range(len(paths)):
    directorylisting = os.listdir(paths[pi])
    print(pi)
    for video in range(len(directorylisting)):
        segment_traininglabels[count] = pi
        count+=1


segment_traininglabels = np_utils.to_categorical(segment_traininglabels, len(paths))

segment_training_data = [segment_training_list, segment_traininglabels]
(segment_trainingframes, segment_traininglabels) = (segment_training_data[0], segment_training_data[1])
segment_training_set = numpy.zeros((segment_trainingsamples, 1,sizeH, sizeV, sizeD))
for h in range(segment_trainingsamples):
    segment_training_set[h][0][:][:][:] = segment_trainingframes[h, :, :, :]

segment_training_set = segment_training_set.astype('float32')
segment_training_set -= numpy.mean(segment_training_set)
segment_training_set /= numpy.max(segment_training_set)

numpy.save('numpy_training_datasets/{0}_images_{1}x{2}x{3}.npy'.format(segmentName,sizeH, sizeV,sizeD), segment_training_set)
numpy.save('numpy_training_datasets/{0}_labels_{1}x{2}x{3}.npy'.format(segmentName,sizeH, sizeV,sizeD), segment_traininglabels)

"""
----------------------------
segments:
----------------------------


UpperFace
----------------------------
up = min(numpylandmarks[18][1], numpylandmarks[19][1], numpylandmarks[23][1], numpylandmarks[24][1]) - 20
down = max(numpylandmarks[31][1], numpylandmarks[32][1], numpylandmarks[33][1], numpylandmarks[34][1],
          numpylandmarks[35][1]) + 5
left = min(numpylandmarks[17][0], numpylandmarks[18][0], numpylandmarks[36][0])
right = max(numpylandmarks[26][0], numpylandmarks[25][0], numpylandmarks[45][0])


Eyes
----------------------------  
up = min(numpylandmarks[18][1], numpylandmarks[19][1], numpylandmarks[23][1], numpylandmarks[24][1]) - 20
down = max(numpylandmarks[36][1], numpylandmarks[39][1], numpylandmarks[40][1], numpylandmarks[41][1],numpylandmarks[42][1], numpylandmarks[47][1], numpylandmarks[46][1], numpylandmarks[45][1]) +10
left = min(numpylandmarks[17][0], numpylandmarks[18][0], numpylandmarks[36][0])
right = max(numpylandmarks[26][0], numpylandmarks[25][0], numpylandmarks[45][0])        


LeftEye
----------------------------  
up=min(numpylandmarks[17][1],numpylandmarks[18][1],numpylandmarks[19][1],numpylandmarks[20][1],numpylandmarks[21][1])-20
down = max(numpylandmarks[36][1], numpylandmarks[39][1], numpylandmarks[40][1], numpylandmarks[41][1]) +10
left = min(numpylandmarks[17][0], numpylandmarks[18][0], numpylandmarks[36][0])
right = max(numpylandmarks[39][0], numpylandmarks[21][0])+10


RightEye
----------------------------   
up = min(numpylandmarks[22][1], numpylandmarks[23][1], numpylandmarks[24][1], numpylandmarks[25][1],
        numpylandmarks[26][1]) - 20
down = max(numpylandmarks[42][1], numpylandmarks[47][1], numpylandmarks[46][1], numpylandmarks[45][1]) + 10
right = max(numpylandmarks[26][0], numpylandmarks[25][0], numpylandmarks[45][0])
left = min(numpylandmarks[22][0], numpylandmarks[42][0])-10


Nose
----------------------------     
up = numpylandmarks[27][1] - 5
down = max(numpylandmarks[31][1], numpylandmarks[32][1], numpylandmarks[33][1], numpylandmarks[34][1], numpylandmarks[35][1]) + 5
left = numpylandmarks[31][0]
right = numpylandmarks[35][0] 
"""