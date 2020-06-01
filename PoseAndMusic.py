#!/usr/bin/env python
#-*- cording: utf-8 -*-
from mutagen.mp3 import MP3 as mp3

import pygame.mixer
import time
import cv2
import sys

g_width = 320;
g_height = 240;

haikei_img = cv2.imread("haikei.jpg");

MatchCount = 0;

diffFolder = ''
diffEdgeFolder = ''
poseFlowFilePath = ''
MusicFilePath = ''
timeStart = 0
timeEnd = 0
spanTime = 0

args = sys.argv

print(len(sys.argv))

if len(args) < 5:
 exit()

diffFolder = args[1];
diffEdgeFolder = args[2]
poseFlowFilePath = args[3]
MusicFilePath = args[4]

# VideoCapture オブジェクトを取得します
g_capture = cv2.VideoCapture(0)

print(g_capture.set(cv2.CAP_PROP_FRAME_WIDTH, g_width))
print(g_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, g_height)) 

out_img = cv2.imread("white.jpg")

global firstPoseFlg
firstPoseFlg = True;

def Play():

    global g_capture
    global g_width
    global g_height

    global diffFolder
    global diffEdgeFolder
    global poseFlowFilePath
    global MusicFilePath
    
    global MatchCount
    
    timeStart = 0.0
    timeEnd = 0.0
    spanTime = 0.0

    prevPose = ''
    with open(poseFlowFilePath) as f:
        lines = f.readlines()
        for index in range(len(lines)):
            vals = lines[index].split(',');
            poseName = vals[0]
            timeSpan = int(vals[1])
            
            while(True):
                ret, frame = g_capture.read()
                #cv2.imshow('frame', frame)
                
                str1 = cv2.waitKey(1)
                
                currentTime = time.time()
                if timeStart == 0:
                    timeStart = time.time()
                    timeEnd = time.time()
                else:
                    timeEnd = time.time()
                    
                timeDiff = timeEnd - timeStart
                
                if(timeDiff >= timeSpan):
                    Saiten(poseName)    
                    timeStart = currentTime
                    break
                    
                DisplayCurrentPose(poseName)
                    
            prevPose = poseName;

    f.close()
    
    str2 = "ポーズが一致した回数: (" + str(MatchCount) + " / " + str(len(lines)) + ")"
    print(str2)
    
    g_capture.release()
    cv2.destroyAllWindows()

def Saiten(poseName):
    global diffFolder
    global g_capture
    global haikei_img
    global MatchCount
    
    poseFileName = diffFolder + "\\" + poseName + ".jpg"
    pose_img = cv2.imread(poseFileName);
    
    ret, frame = g_capture.read()
    ret_img = Diff(haikei_img, frame)
    #cv2.imshow('ret1', ret_img)
    cv2.waitKey(1)
    
    sameRate1 = calcOverlapRate(ret_img, pose_img)
    
    str2 = "一致率:" + str(sameRate1) + "%";
    print(str2)
    
    if sameRate1 >= 45.0:
        MatchCount = MatchCount + 1

    return 0

def DisplayCurrentPose(poseName):
    global g_capture
    global g_width
    global g_height
    
    global diffFolder
    global diffEdgeFolder
    global poseFlowFilePath
    global MusicFilePath
    
    global out_img

    ret, frame = g_capture.read()
    #cv2.imshow('frame', frame);
    
    poseFileName = diffFolder + "\\" + poseName + ".jpg"
    poseEdgeFileName = diffEdgeFolder + "\\" + poseName + "_canny.jpg" 
    
    
    pose_img = cv2.imread(poseFileName);
    pose_canny_img = cv2.imread(poseEdgeFileName)
    
    SetBorderToVideo(frame, pose_canny_img, out_img);
    cv2.imshow('overlapImg', out_img)
    
def Diff(img1, img2):
    
    global g_width
    global g_height


    for x in range(0, g_width) :
         for y in range(0, g_height) :
            if img1[y, x, 0] >= img2[y, x, 0]:
                out_img[y, x, 0] = abs(img1[y, x, 0] - img2[y, x, 0]);
            else:
                out_img[y, x, 0] = abs(img2[y, x, 0] - img1[y, x, 0]);

            if img1[y, x, 1] >= img2[y, x, 1]:
                out_img[y, x, 1] = abs(img1[y, x, 1] - img2[y, x, 1]);
            else:
                out_img[y, x, 1] = abs(img2[y, x, 1] - img1[y, x, 1]);

            if img1[y, x, 2] >= img2[y, x, 2]:
                out_img[y, x, 2] = abs(img1[y, x, 2] - img2[y, x, 2]);
            else:
                out_img[y, x, 2] = abs(img2[y, x, 2] - img1[y, x, 2]);

            absSum = int(out_img[y, x, 0]) + int(out_img[y, x, 1]) + int(out_img[y, x, 2])
            if absSum >= 120:
                    out_img[y, x, 0] = 255
                    out_img[y, x, 1] = 255
                    out_img[y, x, 2] = 255
            else:
                    out_img[y, x, 0] = 0
                    out_img[y, x, 1] = 0
                    out_img[y, x, 2] = 0
                    
    return out_img

def SetBorderToVideo(frame, mask, out_img):

    global g_width
    global g_height

    for x in range(0, g_width) :
         for y in range(0, g_height) :
            if mask[y, x][0] == 255:
                    out_img[y, x, 0] = 0;
                    out_img[y, x, 1] = 0;
                    out_img[y, x, 2] = 255;
            else:
                    out_img[y, x] = frame[y, x]
                    
    return out_img

def calcOverlapRate(img1, img2):

    allWhitePixelCount = 0;
    sameCount = 0;
    resultRate = 0;
    
    for x in range(0, g_width) :
         for y in range(0, g_height) :
             if ( (    img1[y, x, 0] == 255 and
                     img1[y, x, 1] == 255 and
                     img1[y, x, 2] == 255) or
                 (    img2[y, x, 0] == 255 and
                     img2[y, x, 1] == 255 and
                     img2[y, x, 2] == 255) ) :
                allWhitePixelCount = allWhitePixelCount + 1
                
                if img1[y, x, 0] == img2[y, x, 0] and img1[y, x, 1] == img2[y, x, 1] and img1[y, x, 2] == img2[y, x, 2]:
                    sameCount = sameCount + 1; 
    
    
    resultRate = (sameCount / allWhitePixelCount) * 100.0
    return resultRate

def main(): 
    fileName = MusicFilePath
    # mixerモジュールの初期化
    pygame.mixer.init()
    # 音楽ファイルの読み込み
    pygame.mixer.music.load(fileName)
    # 音源の長さ取得
    mp3_length = mp3(fileName).info.length;

    # 音楽再生、および再生回数の設定(-1はループ再生)
    pygame.mixer.music.play(1)

    Play()

    # 再生の終了
    pygame.mixer.music.stop()

    return 0
   

    
        
main()
