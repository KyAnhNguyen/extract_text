from openpyxl import load_workbook


class ExcelExtractor:

    @staticmethod
    def extract(file_path: str) -> str:
        workbook = load_workbook(
            filename=file_path,
            read_only=True,
            data_only=True
        )
        sections = []

        try:
            for worksheet in workbook.worksheets:
                rows = []

                for row in worksheet.iter_rows(values_only=True):
                    values = [
                        "" if value is None else str(value).strip()
                        for value in row
                    ]

                    while values and not values[-1]:
                        values.pop()

                    if values:
                        rows.append("\t".join(values))

                if rows:
                    sections.append(
                        f"[Sheet: {worksheet.title}]\n" + "\n".join(rows)
                    )
        finally:
            workbook.close()

        return "\n\n".join(sections)
