from pathlib import Path
from typing import Callable

import logging

import cv2
import numpy as np

supported_extensions = (".tif", ".tiff", ".jpg", ".png")

logger: logging
# print("OpenCV lib")


def setup_logger(verbose):
    global logger
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        # format="%(asctime)s [ %(threadName)s ] < %(filename)s:%(lineno)d > %(message)s",
        format="%(asctime)s %(levelname)s [pid: %(process)d]  %(message)s",
    )
    logger = logging.getLogger(__name__)

    # logging.getLogger("PIL").setLevel(logging.CRITICAL + 1)


def debug_img(img, title: str = "Title"):
    scale_percent = 50  # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    # print(dim)
    cv2.imshow(title, cv2.resize(img, dim))
    cv2.waitKey(10000)


def image_preprocessor(img1) -> cv2.Mat:
    # to GrayScale
    im1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    # add blur
    im1 = cv2.GaussianBlur(im1, (5, 5), 0)
    # threshold
    _, im1 = cv2.threshold(im1, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)
    return im1


def similarity_measure_fast(img1, img2, debug: bool = False) -> float:
    im1 = image_preprocessor(img1)
    im2 = image_preprocessor(img2)
    # Initiate FAST object with default values
    fast = cv2.FastFeatureDetector_create()

    # Disable nonmaxSuppression
    fast.setNonmaxSuppression(0)

    # find the keypoints on image (grayscale)
    kp1 = fast.detect(im1, None)
    kp2 = fast.detect(im2, None)

    # display the image with keypoints drawn on it
    if debug:
        # Print all default params
        print("Threshold: ", fast.getThreshold())
        print("nonmaxSuppression: ", fast.getNonmaxSuppression())
        print("neighborhood: ", fast.getType())
        print("Total Keypoints 1 without nonmaxSuppression: ", len(kp1))
        print("Total Keypoints 2 without nonmaxSuppression: ", len(kp2))

        im1 = cv2.drawKeypoints(im1, kp1, None)
        debug_img(im1, "Keypoints 1 without nonmaxSuppression")
        im2 = cv2.drawKeypoints(im2, kp2, None)
        debug_img(im1, "Keypoints 2 without nonmaxSuppression")

    # clear unused Mat before exit
    im1 = np.zeros(0)
    im2 = np.zeros(0)
    similarity_score = -1
    return similarity_score


def similarity_measure_orb(img1, img2, debug: bool = False) -> float:
    im1 = image_preprocessor(img1)
    im2 = image_preprocessor(img2)

    # Initialize the ORB detector
    orb = cv2.ORB_create()

    # Find keypoints and descriptors
    keypoints1, descriptors1 = orb.detectAndCompute(im1, None)
    keypoints2, descriptors2 = orb.detectAndCompute(im2, None)

    # Initialize a Brute Force Matcher
    bf = cv2.BFMatcher()

    # Match descriptors
    matches = bf.knnMatch(descriptors1, descriptors2, k=2)

    # Apply ratio test
    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)

    # Calculate a similarity score based on the number of good matches
    similarity_score = len(good_matches) / max(len(keypoints1), len(keypoints2))
    if debug:
        print("Similarity Score:", similarity_score)
    # clear unused Mat before exit
    im1 = np.zeros(0)
    im2 = np.zeros(0)
    return similarity_score


def similarity_measure_sift(img1, img2, debug: bool = False) -> float:
    im1 = image_preprocessor(img1)
    im2 = image_preprocessor(img2)

    # Initialize the SIFT detector
    sift = cv2.SIFT_create()

    # Find keypoints and descriptors
    keypoints1, descriptors1 = sift.detectAndCompute(im1, None)
    keypoints2, descriptors2 = sift.detectAndCompute(im2, None)

    # Initialize a Brute Force Matcher
    bf = cv2.BFMatcher()

    # Match descriptors
    matches = bf.knnMatch(descriptors1, descriptors2, k=2)

    # Apply ratio test
    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)

    # Calculate a similarity score based on the number of good matches
    similarity_score = len(good_matches) / max(len(keypoints1), len(keypoints2))

    if debug:
        im1 = cv2.drawKeypoints(im1, keypoints1, None)
        debug_img(im1, "Keypoints 1 without nonmaxSuppression")
        im2 = cv2.drawKeypoints(im2, keypoints2, None)
        debug_img(im1, "Keypoints 2 without nonmaxSuppression")
        print("Similarity Score:", similarity_score)

    # clear unused Mat before exit
    im1 = np.zeros(0)
    im2 = np.zeros(0)
    return similarity_score


