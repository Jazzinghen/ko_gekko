import sys
import os
from loguru import logger
from datetime import datetime
import platformdirs
from pathlib import Path
import argparse
from urllib.parse import urlsplit
from typing import Optional

from ko_gekko.bin.fetch_database import FetchDatabase
from ko_gekko.common.nest import Nest

KOGEKKO_DATA_ROOT = platformdirs.user_data_path("kogekko", "jazzinghen", roaming=True)
KOGEKKO_LOG_FOLDER = KOGEKKO_DATA_ROOT / "logs"

logger.add(sys.stderr, format="{time} {level} {message}", level="WARNING")


def init_app():
    KOGEKKO_DATA_ROOT.mkdir(parents=True, exist_ok=True)
    KOGEKKO_LOG_FOLDER.mkdir(parents=True, exist_ok=True)


@logger.catch
def main(
    urls: list[str],
    out_path: Path,
    metadata_needed: bool = False,
    verbose: bool = False,
) -> int:
    if verbose:
        logger.add(sys.stdout, format="{time} {level} {message}", level="DEBUG")
    else:
        logger.add(sys.stdout, format="{time} {level} {message}", level="SUCCESS")

    with FetchDatabase(KOGEKKO_DATA_ROOT) as db, Nest(None) as nest:
        (retrieve_results, failed) = nest.retrieve_pages(urls)

        for result in retrieve_results:
            url_data = urlsplit(result.url)
            save_path = out_path / url_data.netloc
            save_path.mkdir(parents=True, exist_ok=True)

            page_name: str = url_data.netloc + ".html"
            if url_data.path:
                path_parts: list[str] = url_data.path.split("/")
                last_part = path_parts[-1]
                if not last_part:
                    last_part = path_parts[-2]

                if "." not in last_part:
                    last_part += ".html"

                page_name = last_part

            with open(save_path / page_name, "wb") as html_fd:
                html_fd.write(result.raw_data)

            last_fetch: Optional[datetime] = db.update_last_fetch(result.url)

            if metadata_needed:
                print(f"Metadata for URL: {result.url}")
                print(f"\tSite: {url_data.netloc}")
                print(f"\tLinks: {result.links}")
                print(f"\tImages: {result.images}")
                if last_fetch is not None:
                    last_fetch_pretty = last_fetch.strftime("%A %Y-%m-%d %H:%M%Z")
                    print(f"\tLast fetch: {last_fetch_pretty}")

        if failed:
            print("The following urls failed:")
            for url in failed:
                print(f"\t{url}")

    return os.EX_OK


if __name__ == "__main__":
    cli_parser = argparse.ArgumentParser(
        prog="KoGekko",
        description="Retrieve pages and check for images!",
    )
    cli_parser.add_argument(
        "urls",
        metavar="URL",
        type=str,
        nargs="*",
        help="list of urls to retrieve",
    )
    cli_parser.add_argument(
        "-o",
        "--output-path",
        metavar="PATH",
        type=Path,
        default=os.getcwd(),
        help="where to save the pages.",
    )
    cli_parser.add_argument(
        "-m",
        "--metadata",
        action="store_true",
        help="print extra metadata from the requested pages",
    )
    cli_parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable verbose output"
    )

    args = cli_parser.parse_args()

    urls: list[str] = args.urls

    # If no input urls let's check whether we are getting input from a pipe or from
    # an interactive shell
    if len(urls) == 0:
        if sys.stdin.isatty():
            cli_parser.print_help()
            sys.exit(os.EX_NOINPUT)

        for line in sys.stdin:
            urls.extend(line.split())

    init_app()

    # Tell Python to run the handler() function when SIGINT is recieved
    # signal(SIGINT, handler)
    sys.exit(main(urls, args.output_path, args.metadata, args.verbose))
