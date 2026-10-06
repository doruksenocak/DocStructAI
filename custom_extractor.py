from pydantic import create_model


def create_custom_schema(fields: list[str]):
    field_definitions = {
        field: (str | None, None)
        for field in fields
    }

    return create_model(
        "CustomDocumentData",
        **field_definitions
    )