import numpy as np
import cv2
from matplotlib import pyplot as plt
import math
#cv2.ocl.setUseOpenCL(False)
img1 = cv2.imread('box.png',0)          # queryImage
img2 = cv2.imread('box_in_scene.png',0) # trainImage

# Initiate SIFT detector
orb = cv2.ORB_create()

# find the keypoints and descriptors with SIFT
kp1, des1 = orb.detectAndCompute(img1,None)
kp2, des2 = orb.detectAndCompute(img2,None)

print len(des1)
print len(des1[0])
print des1
#print size(des2)
print len(des2)
print len(des2[0])
print des2

# create BFMatcher object
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# Match descriptors.
matches = bf.match(des1,des2)

print des1[0]
print des1[0][0]

database = []
for i in des1:
    for j in i:
        database.append(j)

for i in des2:
    for j in i:
        database.append(j)

def generateDistribution(database):
    histogram = [0 ] * 256
    for i in database:
        histogram[i] += 1
    for i in xrange(len(histogram)):
        histogram[i] = histogram[i] / float(len(database))
    return histogram

prob = generateDistribution(database)


def computeEntropy(des, prob):
    "compute entropy"
    entropy = 0
    for i in des:
        entropy += -1 * prob[i] * math.log(prob[i],2)
    return entropy


des1entropy = []
for d in des1:
    des1entropy.append(computeEntropy(d, prob))

des2entropy  = []
for d in des2:
    des2entropy.append(computeEntropy(d, prob))

print des1entropy
print " ------ "
print des2entropy


# rank the descriptors based on entropy
sorted_entropy1_indices = [i[0] for i in sorted(enumerate(des1entropy), key=lambda x:x[1])]
sorted_entropy2_indices = [i[0] for i in sorted(enumerate(des2entropy), key=lambda x:x[1])]

def drawEntropyDescriptors(img, kp, entropy_indice):
    row = img.shape[0]
    col = img.shape[1]
    out = np.zeros((row, col, 3), dtype='uint8')
    out[:row, col] = np.dstack([img, img, img])

    for i in xrange(len(entropy_indice)):
        # select the rannked feature
        p = kp[entropy_indice[i]]
        color = 255 * entropy_indice[i] / len(entropy_indice[i])
        cv2.circle(out, (int(p[0]), int(p[1])), 4, (color, 0, 0), 1)
    cv2.imshow('Features with entropy', out)
    cv2.waitKey(0)
    cv2.destroyWindow('Features with entropy')
    return out

drawEntropyDescriptors(img1, kp1, sorted_entropy1_indices)

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
    cv2.waitKey(0)
    cv2.destroyWindow('Matched Features')

    # Also return the image if you'd like a copy
    return out

# Sort them in the order of their distance.
matches = sorted(matches, key = lambda x:x.distance)

# Draw first 10 matches.

img3 = drawMatches(img1,kp1,img2,kp2,matches[:100])

#plt.imshow(img3)

#plt.imshow(img1)
#plt.savefig("xxx.png")
plt.show()
