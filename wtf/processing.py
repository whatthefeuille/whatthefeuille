import os
import numpy as np

from skimage.io import imread
from skimage.io import imsave
from skimage.feature import hog
from skimage import color
from sklearn.metrics.pairwise import pairwise_distances

from PIL import Image

from wtf import logger


EXIF_TAG_ORIENTATION = 0x0112

WARPED_IMG_SIZE = (500, 500)


def save_normalized(fileobj, filename):
    image = Image.open(fileobj)

    # Resize
    image.thumbnail(WARPED_IMG_SIZE, Image.ANTIALIAS)

    # Flip / rotate image based on EXIF orientation flag
    exif = image._getexif()
    orientation = None if exif is None else exif.get(
        EXIF_TAG_ORIENTATION, None)

    if orientation == 2:
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation == 3:
        image = image.transpose(Image.ROTATE_180)
    elif orientation == 4:
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
    elif orientation == 5:
        image = image.transpose(
            Image.FLIP_TOP_BOTTOM).transpose(Image.ROTATE_270)
    elif orientation == 6:
        image = image.transpose(Image.ROTATE_270)
    elif orientation == 7:
        image = image.transpose(
            Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
    elif orientation == 8:
        image = image.transpose(Image.ROTATE_90)

    # Save image
    image.save(filename)


def get_img_size(img_path):
    """Return the (height, width) size tuple of the image file"""
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
    # Load the data
    original = imread(raw_img_path)
    base = np.array(base)
    top = np.array(top)

    # Check the expected size of the resulting file
    warped_img_size = np.array(warped_img_size)
    warped_h, warped_w = warped_img_size

    bigger = np.max(original.shape[:2]) * 1.5
    embedded = np.zeros(shape=(bigger, bigger, original.shape[2]),
                        dtype=original.dtype)

    original_center = (base + top) / 2
    embedded_center = np.array(embedded.shape[:2]) / 2
    offset = embedded_center - original_center

    x_slice = slice(offset[0], offset[0] + original.shape[0])
    y_slice = slice(offset[1], offset[1] + original.shape[1])

    try:
        embedded[x_slice, y_slice, :] = original
    except ValueError:
        logger.warning("Invalid base and top positions on image %s: %r, %r",
                       raw_img_path, base, top)
        return raw_img_path, tuple(base), tuple(top)

    # Check the original base and top coordinate positions
    embedded_base = base + offset
    embedded_top = top + offset

    warped_base = ((0.9, 0.5) * warped_img_size).astype(np.int)
    warped_top = ((0.05, 0.5) * warped_img_size).astype(np.int)
    logger.debug("About to warp from {base, top = %r, %r} to "
                 "{warped_base, warped_top = %r, %r}",
                 base, top, warped_base, warped_top)

    orig_vector = embedded_top - embedded_base
    orig_norm = np.linalg.norm(orig_vector)

    warped_vector = warped_top - warped_base
    warped_norm = np.linalg.norm(warped_vector)

    if orig_norm == 0:
        logger.warning("Cannot warp image using a null original vector")
        # Cannot warp with this data, return null operation insted
        return raw_img_path, tuple(base), tuple(top)

    scale = warped_norm / orig_norm

    rotation = (np.arctan2(warped_vector[0], warped_vector[1])
                - np.arctan2(orig_vector[0], orig_vector[1]))

    rotation_degrees = rotation * -180. / np.pi

    pil_rotated = Image.fromarray(embedded).rotate(rotation_degrees)

    scaled_size = (int(embedded.shape[0] * scale),
                   int(embedded.shape[1] * scale))
    logger.info("Warping from %r to %r using rot=%0.2f scale=%0.2f",
                orig_vector, warped_vector, rotation_degrees, scale)

    pil_scaled = pil_rotated.resize(scaled_size, Image.ANTIALIAS)

    scaled = np.array(pil_scaled)
    scaled_center = np.array(scaled.shape[:2]) / 2

    x_slice = slice(scaled_center[0] - warped_h / 2,
                    scaled_center[0] + warped_h / 2)
    y_slice = slice(scaled_center[1] - warped_w / 2,
                    scaled_center[1] + warped_w / 2)
    warped = scaled[x_slice, y_slice, :]

    # Save the result back on the harddrive
    warped_path = get_warped_img_path(raw_img_path)
    imsave(warped_path, warped)
    return warped_path, tuple(warped_base), tuple(warped_top)


def compute_features(file_path):
    """Compute a vector of histogram-style features"""
    logger.debug("Extracting features for %s", file_path)
    image = color.rgb2gray(imread(file_path))
    fd = hog(image, orientations=8, pixels_per_cell=(16, 16),
             cells_per_block=(1, 1))
    return fd


def compute_features_collection(snaps, pic_dir, cache=None):
    """Compute the features for every element in the paths"""
    if cache is None:
        cache = {}

    snaps_with_features = []
    features_list = []
    for snap in snaps:
        snap_id = snap.filename
        features = cache.get(snap_id)
        if features is not None:
            snaps_with_features.append(snap)
            features_list.append(features)
            continue

        # Compute the features
        if not snap.get('warped', False):
            logger.warning('Cannot compute feature for unwarped %s',
                           snap_id)
            continue

        warped_file_path = os.path.join(pic_dir, snap.warped_filename)
        new_features = compute_features(warped_file_path)
        cache[snap_id] = new_features
        snaps_with_features.append(snap)
        features_list.append(new_features)

    return snaps_with_features, features_list


def suggest_snaps(query_snap, other_snaps, pic_dir, cache=None,
                  criterion='euclidean_distance'):
    """Order snaps by similarity with the reference query"""
    if cache is None:
        cache = {}

    if not query_snap.warped:
        raise ValueError()
    query_features = cache.get(query_snap.filename)
    if query_features is None:
        query_warped_file_path = os.path.join(
            pic_dir, query_snap.warped_filename)
        query_features = compute_features(query_warped_file_path)
        cache[query_snap.filename] = query_features

    snaps, features = compute_features_collection(
        other_snaps, pic_dir, cache=cache)
    snaps = np.array(snaps)

    if criterion == 'euclidean_distance':
        scores = pairwise_distances([query_features], features).ravel()
        minimize = True
    else:
        raise NotImplementedError('criterion: ' + criterion)

    if minimize:
        ordering = np.argsort(scores)
    else:
        ordering = np.argsort(scores)[::-1]
    return snaps[ordering], scores[ordering]
