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

class Project(BaseModel):
    name: str | None = None
    description: str | None = None
    tools: list[str] = []


class CVData(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    education: list[Education]
    experience: list[Experience]
    projects: list[Experience]
    skills: list[str]
    awards_and_certificates: list[str] = []
    interests: list[str]


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

    items: list[InvoiceItem]

    subtotal: float | None = None
    tax_rate: float | None = None
    total_amount: float | None = None



class ReceiptItem(BaseModel):
    description: str
    quantity: float | None = None
    unit_price: float | None = None
    total_price: float | None = None


class ReceiptData(BaseModel):
    merchant: str | None = None
    merchant_address: str | None = None

    customer: str | None = None
    customer_address: str | None = None

    date: str | None = None
    receipt_number: str | None = None
    currency: str | None = None

    items: list[ReceiptItem]

    subtotal: float | None = None
    tax: float | None = None
    total: float | None = None

    amount_paid: float | None = None
    payment_method: str | None = None

    refund_amount: float | None = None
    refund_date: str | None = None



class PurchaseOrderItem(BaseModel):
    product_code: str | None = None
    description: str
    quantity: float | None = None
    unit: str | None = None
    unit_price: float | None = None
    tax_rate: float | None = None
    total_price: float | None = None


class PurchaseOrderData(BaseModel):
    po_number: str | None = None
    po_date: str | None = None

    supplier: str | None = None
    supplier_address: str | None = None

    buyer: str | None = None
    billing_address: str | None = None
    shipping_address: str | None = None

    currency: str | None = None
    payment_terms: str | None = None

    items: list[PurchaseOrderItem]

    subtotal: float | None = None
    tax: float | None = None
    total: float | None = None


class ContractData(BaseModel):
    contract_type: str | None = None

    party_a: str | None = None
    party_b: str | None = None

    effective_date: str | None = None
    end_date: str | None = None

    subject: str | None = None
    payment_terms: str | None = None
    termination_terms: str | None = None

    governing_law: str | None = None

    key_obligations: list[str]

    signed_by: list[str]

class BankTransaction(BaseModel):
    date: str | None = None
    description: str
    withdrawal: float | None = None
    deposit: float | None = None
    balance: float | None = None


class BankStatementData(BaseModel):
    bank_name: str | None = None

    account_holder: str | None = None
    account_number: str | None = None
    account_type: str | None = None

    statement_start_date: str | None = None
    statement_end_date: str | None = None
    currency: str | None = None

    opening_balance: float | None = None
    total_money_in: float | None = None
    total_money_out: float | None = None

    transactions: list[BankTransaction]

    closing_balance: float | None = None


SCHEMA_MAP = {
    "cv": CVData,
    "invoice": InvoiceData,
    "receipt": ReceiptData,
    "purchase order": PurchaseOrderData,
    "contract": ContractData,
    "bank statement": BankStatementData,
}