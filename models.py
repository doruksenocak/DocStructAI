from pydantic import BaseModel


class Education(BaseModel):
    institution: str
    degree: str
    start_date: str | None = None
    end_date: str | None = None


class Experience(BaseModel):
    company: str
    position: str
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None


class CVData(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    education: list[Education]
    experience: list[Experience]
    skills: list[str]


class InvoiceItem(BaseModel):
    description: str
    quantity: float | None = None
    unit_price: float | None = None
    total_price: float | None = None


class InvoiceData(BaseModel):
    invoice_number: str | None = None
    vendor: str | None = None
    customer: str | None = None
    invoice_date: str | None = None
    due_date: str | None = None
    currency: str | None = None
    total_amount: float | None = None
    items: list[InvoiceItem]

SCHEMA_MAP = {
    "cv": CVData,
    "invoice": InvoiceData,
}