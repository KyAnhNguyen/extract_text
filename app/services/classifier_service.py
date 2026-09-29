class ClassifierService:

        @staticmethod
        def classify(text: str):

            lower = text.lower()

            if "invoice" in lower:
                return "invoice"

            if "contract" in lower:
                return "contract"

            if "resume" in lower:
                return "resume"

            return "unknown"