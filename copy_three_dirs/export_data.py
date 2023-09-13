import csv
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def export_to_csv(
    data: list, filename: Path = Path("data.csv"), settings_path: Path | None = None
) -> bool:
    result = False
    if not data:
        return result
    fieldnames = ["DATE", "NAME"]
    filename.parent.mkdir(exist_ok=True, parents=True)
    try:
        with open(filename, "a", newline="") as csvfile:
            csvfile.tell()
            last_pos = csvfile.tell()
            writer = csv.writer(csvfile)
            # print(f"{last_pos=}")
            if not last_pos:
                writer.writerow(fieldnames)
            for texts in data:
                when = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                row = [when, texts]
                writer.writerow(row)
            result = True
    except OSError:
        logger.error(f"Error save csv, {filename}")
    finally:
        logger.info(f"Saved csv: {filename}")
    return result


def export_similarity_to_csv(
    data: list,
    filename: Path = Path("similarity_data.csv"),
    settings_path: Path | None = None,
) -> bool:
    result = False
    if not data:
        return result
    fieldnames = ["DATE", "NAME", "SCORE"]
    filename.parent.mkdir(exist_ok=True, parents=True)
    try:
        with open(filename, "a", newline="") as csvfile:
            csvfile.tell()
            last_pos = csvfile.tell()
            writer = csv.writer(csvfile)
            # print(f"{last_pos=}")
            if not last_pos:
                writer.writerow(fieldnames)
            for records in data:
                when = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                filename_img = records.get("similarity_img", Path()).name
                score = records.get("similarity_score")
                row = [when, filename_img, score]
                writer.writerow(row)
            result = True
    except OSError:
        logger.error(f"Error save csv, {filename}")
    finally:
        logger.info(f"Saved csv: {filename}")
    return result
