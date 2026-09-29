from fastapi import FastAPI

from app.api.document_api import router as document_router
from app.extractors.image_extractor import ImageExtractor
from app.extractors.pdf_extractor import PdfExtractor
from app.pipelines.extraction_pipeline import ExtractionPipeline

app = FastAPI()
app.include_router(document_router)

# test = ImageExtractor.extract(str("./uploads/Slide1.jpg"));

# test = ExtractionPipeline().process(str("./uploads/Slide3.png"));

# print(test);

@app.get("/")
def health_check():
    return {"status": "ok"}