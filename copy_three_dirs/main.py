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


def copy_file(input1_files, files2, output_path, error_files):
    file_src = input1_files.get(files2.stem)
    if file_src:
        try:
            copy(file_src, output_path)
            logger.debug(f"copied: {files2.name}")
        except OSError:
            error_files.append(files2.name)


async def main_async(args):
    # print(args)
    input1_path = Path(args["input1"])
    input2_path = Path(args["input2"])
    output_path = Path(args["output"])

    input1_files = {i.stem: i for i in input1_path.glob("*.*")}
    # print(input1_files)
    input2_files = list(input2_path.glob("*.*"))
    output_path.mkdir(exist_ok=True, parents=True)

    error_files = []
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(cpu_count() * 2) as pool:
        futures = [
            loop.run_in_executor(
                pool, copy_file, input1_files, files2, output_path, error_files
            )
            for files2 in input2_files
        ]
        with logging_redirect_tqdm():
            pbar = tqdm(asyncio.as_completed(futures), total=len(futures))
            [await t for t in pbar]

    # if error_files:
    #     print(f"Error files: {error_files}")


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
