import os
import shutil
import tempfile
from nose.tools import assert_equals
from nose.tools import assert_true

from wtf.processing import get_warped_img_path
from wtf.processing import warp_img


TEMP_FOLDER = None
IMG_PATH = None


def setup_module():
    global TEMP_FOLDER, IMG_PATH
    if TEMP_FOLDER is None or not os.path.isdir(TEMP_FOLDER):
        TEMP_FOLDER = tempfile.mkdtemp()

    test_folder = os.path.dirname(__file__)
    IMG_PATH = os.path.join(TEMP_FOLDER, 'platane-1.jpeg')
    shutil.copy(os.path.join(test_folder, 'platane-1.jpeg'), IMG_PATH)


def teardown_module():
    global TEMP_FOLDER, IMG_PATH
    if os.path.exists(TEMP_FOLDER):
        shutil.rmtree(TEMP_FOLDER)
    TEMP_FOLDER = None
    IMG_PATH = None


def test_warped_img_path():
    warped_path = get_warped_img_path('/path/to/1234.jpeg')
    assert_equals('/path/to/1234_warped.jpeg', warped_path)


def test_warp_img():
    expected_warped_path = os.path.join(TEMP_FOLDER, 'platane-1_warped.jpeg')

    base = (300, 200)
    top = (100, 200)
    warped_path = warp_img(IMG_PATH, base, top)

    assert_equals(warped_path, expected_warped_path)
    assert_true(os.path.exists(warped_path))
