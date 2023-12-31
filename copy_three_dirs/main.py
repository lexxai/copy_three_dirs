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
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import freeze_support
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


async def pool_join_images_async_proc(
    img1_list: list[Path], img2_dict: dict, output_path: Path, verbose=False
) -> list[Path]:
    max_processes = cpu_count()
    logger.info(f"Processes ({max_processes}) of Join files : {len(img1_list)}.")

    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor(max_processes) as pool:
        futures = [
            loop.run_in_executor(
                pool,
                join_images,
                img1_path,
                img2_dict.get(img1_path.stem),
                output_path,
                verbose,
            )
            for img1_path in img1_list
        ]
        with logging_redirect_tqdm():
            pbar = tqdm(
                asyncio.as_completed(futures),
                total=len(futures),
                desc=f"Join to {output_path.name: <9}",
            )
            error_files: list = [await t for t in pbar]
    error_files = list(filter(lambda t: t is not None, error_files))
    return error_files


def pool_join_images_proc(
    img1_list: list[Path], img2_dict: dict, output_path: Path, verbose=False
) -> list[Path]:
    max_processes = cpu_count()
    logger.info(f"Processes ({max_processes}) of Join files : {len(img1_list)}.")

    # loop = asyncio.get_running_loop()
    with ProcessPoolExecutor(max_processes) as pool:
        futures = [
            pool.submit(
                join_images,
                img1_path,
                img2_dict.get(img1_path.stem),
                output_path,
                verbose,
            )
            for img1_path in img1_list
        ]
        with logging_redirect_tqdm():
            pbar_future = tqdm(
                concurrent.futures.as_completed(futures),
                total=len(futures),
                desc=f"Join to {output_path.name: <9}",
            )
            error_files: list = [future.result() for future in pbar_future]
    error_files = list(filter(lambda t: t is not None, error_files))
    return error_files


def pool_join_images_thread(
    img1_list: list[Path], img2_dict: dict, output_path: Path, verbose=False
) -> list[Path]:
    max_threads = cpu_count() * 4 + 2
    logger.info(f"Threads ({max_threads}) of Join files : {len(img1_list)}.")

    # loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_threads) as pool:
        futures = [
            pool.submit(
                join_images,
                img1_path,
                img2_dict.get(img1_path.stem),
                output_path,
                verbose,
            )
            for img1_path in img1_list
        ]
        with logging_redirect_tqdm():
            pbar_future = tqdm(
                concurrent.futures.as_completed(futures),
                total=len(futures),
                desc=f"Join to {output_path.name: <9}",
            )
            error_files: list = [future.result() for future in pbar_future]
    error_files = list(filter(lambda t: t is not None, error_files))
    return error_files


def join_images_one_core(
    copy_list: list[Path], found_dict: dict, joined_path: Path, verbose: bool = False
):
    logger.info(f"One core process of Join files : {len(copy_list)}.")
    with logging_redirect_tqdm():
        for img1 in tqdm(
            copy_list, total=len(copy_list), desc=f"Join to {joined_path.name: <9}"
        ):
            img2 = found_dict[img1.stem]
            if img1.is_file() and img2.is_file():
                # logger.info(f"join_images({img1}, {img2}, {joined_path})")
                join_images(img1, img2, joined_path)


def join_images_future_core(
    copy_list: list[Path], found_dict: dict, joined_path: Path, verbose: bool = False
):
    error_files = pool_join_images_proc(copy_list, found_dict, joined_path, verbose)
    if error_files:
        print(f"\nError join files ({len(error_files)}): {error_files}")


def join_images_future_thread(
    copy_list: list[Path], found_dict: dict, joined_path: Path, verbose: bool = False
):
    error_files = pool_join_images_thread(copy_list, found_dict, joined_path, verbose)
    if error_files:
        print(f"\nError join files ({len(error_files)}): {error_files}")


async def join_images_future_core_async(
    copy_list: list[Path], found_dict: dict, joined_path: Path, verbose: bool = False
):
    error_files = await pool_join_images_async_proc(
        copy_list, found_dict, joined_path, verbose
    )
    if error_files:
        print(f"\nError join files ({len(error_files)}): {error_files}")


