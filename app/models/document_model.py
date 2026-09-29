from pydantic import BaseModel


class Chunk(BaseModel):
    chunk_id: int
    content: str


class ExtractedDocument(BaseModel):
    file_name: str
    # document_type: str
    raw_text: str
    # metadata: dict
    chunks: list[Chunk]