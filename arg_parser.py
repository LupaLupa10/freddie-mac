import argparse
import os
from dotenv import load_dotenv
from data.freddie_mac_data import DataConfig


def parse_args():
    parser = argparse.ArgumentParser(description="Download and consolidate Freddie Mac loan data")
    parser.add_argument("--start-year", type=int, required=True, help="Start year of data to download")
    parser.add_argument("--end-year", type=int, required=True, help="End year of data to download")
    parser.add_argument("--start-qtr", type=int, default=1, choices=[1, 2, 3, 4], help="Start quarter")
    parser.add_argument("--end-qtr", type=int, default=4, choices=[1, 2, 3, 4], help="End quarter")
    parser.add_argument("--remove-unzipped", action="store_true", help="Delete raw txt files after processing")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    return parser.parse_args()


def build_config_from_args():
    load_dotenv()
    args = parse_args()

    return DataConfig(
        username=os.getenv("FREDDIE_MAC_USERNAME"),
        password=os.getenv("FREDDIE_MAC_PASSWORD"),
        start_year=args.start_year,
        end_year=args.end_year,
        start_qtr=args.start_qtr,
        end_qtr=args.end_qtr,
        remove_unzipped=args.remove_unzipped,
        verbose=args.verbose
    )
