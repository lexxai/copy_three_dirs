# from pathlib import Path
from aiopath import AsyncPath
from aioshutil import copyfile

try:
    from copy_three_dirs.parse_args import app_arg
except ImportError:
    from parse_args import app_arg
# from shutil import copy
import asyncio

# import time
# import random
from concurrent.futures import ThreadPoolExecutor
import logging
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
from multiprocessing import cpu_count


async def copy_file(file_src: AsyncPath, output_path: AsyncPath) -> str | None:
    if file_src:
        try:
            if await file_src.is_file():
                await copyfile(file_src, output_path)
                logger.debug(f"copied: {file_src.name}")
        except OSError:
            logger.error(f"error copy: {file_src.name}")
            return file_src.name


async def main_async(args):
    # print(args)
    input1_path = AsyncPath(args["input1"])
    input2_path = AsyncPath(args["input2"])
    output_path = AsyncPath(args["output"])

    input1_files = {i.stem: i for i in await input1_path.glob("*.*")}
    # print(input1_files)
    input2_files = list(await input2_path.glob("*.*"))

    await output_path.mkdir(exist_ok=True, parents=True)
    copy_list = []
    for files2 in input2_files:
        file_src = input1_files.get(files2.stem)
        if file_src:
            copy_list.append(file_src)
    print(
        f"The Input1 folder '{input1_path.name}' consist of files: {len(input1_files)}"
    )
    print(
        f"The Input2 folder '{input2_path.name}' consist of files: {len(input2_files)}"
    )

    max_threads = cpu_count() * 2 + 2
    print(f"Common files : {len(copy_list)}. Use copy with max threads: {max_threads}")

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
