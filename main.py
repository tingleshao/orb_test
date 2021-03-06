import numpy as np
import cv2
from matplotlib import pyplot as plt
import math

showed = False

# functions
def drawEntropyDescriptors(img, kp, entropy_indice):
    row = img.shape[0]
    col = img.shape[1]
    out = np.zeros((row, col, 3), dtype='uint8')
    out[:row, :col] = np.dstack([img, img, img])

    for i in xrange(4):
        # select the rannked feature
        p = kp[entropy_indice[i]].pt
        color = 255 * entropy_indice[i] / len(entropy_indice)
        cv2.circle(out, (int(p[0]), int(p[1])), 4, (255, 0, 0), 1)
    cv2.imshow('Features with entropy', out)
    cv2.imwrite('www.png',out)
    cv2.waitKey(0)
    cv2.destroyWindow('Features with entropy')
    return out

def generateDistribution(database):
    histogram = [0 ] * 256
    for i in database:
        histogram[i] += 1
    for i in xrange(len(histogram)):
        histogram[i] = histogram[i] / float(len(database))
    return histogram

def computeEntropy(des, kp, prob, method, gaussian):
    "compute entropy"
    entropy = 0
    #img2 = img2[0:270,240:720]
    if method == 'crop':
        if kp.pt[0] > 270 or kp.pt[1] < 240 or kp.pt[1] > 720:
            return 0
        for i in des:
            entropy += -1 * prob[i] * math.log(prob[i],2)
    elif method == 'gaussian':
        for i in des:
            entropy += -1 * prob[i] * math.log(prob[i],2)
        entropy = entropy * gaussian[kp.pt[1],kp.pt[0]]
    return entropy

def drawMatches(img1, kp1, img2, kp2, matches):
    """
    My own implementation of cv2.drawMatches as OpenCV 2.4.9
    does not have this function available but it's supported in
    OpenCV 3.0.0

    This function takes in two images with their associated
    keypoints, as well as a list of DMatch data structure (matches)
    that contains which keypoints matched in which images.

    An image will be produced where a montage is shown with
    the first image followed by the second image beside it.

    Keypoints are delineated with circles, while lines are connected
    between matching keypoints.

    img1,img2 - Grayscale images
    kp1,kp2 - Detected list of keypoints through any of the OpenCV keypoint
              detection algorithms
    matches - A list of matches of corresponding keypoints through any
              OpenCV keypoint matching algorithm
    """
    # Create a new output image that concatenates the two images together
    # (a.k.a) a montage
    rows1 = img1.shape[0]
    cols1 = img1.shape[1]
    rows2 = img2.shape[0]
    cols2 = img2.shape[1]

    out = np.zeros((max([rows1,rows2]),cols1+cols2,3), dtype='uint8')

    # Place the first image to the left
    out[:rows1,:cols1] = np.dstack([img1, img1, img1])

    # Place the next image to the right of it
    out[:rows2,cols1:] = np.dstack([img2, img2, img2])

    # For each pair of points we have between both images
    # draw circles, then connect a line between them
    for mat in matches:

        # Get the matching keypoints for each of the images
        img1_idx = mat.queryIdx
        img2_idx = mat.trainIdx

        # x - columns
        # y - rows
        (x1,y1) = kp1[img1_idx].pt
        (x2,y2) = kp2[img2_idx].pt

        # Draw a small circle at both co-ordinates
        # radius 4
        # colour blue
        # thickness = 1
        cv2.circle(out, (int(x1),int(y1)), 4, (255, 0, 0), 1)
        cv2.circle(out, (int(x2)+cols1,int(y2)), 4, (255, 0, 0), 1)

        # Draw a line in between the two points
        # thickness = 1
        # colour blue
        cv2.line(out, (int(x1),int(y1)), (int(x2)+cols1,int(y2)), (255, 0, 0), 1)

    # Show the image
    cv2.imshow('Matched Features', out)
    global showed
    if not showed:
        cv2.imwrite('yyy.png', out)
        showed = True
    cv2.waitKey(0)
    cv2.destroyWindow('Matched Features')

    # Also return the image if you'd like a copy
    return out


