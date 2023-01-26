# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
""" KoGekko's CLI

Example implementation of a CLI using KoGekko as a page fetching library.

The CLI accepts the following options:

    - output-path
        Folder where to write the retrieved pages
    - threads
        Amount of threads to use for parallel page retrieval
    - metadata
        Extract metadata (i.e. last time fetched, amount of links, amount of images)
        from the retrieved pages
    - local
        Use `pywebcopy` to store a full local copy of the page, in contrast to the
        standard usage, which stores only the HTML code of the retrieved page
    - verbose
        Enable extended status report of the CLI and the library

Attributes
----------
KOGEKKO_DATA_ROOT : pathlib.Path
    Path to the location where to store cross-use data

KOGEKKO_LOG_ROOT : pathlib.Path
    Path to the location where to store logs
"""

from datetime import datetime
from loguru import logger
from pathlib import Path
from typing import Optional, NamedTuple
from urllib.parse import urlsplit
import argparse
import os
import platformdirs
import pywebcopy
import sys

from ko_gekko.bin.fetch_database import FetchDatabase
from ko_gekko.common.nest import Nest

logger.add(sys.stderr, format="{time} {level} {message}", level="WARNING")

if not sys.warnoptions:
    import warnings

    warnings.simplefilter("ignore")

KOGEKKO_DATA_ROOT: Path = platformdirs.user_data_path(
    "ko_gekko", "jazzinghen", roaming=True
)
KOGEKKO_LOG_ROOT: Path = (
    platformdirs.user_state_path("ko_gekko", "jazzinghen", roaming=True) / "logs"
)


class KoGekkoCLIConfig(NamedTuple):
    urls: list[str]
    out_path: Path
    threads: Optional[int] = None
    get_metadata: bool = False
    save_local: bool = False
    verbose: bool = False


def init_app():
    KOGEKKO_DATA_ROOT.mkdir(parents=True, exist_ok=True)
    KOGEKKO_LOG_ROOT.mkdir(parents=True, exist_ok=True)


@logger.catch
def main(config: KoGekkoCLIConfig) -> int:
    if config.verbose:
        logger.add(sys.stdout, format="{time} {level} {message}", level="DEBUG")
    else:
        logger.add(sys.stdout, format="{time} {level} {message}", level="SUCCESS")

    logger.add(
        KOGEKKO_LOG_ROOT / "ko_gekko.log",
        format="{time} {level} {message}",
        level="DEBUG",
        rotation="5 MB",
        compression="zip",
    )

    with FetchDatabase(KOGEKKO_DATA_ROOT) as db, Nest(config.threads) as nest:
        (retrieve_results, failed) = nest.retrieve_pages(config.urls)

        for result in retrieve_results:
            url_data = urlsplit(result.url)
            save_path = config.out_path / url_data.netloc
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

            if config.get_metadata:
                logger.success(f"Metadata for URL: {result.url}")
                logger.success(f"\tSite: {url_data.netloc}")
                logger.success(f"\tLinks: {result.links}")
                logger.success(f"\tImages: {result.images}")
                if last_fetch is not None:
                    last_fetch_pretty = last_fetch.strftime("%A %Y-%m-%d %H:%M%Z")
                    logger.success(f"\tLast fetch: {last_fetch_pretty}")

            if config.save_local:
                local_copy_path = save_path / "local"
                pywebcopy.save_webpage(
                    url=result.url,
                    project_folder=str(local_copy_path),
                    project_name=url_data.netloc,
                    bypass_robots=True,
                    debug=False,
                    open_in_browser=False,
                    delay=None,
                    threaded=True,
                )

        if failed:
            failed_urls: str = ", ".join(failed)
            logger.warning(f"The following urls failed: {failed_urls}")

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
        default=Path(os.getcwd(), "downloads"),
        help="where to save the pages",
    )
    cli_parser.add_argument(
        "-l",
        "--local",
        action="store_true",
        help="saves pages for offline view (PyWebCopy interface)",
    )
    cli_parser.add_argument(
        "-m",
        "--metadata",
        action="store_true",
        help="print extra metadata from the requested pages",
    )
    cli_parser.add_argument(
        "-t",
        "--threads",
        metavar="NUM",
        type=int,
        help=(
            "number of concurrent threads to use for page retrieval. Passing a value"
            "smaller than 0 will set the application to single threaded."
            "If not provided the application will use python 3 default thread amount."
        ),
    )
    cli_parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable verbose output"
    )

    args = cli_parser.parse_args()

    cli_config: KoGekkoCLIConfig = KoGekkoCLIConfig(
        args.urls,
        args.output_path,
        args.threads,
        args.metadata,
        args.local,
        args.verbose,
    )

    # If no input urls let's check whether we are getting input from a pipe or from
    # an interactive shell
    if len(cli_config.urls) == 0:
        if sys.stdin.isatty():
            cli_parser.print_help()
            sys.exit(os.EX_NOINPUT)

        for line in sys.stdin:
            cli_config.urls.extend(line.split())

    if cli_config.threads is not None and cli_config.threads <= 0:
        cli_config.threads = 1  # type: ignore

    init_app()

    # Tell Python to run the handler() function when SIGINT is recieved
    # signal(SIGINT, handler)
    sys.exit(main(cli_config))