def similarity_measure_match(img1, img2, debug: bool = False) -> float:
    im1 = image_preprocessor(img1)
    im2 = image_preprocessor(img2)
    res = cv2.matchTemplate(im1, im2, cv2.TM_SQDIFF_NORMED)
    similarity_res = 1.0 - res[0][0]
    if debug:
        print(f"similarity:  {similarity_res}")
        debug_img(im1)
        debug_img(im2)
    # clear unused Mat before exit
    im1 = np.zeros(0)
    im2 = np.zeros(0)
    return similarity_res


join_sim_methods: dict[str:Callable] = {
    "match": similarity_measure_match,
    "sift": similarity_measure_sift,
    "orb": similarity_measure_orb,
    "fast": similarity_measure_fast,
}


def join_images(args: dict) -> dict:
    img1_path: Path = args.get("img1_path")
    img2_path: Path = args.get("img2_path")
    img_destination_path: Path = args.get("img_destination_path")
    verbose: bool = args.get("verbose", False)
    join_similarity: bool = args.get("join_similarity", False)
    join_sim_method: str = args.get("join_sim_method", "sift")
    debug: bool = args.get("debug", False)
    setup_logger(verbose)
    result_join = {"error": None, "similarity_img": None, "similarity_score": None}
    if img1_path.suffix not in supported_extensions:
        # print(supported_extensions, type(supported_extensions))
        logger.error(f"not supported_extensions for {img1_path}")
        result_join["error"] = img1_path
        return result_join

    image1 = cv2.imread(str(img1_path))
    image2 = cv2.imread(str(img2_path))

    image1_size = image1.shape
    image2_size = image2.shape

    if image1_size != image2_size:
        image2 = cv2.resize(image2, (image1_size[1], image1_size[0]))

    image1image2 = np.concatenate((image1, image2), axis=1)

    save_path = img_destination_path.joinpath(img1_path.with_suffix(".tif").name)

    try:
        cv2.imwrite(str(save_path), image1image2)
        logger.debug(f"joined: {save_path.name}")
    except OSError:
        logger.error(f"error saving the file: {save_path}")
        result_join["error"] = save_path
        return result_join
    if debug:
        debug_img(image1image2)

    similarity_score = None
    if join_similarity:
        similarity_measure = join_sim_methods.get(join_sim_method)
        if similarity_measure:
            similarity_score = similarity_measure(image2, image1, debug)
        else:
            logger.error(f"join_sim_method not known: {join_sim_method}")

    # clear images
    image1 = np.zeros(0)
    image2 = np.zeros(0)
    image1image2 = np.zeros(0)

    result_join["similarity_img"] = img1_path
    result_join["similarity_score"] = similarity_score

    return result_join


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        # format="%(asctime)s [ %(threadName)s ] < %(filename)s:%(lineno)d > %(message)s",
        format="%(asctime)s [ %(threadName)s ]  %(message)s",
    )
    logger = logging.getLogger(__name__)
    image1_path = Path("../tests/input_1/009959054-23.tif")
    # image2_path = Path("../tests/input_2/104178477-23.tif")
    image2_path = Path("../tests/input_2/009959054-23.tif")

    destination_path = Path("../tests/join_images")
    destination_path.mkdir(exist_ok=True, parents=True)
    args = {
        "img1_path": image1_path,
        "img2_path": image2_path,
        "img_destination_path": destination_path,
        "verbose": False,
        "join_similarity": True,
        "debug": True,
        "join_sim_method": "sift",
    }
    result = join_images(args)
    print(result)
