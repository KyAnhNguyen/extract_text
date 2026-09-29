import re


class MetadataService:

    @staticmethod
    def extract(text: str):

        metadata = {}

        invoice = re.search(r'INV\d+', text)

        if invoice:
            metadata["invoice_number"] = invoice.group()

            amount = re.search(r'(\d+\s*USD)', text)

        if amount:
            metadata["amount"] = amount.group()

        return metadata