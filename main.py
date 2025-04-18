import sys
from core_utils.arg_parser import build_config_from_args
from core_utils.config_loader import load_config_from_yaml
from data.freddie_mac_data import DataConfig, FreddieMacData


def main():
    if "--config" in sys.argv:
        config_path = sys.argv[sys.argv.index("--config") + 1]
        config = load_config_from_yaml("configs/freddie_mac_data.yaml", DataConfig)
    else:
        config = build_config_from_args()

    downloader = FreddieMacData(config)
    downloader.run()


if __name__ == "__main__":
    main()
    
    
