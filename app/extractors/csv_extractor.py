import csv


class CsvExtractor:

    @staticmethod
    def extract(file_path: str) -> str:
        rows = []

        with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
            sample = file.read(4096)
            file.seek(0)

            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = csv.excel

            reader = csv.reader(file, dialect)
            for row in reader:
                rows.append("\t".join(cell.strip() for cell in row))

        return "\n".join(rows)
