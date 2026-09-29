import pymupdf


class PdfExtractor:

    @staticmethod
    def extract(file_path: str) -> str:
        with pymupdf.open(file_path) as pdf:
            return "\n\n".join(
                page.get_text("text")
                for page in pdf
            )