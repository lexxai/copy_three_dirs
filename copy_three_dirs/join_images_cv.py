from pathlib import Path

import logging

import cv2
import numpy as np

supported_extensions = (".tif", ".tiff", ".jpg", ".png")

logger: logging


def setup_logger(verbose):
    global logger
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        # format="%(asctime)s [ %(threadName)s ] < %(filename)s:%(lineno)d > %(message)s",
        format="%(asctime)s %(levelname)s [pid: %(process)d]  %(message)s",
    )
    logger = logging.getLogger(__name__)

    # logging.getLogger("PIL").setLevel(logging.CRITICAL + 1)


def debug_img(img):
    scale_percent = 50  # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    print(dim)
    cv2.imshow("Join", cv2.resize(img, dim))
    cv2.waitKey(10000)


def similarity_measure(img1, img2, debug: bool = False) -> float:
    im1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    im2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    im1 = cv2.GaussianBlur(im1, (5, 5), 0)  # Ad
    im2 = cv2.GaussianBlur(im2, (5, 5), 0)  # Ad
    ret, im1 = cv2.threshold(im1, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)
    ret, im2 = cv2.threshold(im2, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)
    res = cv2.matchTemplate(im1, im2, cv2.TM_SQDIFF_NORMED)
    similarity_res = 1.0 - res[0][0]
    if debug:
        print(f"similarity:  {similarity_res}")
        debug_img(im1)
        debug_img(im2)
    im1 = np.zeros(0)
    im2 = np.zeros(0)
    return similarity_res


def join_images(args: dict) -> dict:
    img1_path: Path = args.get("img1_path")
    img2_path: Path = args.get("img2_path")
    img_destination_path: Path = args.get("img_destination_path")
    verbose: bool = args.get("verbose", False)
    join_similarity: bool = args.get("join_similarity", False)
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

    if join_similarity:
        similarity_score = similarity_measure(image2, image1, debug)
    else:
        similarity_score = None

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
    image2_path = Path("../tests/input_2/104178477-23.tif")
    # image2_path = Path("../tests/input_2/009959054-23.tif")

    destination_path = Path("../tests/join_images")
    destination_path.mkdir(exist_ok=True, parents=True)
    args = {
        "img1_path": image1_path,
        "img2_path": image2_path,
        "img_destination_path": destination_path,
        "verbose": False,
        "join_similarity": True,
        "debug": True,
    }
    result = join_images(args)
    print(result)
