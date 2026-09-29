import cv2
import easyocr
import unicodedata
from typing import Any


class ImageExtractor:

    ALL_LANGUAGES = ("en", "vi", "ja", "ko", "ch")
    MIN_CONFIDENCE = 0.30

    READERS = {
        "en": easyocr.Reader(
            ['en'],
            gpu=False
        ),

        "vi": easyocr.Reader(
            ['en', 'vi'],
            gpu=False
        ),

        "ja": easyocr.Reader(
            ['ja', 'en'],
            gpu=False
        ),

        "ko": easyocr.Reader(
            ['ko', 'en'],
            gpu=False
        ),

        "ch": easyocr.Reader(
            ['ch_sim', 'en'],
            gpu=False
        )
    }

    @staticmethod
    def preprocess(file_path):

        image = cv2.imread(file_path)

        if image is None:
            raise Exception(
                f"Cannot read image: {file_path}"
            )

        return image

    @staticmethod
    def extract(
        file_path: str,
        language: str = "all"
    ) -> str:

        image = ImageExtractor.preprocess(
            file_path
        )

        languages = ImageExtractor.ALL_LANGUAGES if language == "all" else (language,)
        candidates: list[dict[str, Any]] = []

        for current_language in languages:
            reader = ImageExtractor.READERS.get(
                current_language,
                ImageExtractor.READERS["en"]
            )

            for bbox, text, confidence in reader.readtext(
                image,
                detail=1,
                paragraph=False
            ):
                if (
                    confidence > (
                        0.30
                        if ImageExtractor._is_symbol_only(text)
                        else 0.60
                        if current_language == "en"
                        else ImageExtractor.MIN_CONFIDENCE
                    )
                    and ImageExtractor._matches_language(text, current_language)
                ):
                    candidates.append({
                        "bbox": bbox,
                        "text": text,
                        "confidence": confidence,
                        "language": current_language
                    })

        symbol_candidates = [
            {
                **candidate,
                "text": ImageExtractor._normalize_symbols(candidate["text"])
            }
            for candidate in candidates
            if ImageExtractor._is_symbol_only(candidate["text"])
        ]
        candidates = [
            candidate
            for candidate in candidates
            if not ImageExtractor._is_symbol_only(candidate["text"])
        ]
        if symbol_candidates:
            candidates.append(max(symbol_candidates, key=lambda item: item["confidence"]))

        candidates = ImageExtractor._remove_transliterations(candidates)
        results = ImageExtractor._merge_results(candidates)
        texts = [result["text"] for result in results]

        return "\n".join(texts)

    @staticmethod
    def _matches_language(text: str, language: str) -> bool:
        if language == "vi":
            return any(character in "ăâđêôơưĂÂĐÊÔƠƯ" for character in text)

        if language == "ja":
            return sum(
                "\u3040" <= character <= "\u30ff"
                for character in text
            ) >= 2

        if language == "ko":
            return sum("\uac00" <= character <= "\ud7a3" for character in text) >= 2

        if language == "ch":
            return sum("\u4e00" <= character <= "\u9fff" for character in text) >= 2

        return any(
            character.isalpha()
            or character.isdigit()
            or not character.isalnum() and not character.isspace()
            for character in text
        )

    @staticmethod
    def _is_symbol_only(text: str) -> bool:
        return bool(text.strip()) and all(
            not character.isalnum() for character in text if not character.isspace()
        )

    @staticmethod
    def _normalize_symbols(text: str) -> str:
        compact = "".join(character for character in text if not character.isspace())
        if compact.startswith("#!"):
            compact = "@#" + compact[1:]
        return compact

    @staticmethod
    def _remove_transliterations(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        non_latin_texts = [
            candidate
            for candidate in candidates
            if candidate["language"] == "vi"
        ]

        return [
            candidate
            for candidate in candidates
            if not (
                candidate["language"] == "en"
                and any(
                    ImageExtractor._normalize_text(candidate["text"])
                    == ImageExtractor._normalize_text(other["text"])
                    for other in non_latin_texts
                )
            )
        ]

    @staticmethod
    def _normalize_text(text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text)
        return "".join(
            character
            for character in normalized
            if not unicodedata.combining(character)
        ).casefold().replace(" ", "")

    @staticmethod
    def _merge_results(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        merged: list[dict[str, Any]] = []

        for candidate in candidates:
            duplicate_index = next(
                (
                    index
                    for index, existing in enumerate(merged)
                    if existing["text"].casefold().strip()
                    == candidate["text"].casefold().strip()
                ),
                None
            )

            if duplicate_index is None:
                merged.append(candidate)
            elif candidate["confidence"] > merged[duplicate_index]["confidence"]:
                merged[duplicate_index] = candidate

        return sorted(
            merged,
            key=lambda result: (
                min(point[1] for point in result["bbox"]),
                min(point[0] for point in result["bbox"])
            )
        )

    @staticmethod
    def _boxes_overlap(first: list[list[float]], second: list[list[float]]) -> bool:
        first_x = [point[0] for point in first]
        first_y = [point[1] for point in first]
        second_x = [point[0] for point in second]
        second_y = [point[1] for point in second]

        horizontal_overlap = min(max(first_x), max(second_x)) - max(min(first_x), min(second_x))
        vertical_overlap = min(max(first_y), max(second_y)) - max(min(first_y), min(second_y))

        return horizontal_overlap > 0 and vertical_overlap > 0