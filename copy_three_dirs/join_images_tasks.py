import asyncio
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import cpu_count
from pathlib import Path

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

try:
    from copy_three_dirs.join_images_cv import join_images
except ImportError:
    from join_images_cv import join_images
import logging

logger = logging.getLogger(__name__)


async def pool_join_images_async_proc(
    img1_list: list[Path],
    img2_dict: dict,
    output_path: Path,
    verbose=False,
    join_tasks=0,
    join_similarity=False,
) -> list[dict]:
    max_processes = cpu_count() if not join_tasks else join_tasks
    if max_processes > 61:
        max_processes = 61
    logger.info(f"Processes ({max_processes}) of Join files : {len(img1_list)}.")
    args = {
        "img1_path": None,
        "img2_path": None,
        "img_destination_path": output_path,
        "verbose": verbose,
        "join_similarity": join_similarity,
    }
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor(max_processes) as pool:
        futures = []
        for img1_path in img1_list:
            args["img1_path"] = img1_path
            args["img2_path"] = img2_dict.get(img1_path.stem)
            futures.append(loop.run_in_executor(pool, join_images, args.copy()))
        with logging_redirect_tqdm():
            pbar = tqdm(
                asyncio.as_completed(futures),
                total=len(futures),
                desc=f"Join to {output_path.name: <9}",
            )
            results: list = [await t for t in pbar]
    return results


def pool_join_images_proc(
    img1_list: list[Path],
    img2_dict: dict,
    output_path: Path,
    verbose=False,
    join_tasks=0,
    join_similarity=False,
) -> list[dict]:
    max_processes = cpu_count() if not join_tasks else join_tasks
    if max_processes > 61:
        max_processes = 61
    logger.info(f"Processes ({max_processes}) of Join files : {len(img1_list)}.")

    # loop = asyncio.get_running_loop()
    args = {
        "img1_path": None,
        "img2_path": None,
        "img_destination_path": output_path,
        "verbose": verbose,
        "join_similarity": join_similarity,
    }
    with ProcessPoolExecutor(max_processes) as pool:
        # futures = [
        #     pool.submit(
        #         join_images,
        #         img1_path,
        #         img2_dict.get(img1_path.stem),
        #         output_path,
        #         verbose,
        #     )
        #     for img1_path in img1_list
        # ]
        futures = []
        for img1_path in img1_list:
            args["img1_path"] = img1_path
            args["img2_path"] = img2_dict.get(img1_path.stem)
            futures.append(pool.submit(join_images, args.copy()))
        with logging_redirect_tqdm():
            pbar_future = tqdm(
                concurrent.futures.as_completed(futures),
                total=len(futures),
                desc=f"Join to {output_path.name: <9}",
            )
            results: list = [future.result() for future in pbar_future]
    return results


def pool_join_images_thread(
    img1_list: list[Path],
    img2_dict: dict,
    output_path: Path,
    verbose=False,
    join_tasks=0,
    join_similarity=False,
) -> list[dict]:
    max_threads = cpu_count() * 4 + 2 if not join_tasks else join_tasks
    logger.info(f"Threads ({max_threads}) of Join files : {len(img1_list)}.")
    # loop = asyncio.get_running_loop()
    args = {
        "img1_path": None,
        "img2_path": None,
        "img_destination_path": output_path,
        "verbose": verbose,
        "join_similarity": join_similarity,
    }
    with ThreadPoolExecutor(max_threads) as pool:
        futures = []
        for img1_path in img1_list:
            args["img1_path"] = img1_path
            args["img2_path"] = img2_dict.get(img1_path.stem)
            futures.append(pool.submit(join_images, args.copy()))

        with logging_redirect_tqdm():
            pbar_future = tqdm(
                concurrent.futures.as_completed(futures),
                total=len(futures),
                desc=f"Join to {output_path.name: <9}",
            )
            results: list = [future.result() for future in pbar_future]
    return results


def join_images_one_core(
    copy_list: list[Path],
    found_dict: dict,
    joined_path: Path,
    verbose: bool = False,
    join_tasks=0,
    join_similarity=False,
) -> list[dict]:
    logger.info(f"One core process of Join files : {len(copy_list)}.")
    results = []
    args = {
        "img1_path": None,
        "img2_path": None,
        "img_destination_path": joined_path,
        "verbose": verbose,
        "join_similarity": join_similarity,
    }
    with logging_redirect_tqdm():
        for img1 in tqdm(
            copy_list, total=len(copy_list), desc=f"Join to {joined_path.name: <9}"
        ):
            img2 = found_dict[img1.stem]
            if img1.is_file() and img2.is_file():
                args["img1_path"] = img1
                args["img2_path"] = img2
                # logger.info(f"join_images({img1}, {img2}, {joined_path})")
                result = join_images(args.copy())
                results.append(result)
    return results


def join_images_future_core(
    copy_list: list[Path],
    found_dict: dict,
    joined_path: Path,
    verbose: bool = False,
    join_tasks=0,
    join_similarity=False,
):
    results = pool_join_images_proc(
        copy_list, found_dict, joined_path, verbose, join_tasks, join_similarity
    )
    return results


def join_images_future_thread(
    copy_list: list[Path],
    found_dict: dict,
    joined_path: Path,
    verbose: bool = False,
    join_tasks=0,
    join_similarity=False,
):
    results = pool_join_images_thread(
        copy_list, found_dict, joined_path, verbose, join_tasks, join_similarity
    )
    return results


async def join_images_future_core_async(
    copy_list: list[Path],
    found_dict: dict,
    joined_path: Path,
    verbose: bool = False,
    join_tasks=0,
    join_similarity=False,
):
    results = await pool_join_images_async_proc(
        copy_list, found_dict, joined_path, verbose, join_tasks, join_similarity
    )
    return results
