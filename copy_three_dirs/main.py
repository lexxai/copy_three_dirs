import logging
from pathlib import Path
from shutil import copy
import asyncio
from multiprocessing import cpu_count
from multiprocessing import freeze_support
from concurrent.futures import ThreadPoolExecutor

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm


try:
    from copy_three_dirs.parse_args import app_arg
    from copy_three_dirs.export_data import export_to_csv, export_similarity_to_csv
    import copy_three_dirs.join_images_tasks as ji_tasks

    from copy_three_dirs.join_images_cv import join_images

    # from copy_three_dirs.join_images_pil import join_images
except ImportError:
    from parse_args import app_arg
    from export_data import export_to_csv, export_similarity_to_csv
    import join_images_tasks as ji_tasks
    from join_images_cv import join_images

    # from join_images_pil import join_images


def copy_file(file_src, output_path):
    if file_src:
        try:
            copy(file_src, output_path)
            logger.debug(f"copied: {file_src.name}")
        except OSError:
            logger.error(f"error copy: {file_src.name}")
            return file_src.name


async def pool_copy_files(
    copy_list: list[Path],
    output_path: Path,
    verbose=False,
    join_tasks=0,
) -> list[Path]:
    max_threads = cpu_count() * 2 + 2 if not join_tasks else join_tasks
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
    # parse parameters of cli
    work_path = Path(args["work"])
    input1_path = Path(args["input1"])
    input2_path = Path(args["input2"])
    output_path = Path(args["output"])
    notfound1_path = Path(args["notfound1"])
    notfound2_path = Path(args["notfound2"])
    found_path = Path(args["found"])
    joined_path = Path(args["joined"])
    csv_path = Path(args["csv"])
    # add work prefix to path is path is not absolute
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
    if not csv_path.is_absolute():
        csv_path = work_path.joinpath(csv_path)
    to_join = args.get("join")
    to_join_only = args.get("join_only")
    join_mode = args.get("join_mode")
    join_tasks = args.get("join_tasks")
    join_similarity = args.get("join_similarity")

    # find files in source directories and build dict with keys as stem of filename
    input1_files = {i.stem: i for i in input1_path.glob("*.*")}
    input2_files = {i.stem: i for i in input2_path.glob("*.*")}
    # build sets of filenames by their stem for search later difference
    input1_files_set = set(input1_files.keys())
    input2_files_set = set(input2_files.keys())

    output_path.mkdir(exist_ok=True, parents=True)
    copy_list = []
    found_dict = {}
    # build list of files for copy
    for files2_stem, files2 in input2_files.items():
        file_src = input1_files.get(files2_stem)
        if file_src:
            copy_list.append(file_src)
            found_dict[files2_stem] = files2

    found_list: list[Path] = list(found_dict.values())
    # find difference input1 from input2
    not_found1_difference = input1_files_set.difference(input2_files_set)
    not_found1_list: list[Path] = [input1_files[item] for item in not_found1_difference]
    # find difference input2 from input1
    not_found2_difference = input2_files_set.difference(input1_files_set)
    not_found2_list: list[Path] = [input2_files[item] for item in not_found2_difference]
    # check if need only joint than skip copy tasks
    if not to_join_only:
        print(
            f"The Input1 folder '{input1_path.name}' consist of files: {len(input1_files)}"
        )
        print(
            f"The Input2 folder '{input2_path.name}' consist of files: {len(input2_files)}"
        )
        logger.info(f"Copy only common files by name to '{output_path}' folder")
        # async copy files from copy_list
        if copy_list:
            error_files = await pool_copy_files(copy_list, output_path)
            if error_files:
                print(f"\nError copy files ({len(error_files)}): {error_files}")
        # async copy files from found_list
        if found_list:
            found_path.mkdir(exist_ok=True, parents=True)
            logger.info(f"Copy found files to '{found_path}' folder")
            error_files = await pool_copy_files(found_list, found_path)
            if error_files:
                print(f"\nError copy files ({len(error_files)}): {error_files}")
        # async copy files from not_found1_list
        if not_found1_list:
            notfound1_path.mkdir(exist_ok=True, parents=True)
            logger.info(f"Copy notfound files to '{notfound1_path}' folder")
            error_files = await pool_copy_files(not_found1_list, notfound1_path)
            if error_files:
                print(f"\nError copy files ({len(error_files)}): {error_files}")
            export_to_csv(not_found1_list, csv_path.joinpath("not_found1.csv"))
        # async copy files from not_found2_list
        if not_found2_list:
            notfound2_path.mkdir(exist_ok=True, parents=True)
            logger.info(f"Copy notfound files to '{notfound2_path}' folder")
            error_files = await pool_copy_files(not_found2_list, notfound2_path)
            if error_files:
                print(f"\nError copy files ({len(error_files)}): {error_files}")
            export_to_csv(not_found2_list, csv_path.joinpath("not_found2.csv"))
    # tasks of join images from directories copy_list and found_list and check similarity of them
    if (to_join or to_join_only) and copy_list and found_list:
        joined_path.mkdir(exist_ok=True, parents=True)
        results = []
        # check what method of CPU bounding task will to use, by default will to used method 'future_thread'
        match join_mode:
            case "one_core":
                # one_core
                results = ji_tasks.join_images_one_core(
                    copy_list,
                    found_dict,
                    joined_path,
                    verbose=args.get("verbose"),
                    join_tasks=join_tasks,
                    join_similarity=join_similarity,
                )
            case "future_core":
                # future_core
                results = ji_tasks.join_images_future_core(
                    copy_list,
                    found_dict,
                    joined_path,
                    verbose=args.get("verbose"),
                    join_tasks=join_tasks,
                    join_similarity=join_similarity,
                )
            case "future_thread":
                # future_thread
                results = ji_tasks.join_images_future_thread(
                    copy_list,
                    found_dict,
                    joined_path,
                    verbose=args.get("verbose"),
                    join_tasks=join_tasks,
                    join_similarity=join_similarity,
                )
            case "future_core_async":
                # future_thread
                results = await ji_tasks.join_images_future_core_async(
                    copy_list,
                    found_dict,
                    joined_path,
                    verbose=args.get("verbose"),
                    join_tasks=join_tasks,
                    join_similarity=join_similarity,
                )
            case _:
                logger.error("Join method unknown")

        # after join tasks
        if join_similarity:
            # export similarity data for file CSV
            export_similarity_to_csv(results, csv_path.joinpath("join_similarity.csv"))
        # filter from results only error_files list
        error_files = list(filter(lambda t: t.get("error") is not None, results))
        if error_files:
            print(f"\nError join files ({len(error_files)}): {error_files}")


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
    # async io tasks
    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt as e:
        logger.info("Keyboard Interrupt")


if __name__ == "__main__":
    main()
