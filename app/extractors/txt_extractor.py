from pathlib import Path


class TxtExtractor:

    @staticmethod
    def extract(file_path: str) -> str:
        path = Path(file_path)

        try:
            return path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            return path.read_text(encoding="latin-1")