def makeGaussian(width, height, fwhm=150, center=None):
    """ Make a square gaussian kernel.
    size is the length of a side of the square
    fwhm is full-width-half-maximum, which
    can be thought of as an effective radius.
    """
    x = np.arange(0, width, 1, float)
    yy = np.arange(0, height, 1, float)
    y = yy[:,np.newaxis]
    center = (480, 135)
    if center is None:
        x0 = y0 = size // 2
    else:
        x0 = center[0]
        y0 = center[1]

    return np.exp(-4*np.log(2) * (((x-x0)/(700))**2 + ((y-y0)/(200))**2))


# Show the image
blob = makeGaussian(960, 540)
print blob
print "------"
print blob[135,480]
cv2.imshow('Matched Features', blob)
cv2.imwrite('zzz.png', blob * 255)
#cv2.imwrite('yyy.png', out)
cv2.waitKey(0)
cv2.destroyWindow('Matched Features')

#cv2.ocl.setUseOpenCL(False)
#img1 = cv2.imread('box.png',0)          # queryImage
#img2 = cv2.imread('box_in_scene.png',0) # trainImage
#img2 = cv2.imread('ref.jpg', 0) # train image

prepare_video_frames = False
video_name = 'move.mp4'
#if prepare_video_frames:
    # cap = cv2.VideoCapture(video_name)
    # count = 0
    # while(cap.isOpened()):
    #     count += 1
    #     ret, frame = cap.read()
    #     if count == 27:
    #         count = 0
    #         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #         imwrite('move' + str(count) + '.png', gray)
# TODO: gaussian based feature selection

img2 = cv2.imread('m0.png',0) # trainImage
img2 = cv2.resize(img2,(960, 540), interpolation = cv2.INTER_CUBIC)
# Initiate SIFT detector
orb = cv2.ORB_create()
# find the keypoints and descriptors with SIFT
#kp1, des1 = orb.detectAndCompute(img1,None)
kp2, des2 = orb.detectAndCompute(img2,None)
database = []
for i in des2:
    for j in i:
        database.append(j)
prob = generateDistribution(database)
des2entropy  = []
for i in xrange(len(des2)):
    d = des2[i]
    p = kp2[i]
    des2entropy.append(computeEntropy(d, p, prob, "gaussian", blob))
# rank the descriptors based on entropy
sorted_entropy2_indices = [i[0] for i in sorted(enumerate(des2entropy), key=lambda x:x[1], reverse=True)]
#sorted_entropy2_indices = [82, 72, 15, 66];
drawEntropyDescriptors(img2, kp2, sorted_entropy2_indices)
#kp2_sel = np.array([kp2[sorted_entropy2_indices[0]],kp2[sorted_entropy2_indices[1]],kp2[sorted_entropy2_indices[2]],kp2[sorted_entropy2_indices[3]], kp2[sorted_entropy2_indices[4]],kp2[sorted_entropy2_indices[5]],kp2[sorted_entropy2_indices[6]],kp2[sorted_entropy2_indices[7]]])
kp2_sel = np.array([kp2[sorted_entropy2_indices[0]],kp2[sorted_entropy2_indices[1]],kp2[sorted_entropy2_indices[2]],kp2[sorted_entropy2_indices[3]]])
#des2_sel = np.array([des2[sorted_entropy2_indices[0]],des2[sorted_entropy2_indices[1]],des2[sorted_entropy2_indices[2]],des2[sorted_entropy2_indices[3]],des2[sorted_entropy2_indices[4]],des2[sorted_entropy2_indices[5]],des2[sorted_entropy2_indices[6]],des2[sorted_entropy2_indices[7]]])
des2_sel = np.array([des2[sorted_entropy2_indices[0]],des2[sorted_entropy2_indices[1]],des2[sorted_entropy2_indices[2]],des2[sorted_entropy2_indices[3]]])



# create BFMatcher object
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

#for i in xrange(1,28):
for i in xrange(1):
    #img1 = cv2.imread('m' + str(i) + '.png',0)          # queryImage
    img1 = cv2.imread('ref1' + '.png',0)          # queryImage
    img1 = cv2.resize(img1,(960, 540), interpolation = cv2.INTER_CUBIC)

    kp1, des1 = orb.detectAndCompute(img1,None)
    matches_sel = bf.match(des1,des2_sel)
# only use the best 4 features in entropy to match
# Sort them in the order of their distance.
#matches = sorted(matches, key = lambda x:x.distance)
# Draw first 10 matches.
#print matches_sel
    img3 = drawMatches(img1,kp1,img2,kp2_sel,matches_sel)
    plt.show()
