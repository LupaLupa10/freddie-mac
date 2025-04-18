# 📊 Freddie Mac 

A Python tool to download, extract, and consolidate Freddie Mac Single-Family Loan-Level Datasets — designed for researchers, analysts, and engineers working with mortgage data.
B

## 🔧 Features

- ✅ Authenticates via `.env` credentials
- ✅ Downloads quarterly loan ZIP files from Freddie Mac
- ✅ Extracts and merges `orig` (origination) and `svcg` (performance) data
- ✅ Outputs clean, consolidated CSVs
- ✅ CLI + YAML config support
- ✅ Modular, testable design using `@dataclass`
- ✅ Poetry-based for reproducible environments
- ✅ Data Analysis (WIP)
- ✅ Bayesian Model (WIP)
- ✅ Report (WIP)

## 📁 Project Structure

```
├── configs/
├── core_utils/
│   ├── arg_parser.py  
│   ├── constants.py    
│   └── config_loader.py   
├── data/
│   ├── freddie_mac_data.py  
│   ├── data_analysis.py  
│   ├── combined_dataset/    
│   └── raw_dataset/
│   └── plots/
├── report/
│   ├── report.html  
│   ├── report.py                        
├── templates/
│   ├── report.html.j2
├── .env                             
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
   git clone https://github.com/LupaLupa10/freddie-mac.git
   cd freddie-mac
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

### Data

To download data for a specific time range, use either command-line flags:
```bash
python main.py --start-year 2023 --end-year 2024 --start-qtr 1 --end-qtr 2 --verbose
```

Or using a YAML config:
```bash
python3 main.py --config configs/freddie_mac.yaml
```

### View Report

To view the HTML report generated via Jinja:

Run a local server:
```bash
python -m http.server
```

Open in your browser: 
```bash
http://localhost:8000/report/report.html
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

for commercial use of data, you need to contact freddie mac 