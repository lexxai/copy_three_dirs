from pathlib import Path

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
    logger.info(
        f"Thread Copy files : {len(copy_list)}. Use copy with max threads: {max_threads}"
    )

    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_threads) as pool:
        futures = [
            loop.run_in_executor(pool, copy_file, file_src, output_path)
            for file_src in copy_list
        ]
        with logging_redirect_tqdm():
            pbar = tqdm(asyncio.as_completed(futures), total=len(futures))
            error_files: list = [await t for t in pbar]
    error_files = list(filter(lambda t: t is not None, error_files))
    return error_files


async def main_async(args):
    # print(args)
    input1_path = Path(args["input1"])
    input2_path = Path(args["input2"])
    output_path = Path(args["output"])
    notfound_path = Path(args["notfound_path"])

    input1_files = {i.stem: i for i in input1_path.glob("*.*")}
    # print(input1_files)
    input2_files = list(input2_path.glob("*.*"))

    output_path.mkdir(exist_ok=True, parents=True)
    copy_list = []
    not_found_list = []
    for files2 in input2_files:
        file_src = input1_files.get(files2.stem)
        if file_src:
            copy_list.append(file_src)
        else:
            not_found_list.append((file_src))
    print(
        f"The Input1 folder '{input1_path.name}' consist of files: {len(input1_files)}"
    )
    print(
        f"The Input2 folder '{input2_path.name}' consist of files: {len(input2_files)}"
    )
    logger.info(f"Copy only common files by name to {output_path.name}")
    if copy_list:
        error_files = await pool_copy_files(copy_list, output_path)
        if error_files:
            print(f"\nError copy files ({len(error_files)}): {error_files}")

    if not_found_list:
        notfound_path.mkdir(exist_ok=True, parents=True)
        logger.info(f"Copy notfound files to {notfound_path.name}")
        error_files = await pool_copy_files(not_found_list, notfound_path)
        if error_files:
            print(f"\nError copy files ({len(error_files)}): {error_files}")


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
