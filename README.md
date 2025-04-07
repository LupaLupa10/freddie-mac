# 📊 Freddie Mac Loan Data Downloader

A Python CLI tool to download, extract, and consolidate Freddie Mac Single-Family Loan-Level Datasets — designed for researchers, analysts, and engineers working with mortgage data.

## 🔧 Features

- ✅ Authenticates via `.env` credentials
- ✅ Downloads quarterly loan ZIP files from Freddie Mac
- ✅ Extracts and merges `orig` (origination) and `svcg` (performance) data
- ✅ Outputs clean, consolidated CSVs
- ✅ CLI + YAML config support
- ✅ Modular, testable design using `@dataclass`
- ✅ Poetry-based for reproducible environments

## 📁 Project Structure

```
├── data/
│   ├── freddie_mac_data.py  
│   ├── combined_dataset/    
│   └── raw_dataset/         
├── .env                      
├── arg_parser.py       
├── constants.py         
├── main.py                  
└── README.md                 
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Poetry package manager

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/freddie-mac-downloader.git
   cd freddie-mac-downloader
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Create a `.env` file with your Freddie Mac credentials:
   ```
   FREDDIE_MAC_USERNAME=your_username
   FREDDIE_MAC_PASSWORD=your_password
   ```

## 💻 Usage

### Basic Usage

Download data for a specific time range:

```bash
python main.py --start-year 2023 --end-year 2024 --start-qtr 1 --end-qtr 2 --verbose
```

### All Options

```bash
python main.py --help
```

Output:
```
usage: main.py [-h] --start-year START_YEAR --end-year END_YEAR
               [--start-qtr {1,2,3,4}] [--end-qtr {1,2,3,4}]
               [--remove-unzipped] [--verbose]

Download and consolidate Freddie Mac loan data.

optional arguments:
  -h, --help            show this help message and exit
  --start-year START_YEAR
                        Start year of data to download
  --end-year END_YEAR   End year of data to download
  --start-qtr {1,2,3,4}
                        Start quarter (default: 1)
  --end-qtr {1,2,3,4}   End quarter (default: 4)
  --remove-unzipped     Delete raw TXT files after processing
  --verbose             Enable verbose logging
```

## 📊 Output Data

After running the tool, you'll find:

1. `data/combined_dataset/` - Contains the final consolidated CSV files:
   - `combined_origination_data.csv` - All loan origination records
   - `combined_performance_data.csv` - All loan performance records

2. (Optional) `data/raw_dataset/` - Contains the extracted raw text files if `--remove-unzipped` is not specified

## 📚 About the Data

This tool downloads the Freddie Mac Single-Family Loan-Level Dataset, which contains:

- **Origination data**: Loan and property characteristics at origination
- **Performance data**: Monthly loan performance records

For more information about the dataset structure, visit [Freddie Mac's website](https://www.freddiemac.com/research/datasets/sf-loanlevel-dataset).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.