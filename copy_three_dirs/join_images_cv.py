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


def join_images(
    img1_path: Path,
    img2_path: Path,
    img_destination_path: Path,
    verbose=False,
    debug=False,
):
    setup_logger(verbose)
    if img1_path.suffix not in supported_extensions:
        # print(supported_extensions, type(supported_extensions))
        logger.error(f"not supported_extensions for {img1_path}")
        return img1_path

    image1 = cv2.imread(str(img1_path))
    image2 = cv2.imread(str(img2_path))

    image1_size = image1.shape
    image2_size = image2.shape

    if image1_size != image2_size:
        image2 = cv2.resize(image2, image1_size[:2])

    vis = np.concatenate((image1, image2), axis=1)

    save_path = img_destination_path.joinpath(img1_path.with_suffix(".jpg").name)

    try:
        cv2.imwrite(str(save_path), vis)
        logger.debug(f"joined: {save_path.name}")
    except OSError:
        logger.error(f"error saving the file: {save_path}")
        return save_path
    if debug:
        print(image1_size)
        print(image2_size)
        scale_percent = 50  # percent of original size
        width = int(vis.shape[1] * scale_percent / 100)
        height = int(vis.shape[0] * scale_percent / 100)
        dim = (width, height)
        print(dim)
        cv2.imshow("Join", cv2.resize(vis, dim))
        cv2.waitKey(10000)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        # format="%(asctime)s [ %(threadName)s ] < %(filename)s:%(lineno)d > %(message)s",
        format="%(asctime)s [ %(threadName)s ]  %(message)s",
    )
    logger = logging.getLogger(__name__)
    image1_path = Path("../tests/input_1/005965323-23.tif")
    image2_path = Path("../tests/input_2/005682407-23.tif")
    destination_path = Path("../tests/join_images")
    destination_path.mkdir(exist_ok=True, parents=True)
    join_images(image1_path, image2_path, destination_path)
