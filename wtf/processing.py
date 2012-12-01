import os
import numpy as np

from skimage import transform as tf
from skimage.io import imread
from skimage.io import imsave


WARPED_IMG_SIZE = (500, 500)


def get_img_size(img_path):
    """Return the (width, height) size tuple of the image file"""
    return imread(img_path).shape[:2]


def get_original_path(warped_img):
    """Find the expected file location of an image from the warped"""
    img_folder = os.path.dirname(warped_img)
    base_name = os.path.basename(warped_img)
    img_id, img_ext = os.path.splitext(base_name)
    img_name = img_id[:-len("_warped")] + img_ext
    return os.path.join(img_folder, img_name)


def get_warped_img_path(raw_img_path):
    """Find the expected file location of a warped image from the source"""
    img_folder = os.path.dirname(raw_img_path)
    raw_base_name = os.path.basename(raw_img_path)
    img_id, img_ext = os.path.splitext(raw_base_name)

    warped_img_name = img_id + "_warped" + img_ext
    return os.path.join(img_folder, warped_img_name)


def warp_img(raw_img_path, base, top, warped_img_size=WARPED_IMG_SIZE):
    """Rotate and rescale to normalize the position of base and top points

    Return the file system path of the transformed image and the transformed
    base and top positions in the new image.

    """
    # Check the expected size of the resulting file
    warped_img_size = np.array(warped_img_size)
    warped_w, warped_h = warped_img_size

    # Check the original base and top coordinate positions
    base = np.array(base)
    top = np.array(top)

    # Load the source image from the disk
    img = imread(raw_img_path)

    # Include the original picture in a larger ones to be able to perform the
    # warp operation without losing data around the edges
    img_max = np.max(img.shape[:2])
    twice = img_max * 2
    img_square = np.zeros(shape=(twice, twice, img.shape[2]), dtype=img.dtype)
    img_center = (top + base) / 2
    offset = np.array(img_square.shape[:2]) / 2 - img_center
    base += offset
    top += offset

    x_slice = slice(offset[0], offset[0] + img.shape[0])
    y_slice = slice(offset[1], offset[1] + img.shape[1])

    img_square[x_slice, y_slice, :] = img

    # Find the geometric transformation to rotate / rescale the image to have
    # the base under the top vertically aligned and horizontally centered
    warped_base = ((0.5, 0.8) * warped_img_size).astype(np.int)
    warped_top = ((0.5, 0.1) * warped_img_size).astype(np.int)
    src = np.array([warped_base, warped_top])
    dst = np.array([base, top])

    # Perform the transformation
    tform = tf.estimate_transform('similarity', src, dst)
    warped = tf.warp(img_square, tform)[:warped_w, :warped_h, :]

    # Save the result back on the harddrive
    warped_path = get_warped_img_path(raw_img_path)
    imsave(warped_path, warped)
    return warped_path, tuple(warped_base), tuple(warped_top)
