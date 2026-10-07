import json
from pathlib import Path
from pydantic import BaseModel
import csv
from openpyxl import Workbook
from openpyxl.styles import Alignment

def export_to_json(data: BaseModel, output_path: str):
    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            data.model_dump(),
            file,
            indent=2,
            ensure_ascii=False
        )


def export_rows_to_csv(rows: list[BaseModel], output_path: str):
    if not rows:
        raise ValueError("Cannot export an empty list to CSV.")

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    data = [
        row.model_dump()
        for row in rows
    ]

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=data[0].keys()
        )

        writer.writeheader()
        writer.writerows(data)

def export_to_csv(data: BaseModel, output_dir: str, name: str):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    document = data.model_dump()

    metadata = {}

    for field_name, value in document.items():

        # Normal fields → metadata
        if not isinstance(value, list):
            metadata[field_name] = value
            continue

        # Empty list
        if not value:
            continue

        # List of objects → own CSV table
        if isinstance(value[0], dict):
            file_path = output_dir / f"{name}_{field_name}.csv"

            with file_path.open(
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.DictWriter(
                    file,
                    fieldnames=value[0].keys()
                )

                writer.writeheader()
                writer.writerows(value)

        # Simple list: skills, interests, signers, etc.
        else:
            file_path = output_dir / f"{name}_{field_name}.csv"

            with file_path.open(
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.writer(file)

                writer.writerow([field_name])

                for item in value:
                    writer.writerow([item])

    # Export normal document-level fields
    if metadata:
        file_path = output_dir / f"{name}_metadata.csv"

        with file_path.open(
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=metadata.keys()
            )

            writer.writeheader()
            writer.writerow(metadata)


def format_sheet(sheet):
    max_width = 50

    for column_cells in sheet.columns:
        longest_length = 0

        for cell in column_cells:
            cell.alignment = Alignment(
                wrap_text=True,
                vertical="top"
            )

            if cell.value is not None:
                longest_length = max(
                    longest_length,
                    len(str(cell.value))
                )

        column_letter = column_cells[0].column_letter

        sheet.column_dimensions[column_letter].width = min(
            longest_length + 2,
            max_width
        )

def export_to_excel(data: BaseModel, output_path: str):
    workbook = Workbook()

    metadata_sheet = workbook.active
    metadata_sheet.title = "Metadata"

    document = data.model_dump()

    for field_name, value in document.items():

        # Normal value → Metadata sheet
        if not isinstance(value, list):
            metadata_sheet.append([field_name, value])
            continue

        # Empty list → nothing to export
        if not value:
            continue

        # Create a new sheet for this list
        sheet = workbook.create_sheet(
            title=field_name.capitalize()
        )

        # List of objects
        if isinstance(value[0], dict):

            headers = list(value[0].keys())
            sheet.append(headers)

            for row in value:
                sheet.append([
                    row[header]
                    for header in headers
                ])

        # Simple list (skills, interests, obligations...)
        else:
            sheet.append([field_name])

            for item in value:
                sheet.append([item])

    for sheet in workbook.worksheets:
        format_sheet(sheet)

    workbook.save(output_path)