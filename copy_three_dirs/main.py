from pathlib import Path

from copy_three_dirs.join_images import join_images

try:
    from copy_three_dirs.parse_args import app_arg
except ImportError:
    from parse_args import app_arg
from shutil import copy
import asyncio
import time
import random
from concurrent.futures import ThreadPoolExecutor
import logging
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
from multiprocessing import cpu_count

# from tqdm.asyncio import tqdm


def copy_file(file_src, output_path):
    if file_src:
        try:
            copy(file_src, output_path)
            logger.debug(f"copied: {file_src.name}")
        except OSError:
            logger.error(f"error copy: {file_src.name}")
            return file_src.name


async def pool_copy_files(copy_list: list[Path], output_path: Path) -> list[Path]:
    max_threads = cpu_count() * 2 + 2
    logger.info(f"Thread Copy files : {len(copy_list)}.")

    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_threads) as pool:
        futures = [
            loop.run_in_executor(pool, copy_file, file_src, output_path)
            for file_src in copy_list
        ]
        with logging_redirect_tqdm():
            pbar = tqdm(
                asyncio.as_completed(futures),
                total=len(futures),
                desc=f"Copy to {output_path.name: <9}",
            )
            error_files: list = [await t for t in pbar]
    error_files = list(filter(lambda t: t is not None, error_files))
    return error_files


async def main_async(args):
    # print(args)
    work_path = Path(args["work"])
    input1_path = work_path.joinpath(Path(args["input1"]))
    input2_path = work_path.joinpath(Path(args["input2"]))
    output_path = work_path.joinpath(Path(args["output"]))
    notfound_path = work_path.joinpath(Path(args["notfound"]))
    found_path = work_path.joinpath(Path(args["found"]))
    joined_path = work_path.joinpath(Path(args["joined"]))
    to_join = args.get("join")

    input1_files = {i.stem: i for i in input1_path.glob("*.*")}
    # print(input1_files)
    input2_files = list(input2_path.glob("*.*"))

    output_path.mkdir(exist_ok=True, parents=True)
    copy_list = []
    found_dict = {}
    # not_found_list = []
    for files2 in input2_files:
        file_src = input1_files.get(files2.stem)
        if file_src:
            copy_list.append(file_src)
            found_dict[files2.stem] = files2

    not_found_dict = input1_files.copy()
    for copy_item in copy_list:
        del not_found_dict[copy_item.stem]
    not_found_list: list[Path] = list(not_found_dict.values())
    found_list: list[Path] = list(found_dict.values())

    print(
        f"The Input1 folder '{input1_path.name}' consist of files: {len(input1_files)}"
    )
    print(
        f"The Input2 folder '{input2_path.name}' consist of files: {len(input2_files)}"
    )
    logger.info(f"Copy only common files by name to '{output_path}' folder")
    if copy_list:
        error_files = await pool_copy_files(copy_list, output_path)
        if error_files:
            print(f"\nError copy files ({len(error_files)}): {error_files}")

    if found_list:
        found_path.mkdir(exist_ok=True, parents=True)
        logger.info(f"Copy found files to '{found_path}' folder")
        error_files = await pool_copy_files(found_list, found_path)
        if error_files:
            print(f"\nError copy files ({len(error_files)}): {error_files}")

    if not_found_list:
        notfound_path.mkdir(exist_ok=True, parents=True)
        logger.info(f"Copy notfound files to '{notfound_path}' folder")
        error_files = await pool_copy_files(not_found_list, notfound_path)
        if error_files:
            print(f"\nError copy files ({len(error_files)}): {error_files}")

    if to_join and copy_list and found_list:
        joined_path.mkdir(exist_ok=True, parents=True)
        for img1 in copy_list:
            img2 = found_dict[img1.stem]
            if img2.is_file():
                print(f"join_images({img1}, {img2}, {joined_path})")
                join_images(img1, img2, joined_path)


logger: logging


def main():
    global logger
    args = app_arg()
    logging.basicConfig(
        level=logging.DEBUG if args.get("verbose") else logging.INFO,
        # format="%(asctime)s [ %(threadName)s ] < %(filename)s:%(lineno)d > %(message)s",
        format="%(asctime)s [ %(threadName)s ]  %(message)s",
    )
    logger = logging.getLogger(__name__)
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
