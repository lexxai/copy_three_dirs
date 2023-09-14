from pathlib import Path

import logging

from PIL import Image

extensions = Image.registered_extensions()
supported_extensions = {ex for ex, f in extensions.items() if f in Image.OPEN}


logger: logging

# print("Pillow lib")


def setup_logger(verbose):
    global logger
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        # format="%(asctime)s [ %(threadName)s ] < %(filename)s:%(lineno)d > %(message)s",
        format="%(asctime)s %(levelname)s [pid: %(process)d]  %(message)s",
    )
    logger = logging.getLogger(__name__)

    logging.getLogger("PIL").setLevel(logging.CRITICAL + 1)


def join_images(
    img1_path: Path,
    img2_path: Path,
    img_destination_path: Path,
    verbose=False,
):
    setup_logger(verbose)
    if img1_path.suffix not in supported_extensions:
        # print(supported_extensions, type(supported_extensions))
        logger.error(f"not supported_extensions for {img1_path}")
        return img1_path
    # Read the two images
    image1 = Image.open(img1_path)
    # image1.show()
    image2 = Image.open(img2_path)
    # image2.show()
    # resize, first image
    # image1 = image1.resize((426, 240))
    image1_size = image1.size
    mage2_size = image2.size
    if image1_size != mage2_size:
        image2 = image2.resize(image1_size)
    # image2_size = image2.size

    new_image = Image.new("RGB", (2 * image1_size[0], image1_size[1]), (250, 250, 250))
    new_image.paste(image1, (0, 0))
    new_image.paste(image2, (image1_size[0], 0))
    save_path = img_destination_path.joinpath(img1_path.with_suffix(".jpg").name)

    try:
        new_image.save(save_path, "JPEG")
        logger.debug(f"joined: {save_path.name}")
    except OSError:
        logger.error(f"error saving the file: {save_path}")
        return save_path
    # new_image.show()


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
