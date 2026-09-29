from app.extractors.txt_extractor import TxtExtractor


class MdExtractor:

    @staticmethod
    def extract(file_path: str) -> str:
        return TxtExtractor.extract(file_path)
