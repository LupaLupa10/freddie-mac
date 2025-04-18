import os
import zipfile
import csv
import requests
from threading import Thread
from dataclasses import dataclass
from core_utils.constants import LOGIN_URL, DOWNLOAD_A_URL, DOWNLOAD_Q_URL, ORIG_HEADERS, SVCG_HEADERS


@dataclass
class DataConfig:
    username: str
    password: str
    start_year: int
    end_year: int
    start_qtr: int
    end_qtr: int
    frequency: str = "quarterly"
    base_dir: str = "data"
    raw_dir: str = "raw_dataset"
    combined_dir: str = "combined_dataset"
    remove_unzipped: bool = False
    verbose: bool = True


class FreddieMacData:
    def __init__(self, config: DataConfig):
        self.config = config
        self.extract_dir = os.path.join(config.base_dir, config.raw_dir)
        self.download_dir = os.path.join(config.base_dir, config.combined_dir)

    def log(self, message):
        if self.config.verbose:
            print(message)

    def setup_directories(self):
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.extract_dir, exist_ok=True)
        self.log(f"Directories ready: {self.download_dir}, {self.extract_dir}")

    def authenticate(self, session):
        self.log("Authenticating...")
        payload = {
            "username": self.config.username,
            "password": self.config.password,
            "action": "authenticate"
        }
        response = session.post(LOGIN_URL, data=payload)
        if "Invalid username/password" in response.text:
            raise ValueError("Login failed: Invalid username/password")

        download_url = DOWNLOAD_Q_URL if self.config.frequency == "quarterly" else DOWNLOAD_A_URL
        session.post(download_url, data={"accept": "Yes", "action": "acceptTandC", "acceptSubmit": "Continue"})
        self.log(f"Authenticated and terms accepted via {download_url}")

    def download_and_extract(self, year, quarter, session):
        if self.config.frequency == "annual":
            zip_filename = f"historical_data_{year}.zip"
        else:
            if quarter is None:
                self.log(f"Missing quarter for quarterly download of year {year}")
                return
            zip_filename = f"historical_data_{year}Q{quarter}.zip"

        zip_path = os.path.join(self.download_dir, zip_filename)
        url = f"https://freddiemac.embs.com/FLoan/Data/{zip_filename}"

        try:
            self.log(f"Downloading: {url}")
            response = session.get(url, stream=True)
            response.raise_for_status()

            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

            self.log(f"Downloaded: {zip_path}")

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(self.extract_dir)
            self.log(f"Extracted to: {self.extract_dir}")
            os.remove(zip_path)

            if self.config.frequency == "annual":
                for file in os.listdir(self.extract_dir):
                    if file.endswith(".zip"):
                        inner_zip_path = os.path.join(self.extract_dir, file)
                        self.log(f"🔁 Extracting inner ZIP: {inner_zip_path}")
                        with zipfile.ZipFile(inner_zip_path, "r") as inner_zip:
                            inner_zip.extractall(self.extract_dir)
                        os.remove(inner_zip_path)

            self.log(f"Final contents: {os.listdir(self.extract_dir)}")

        except Exception as e:
            self.log(f"Error downloading/extracting {zip_filename}: {e}")

    def consolidate_files(self, file_type: str):
        headers = ORIG_HEADERS if file_type == "orig" else SVCG_HEADERS
        output_file = os.path.join(self.download_dir, f"consolidated_{file_type}.csv")

        if file_type == "orig":
            files_to_merge = [
                f for f in os.listdir(self.extract_dir)
                if f.endswith(".txt") and "time" not in f.lower()
            ]
        else:  
            files_to_merge = [
                f for f in os.listdir(self.extract_dir)
                if f.endswith(".txt") and "time" in f.lower()
            ]

        if not files_to_merge:
            self.log(f"No files to consolidate for type: {file_type}")
            return

        self.log(f"Found {len(files_to_merge)} files to consolidate for '{file_type}':")
        for f in sorted(files_to_merge):
            self.log(f"   - {f}")

        with open(output_file, "w", newline="") as out_csv:
            writer = csv.writer(out_csv)
            writer.writerow(headers)

            for file in sorted(files_to_merge):
                file_path = os.path.join(self.extract_dir, file)
                self.log(f"Processing: {file_path}")
                with open(file_path, "r") as f:
                    for line in f:
                        row = line.strip().split("|")
                        writer.writerow(row)

                if self.config.remove_unzipped:
                    os.remove(file_path)
                    self.log(f"Removed: {file_path}")

        self.log(f"Consolidated CSV saved to: {output_file}")

    def run(self):
        self.setup_directories()
        with requests.Session() as session:
            self.authenticate(session)
            threads = []

            for year in range(self.config.start_year, self.config.end_year + 1):
                if self.config.frequency == "annual":
                    t = Thread(target=self.download_and_extract, args=(year, None, session))
                    threads.append(t)
                    t.start()
                else:
                    for quarter in range(self.config.start_qtr, self.config.end_qtr + 1):
                        t = Thread(target=self.download_and_extract, args=(year, quarter, session))
                        threads.append(t)
                        t.start()

            for t in threads:
                t.join()

            self.log("All downloads complete. Starting consolidation...")
            self.consolidate_files("orig")
            self.consolidate_files("svcg")
            self.log("All tasks complete.")
