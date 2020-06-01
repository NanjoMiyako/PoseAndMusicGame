import cv2
import sys

args = sys.argv

print(len(sys.argv))

if len(args) < 3:
 exit()

diffFolder = args[1];
diffEdgeFolder = args[2]

global g_width;
global g_height;

g_width = 320;
g_height = 240;
# VideoCapture オブジェクトを取得します
capture = cv2.VideoCapture(0)

print(capture.set(cv2.CAP_PROP_FRAME_WIDTH, g_width))
print(capture.set(cv2.CAP_PROP_FRAME_HEIGHT, g_height))

out_img = cv2.imread("white.jpg");
haikei_img = cv2.imread("haikei.jpg");


def DiffOnePixel(ar1, ar2):
    d1 = int(ar1[0]) - int(ar2[0])
    d2 = int(ar1[1]) - int(ar2[1])
    d3 = int(ar1[2]) - int(ar2[2]);
    
    dS = abs(d1) + abs(d2) + abs(d3)
    return dS
    
def GetEdge(img1):

    # エッジ抽出
    canny_img = cv2.Canny(img1, 50, 110)
    
    return canny_img

def Diff(img1, img2):
    global g_width;
    global g_height;

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

        for x in range(0, mask_width) :
             for y in range(0, mask_height) :
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



global FuncCount
FuncCount = 0;

import time

def HaikeiTouroku():
        
        print("10秒後に背景画像を取ります");
        time.sleep(10);
        
        ret, frame = capture.read()
        cv2.imshow('frame',frame)
        
        cv2.imwrite("haikei.jpg", frame);
        
        print("取りました")
        print('\007')
      


def main():

    global timeStart;
    global timeEnd;
    global diffFileName;
    global diffEdgeFileName;

    global haikei_img
    global out_img

    snapShotFlg = False;
    while(True):
            
        ret, frame = capture.read()
        cv2.imshow('frame', frame)
        str1 = cv2.waitKey(1)
        
        if str1 == ord("q"):
            break

        elif str1 == ord("h"):
            HaikeiTouroku()
            
        elif str1 == ord("d"):
            print("保存ファイル名を入力:(拡張子除く)");
            FileName = input();
            diffFileName = diffFolder + "\\" + FileName + ".jpg"
            diffEdgeFileName = diffEdgeFolder + "\\" + FileName + "_canny.jpg"
            print(diffEdgeFileName);
            
            print("15秒後にポーズ用の画像としてDiffを取ります");
            snapShotFlg = True;
            timeStart = time.time();
            #time.sleep(15);
        elif snapShotFlg == True:
            timeEnd = time.time()
            timeDiff = timeEnd - timeStart
            
            if timeDiff >= 15.0 :
                ret, frame = capture.read()
                cv2.imshow('frame', frame)
                
                ret_img = Diff(haikei_img, frame)
                ret_edge_img = GetEdge(ret_img)
                
                cv2.imwrite(diffFileName, ret_img);
                cv2.imwrite(diffEdgeFileName, ret_edge_img);
                
                print("Diff取りました")
                print('\007')
                
                
                snapShotFlg = False

    capture.release()
    cv2.destroyAllWindows()
    
    return 0
    
main()