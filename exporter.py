import json
from pathlib import Path
from pydantic import BaseModel


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