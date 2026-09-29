from pathlib import Path

from app.extractors.pdf_extractor import PdfExtractor
from app.extractors.image_extractor import ImageExtractor
from app.extractors.txt_extractor import TxtExtractor
from app.extractors.md_extractor import MdExtractor
from app.extractors.csv_extractor import CsvExtractor
from app.extractors.excel_extractor import ExcelExtractor

from app.services.metadata_service import MetadataService
from app.services.classifier_service import ClassifierService
from app.services.chunk_service import ChunkService


class ExtractionPipeline:

    def process(self, file_path: str):
    
        ext = Path(file_path).suffix.lower()
        
        if ext == ".pdf":
            raw_text = PdfExtractor.extract(file_path)
        
        elif ext in [".jpg", ".jpeg", ".png", ".tiff"]:
            raw_text = ImageExtractor.extract(file_path, language="all")

        elif ext == ".txt":
            raw_text = TxtExtractor.extract(file_path)

        elif ext in [".md", ".markdown"]:
            raw_text = MdExtractor.extract(file_path)

        elif ext == ".csv":
            raw_text = CsvExtractor.extract(file_path)

        elif ext in [".xlsx", ".xlsm", ".xltx", ".xltm"]:
            raw_text = ExcelExtractor.extract(file_path)
        
        else:
            raise Exception("Unsupported file")
        
        # metadata = MetadataService.extract(raw_text)
        
        # document_type = ClassifierService.classify(raw_text)
        
        chunks = ChunkService.split_text(raw_text)
        
        return {
            "file_name": Path(file_path).name,
            # "document_type": document_type,
            # "metadata": metadata,
            "raw_text": raw_text,
            "chunks": chunks
        }