from arg_parser import build_config_from_args
from data.freddie_mac_data import FreddieMacData

def main():
    config = build_config_from_args()
    downloader = FreddieMacData(config)
    downloader.run()


if __name__ == "__main__":
    main()