async def main_async(args):
    # print(args)
    work_path = Path(args["work"])

    input1_path = Path(args["input1"])
    input2_path = Path(args["input2"])
    output_path = Path(args["output"])
    notfound1_path = Path(args["notfound1"])
    notfound2_path = Path(args["notfound2"])
    found_path = Path(args["found"])
    joined_path = Path(args["joined"])
    if not input1_path.is_absolute():
        input1_path = work_path.joinpath(input1_path)
    if not input2_path.is_absolute():
        input2_path = work_path.joinpath(input2_path)
    if not output_path.is_absolute():
        output_path = work_path.joinpath(output_path)
    if not notfound1_path.is_absolute():
        notfound1_path = work_path.joinpath(notfound1_path)
    if not notfound2_path.is_absolute():
        notfound2_path = work_path.joinpath(notfound2_path)
    if not found_path.is_absolute():
        found_path = work_path.joinpath(found_path)
    if not joined_path.is_absolute():
        joined_path = work_path.joinpath(joined_path)

    to_join = args.get("join")
    to_join_only = args.get("join_only")
    join_mode = args.get("join_mode")

    input1_files = {i.stem: i for i in input1_path.glob("*.*")}
    # print(input1_files)
    # input2_files = list(input2_path.glob("*.*"))
    input2_files = {i.stem: i for i in input2_path.glob("*.*")}

    input1_files_set = set(input1_files.keys())
    input2_files_set = set(input2_files.keys())

    output_path.mkdir(exist_ok=True, parents=True)
    copy_list = []
    found_dict = {}
    # not_found1_list = []
    for files2_stem, files2 in input2_files.items():
        file_src = input1_files.get(files2_stem)
        if file_src:
            copy_list.append(file_src)
            found_dict[files2_stem] = files2

    found_list: list[Path] = list(found_dict.values())

    # not_found1_dict = input1_files.copy()
    # for copy_item in copy_list:
    #     item = not_found1_dict.get(copy_item.stem)
    #     if item:
    #         del not_found1_dict[copy_item.stem]
    # not_found1_list: list[Path] = list(not_found1_dict.values())

    not_found1_difference = input1_files_set.difference(input2_files_set)
    not_found1_list: list[Path] = [input1_files[item] for item in not_found1_difference]

    not_found2_difference = input2_files_set.difference(input1_files_set)
    not_found2_list: list[Path] = [input2_files[item] for item in not_found2_difference]

    if not to_join_only:
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

        if not_found1_list:
            notfound1_path.mkdir(exist_ok=True, parents=True)
            logger.info(f"Copy notfound files to '{notfound1_path}' folder")
            error_files = await pool_copy_files(not_found1_list, notfound1_path)
            if error_files:
                print(f"\nError copy files ({len(error_files)}): {error_files}")

        if not_found2_list:
            notfound2_path.mkdir(exist_ok=True, parents=True)
            logger.info(f"Copy notfound files to '{notfound2_path}' folder")
            error_files = await pool_copy_files(not_found2_list, notfound2_path)
            if error_files:
                print(f"\nError copy files ({len(error_files)}): {error_files}")

    # to join
    if (to_join or to_join_only) and copy_list and found_list:
        # joined_path.mkdir(exist_ok=True, parents=True)
        # error_files = await pool_join_images(
        #     copy_list, found_dict, joined_path, verbose=args.get("verbose")
        # )
        # if error_files:
        #     print(f"\nError join files ({len(error_files)}): {error_files}")

        joined_path.mkdir(exist_ok=True, parents=True)
        match join_mode:
            case "one_core":
                # one_core
                join_images_one_core(
                    copy_list, found_dict, joined_path, args.get("verbose")
                )
            case "future_core":
                # future_core
                join_images_future_core(
                    copy_list, found_dict, joined_path, args.get("verbose")
                )
            case "future_thread":
                # future_thread
                join_images_future_thread(
                    copy_list, found_dict, joined_path, args.get("verbose")
                )
            case "future_core_async":
                # future_thread
                await join_images_future_core_async(
                    copy_list, found_dict, joined_path, args.get("verbose")
                )
            case _:
                logger.error("Join method unknown")


logger: logging


def main():
    # only for pyinstall exe, need to use freeze_support
    freeze_support()
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
