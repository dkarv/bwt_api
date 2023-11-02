import argparse
import logging
import sys
import asyncio


from bwt_api import __version__
from .api import BwtApi

__author__ = "dkarv"
__copyright__ = "dkarv"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="BWT Api")
    parser.add_argument(
        "--version",
        action="version",
        version=f"bwt_api {__version__}",
    )
    parser.add_argument("--host", help="host")
    parser.add_argument("--code", help="user code")
    parser.add_argument(dest="cmd", choices=["current","daily","monthly","yearly"],default="current",help="Which data to fetch")
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    """Test

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose"]``).
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Start")
    api = BwtApi(args.host, args.code)
    match args.cmd:
        case "current":
            result = asyncio.run(api.get_current_data())
        case "daily":
            result = asyncio.run(api.get_daily_data())
        case "monthly":
            result = asyncio.run(api.get_monthly_data())
        case "yearly":
            result = asyncio.run(api.get_yearly_data())
    print(f"{result}")
    _logger.info("End")


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m bwt_api.skeleton 42
    #
    run()
