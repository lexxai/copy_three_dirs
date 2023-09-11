from pathlib import Path

from PIL import Image


def join_images(img1_path: Path, img2_path: Path, img_destination_path: Path):
    # Read the two images
    image1 = Image.open(img1_path)
    # image1.show()
    image2 = Image.open(img2_path)
    # image2.show()
    # resize, first image
    # image1 = image1.resize((426, 240))
    image1_size = image1.size
    image2 = image2.resize(image1_size)
    # image2_size = image2.size

    new_image = Image.new("RGB", (2 * image1_size[0], image1_size[1]), (250, 250, 250))
    new_image.paste(image1, (0, 0))
    new_image.paste(image2, (image1_size[0], 0))
    save_path = img_destination_path.joinpath(img1_path.with_suffix(".jpg").name)
    new_image.save(save_path, "JPEG")
    # new_image.show()


if __name__ == "__main__":
    image1_path = Path("../tests/input_1/005965323-23.tif")
    image2_path = Path("../tests/input_2/005682407-23.tif")
    destination_path = Path("../tests/join_images")
    destination_path.mkdir(exist_ok=True, parents=True)
    join_images(image1_path, image2_path, destination_path)