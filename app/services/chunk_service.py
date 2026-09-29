class ChunkService:

    @staticmethod
    def split_text(
        text: str,
        chunk_size: int = 1000
    ):

        chunks = []

        start = 0
        index = 1

        while start < len(text):

            chunk = text[start:start + chunk_size]

            chunks.append({
            "chunk_id": index,
            "content": chunk
            })

            start += chunk_size
            index += 1

        return chunks