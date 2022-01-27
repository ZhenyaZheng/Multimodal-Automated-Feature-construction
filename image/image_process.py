import numpy as np
from scipy.stats import describe
from skimage.color import rgb2gray
from skimage.feature import hog
from skimage import exposure
from skimage.feature import canny
def Dig_feature(image = None):
    ans = None
    if image is None:
        return ans
    return np.round(np.array([np.mean(image), np.var(image), np.mean((image - np.mean(image)) ** 4) / pow(np.var(image), 2), np.mean((image - np.mean(image)) ** 3), np.median(image)]),2)
def Dig_all_feature(image = None):
    ans = None
    if image is None:
        return ans
    image_rgb = image.reshape((image.shape[0]*image.shape[1]), 3).T
    description = describe(image_rgb, axis=1)
    image_gs = rgb2gray(image)
    image_gs_feature = Dig_feature(image_gs)
    fd_image, image_hog = hog(image_gs, orientations=8, pixels_per_cell=(8, 8),
                    cells_per_block=(3, 3), visualize=True)
    image_hogs = exposure.rescale_intensity(image_hog, in_range=(0, 0.04))
    image_hogs_feature = Dig_feature(image_hogs)
    image_edges = canny(image_gs, sigma=3)
    image_edges_nums = np.array([np.sum(np.array(image_edges).flatten() == True) ,np.sum(np.array(image_edges).flatten() == False)])
    ans = np.append(np.array([np.round(description.mean, 2),np.round(description.variance, 2),
                     np.round(description.kurtosis, 2),np.round(description.skewness, 2),
                     np.round(np.median(image_rgb, axis=1), 2)]).flatten(),np.array([image_gs_feature,
                     image_hogs_feature]).flatten())
    return np.append(ans,image_edges_nums)