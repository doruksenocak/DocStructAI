from enum import Enum
import re

from pydantic import BaseModel

from models import CVData, InvoiceData, ReceiptData, PurchaseOrderData, ContractData, BankStatementData

class ValidationSeverity(str, Enum):
    WARNING = "warning"
    ERROR = "error"


class ValidationIssue(BaseModel):
    field: str | None = None
    message: str
    severity: ValidationSeverity


class ValidationResult(BaseModel):
    is_valid: bool
    issues: list[ValidationIssue]

    @property
    def errors(self):
        return [
            issue for issue in self.issues
            if issue.severity == ValidationSeverity.ERROR
        ]

    @property
    def warnings(self):
        return [
            issue for issue in self.issues
            if issue.severity == ValidationSeverity.WARNING
        ]


def validate_cv(cv: CVData) -> ValidationResult:
    issues = []

    # 1. Name
    if not cv.name.strip():
        issues.append(
            ValidationIssue(
                field="name",
                message="Extracted name is empty.",
                severity=ValidationSeverity.WARNING
            )
        )

    # 2. Email
    if cv.email is not None:
        email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        if not re.match(email_pattern, cv.email.strip()):
            issues.append(
                ValidationIssue(
                    field="email",
                    message=f"Extracted email has a suspicious format: {cv.email}",
                    severity=ValidationSeverity.WARNING
                )
            )

    # 3. Phone
    if cv.phone is not None:
        digits = re.sub(r"\D", "", cv.phone)

        if len(digits) < 7 or len(digits) > 15:
            issues.append(
                ValidationIssue(
                    field="phone",
                    message=f"Extracted phone number has a suspicious format: {cv.phone}",
                    severity=ValidationSeverity.WARNING
                )
            )

    # 4. Education
    for index, education in enumerate(cv.education):
        if not education.institution.strip():
            issues.append(
                ValidationIssue(
                    field=f"education[{index}].institution",
                    message="Extracted education entry has an empty institution.",
                    severity=ValidationSeverity.WARNING
                )
            )

        if not education.degree.strip():
            issues.append(
                ValidationIssue(
                    field=f"education[{index}].degree",
                    message="Extracted education entry has an empty degree.",
                    severity=ValidationSeverity.WARNING
                )
            )

    # 5. Experience
    for index, experience in enumerate(cv.experience):
        if not experience.company.strip():
            issues.append(
                ValidationIssue(
                    field=f"experience[{index}].company",
                    message="Extracted experience entry has an empty company.",
                    severity=ValidationSeverity.WARNING
                )
            )

        if not experience.position.strip():
            issues.append(
                ValidationIssue(
                    field=f"experience[{index}].position",
                    message="Extracted experience entry has an empty position.",
                    severity=ValidationSeverity.WARNING
                )
            )

    # 6. Skills - empty entries
    for index, skill in enumerate(cv.skills):
        if not skill.strip():
            issues.append(
                ValidationIssue(
                    field=f"skills[{index}]",
                    message="Extracted skill is empty.",
                    severity=ValidationSeverity.WARNING
                )
            )

    # 7. Skills - duplicates
    normalized_skills = [
        skill.strip().lower()
        for skill in cv.skills
        if skill.strip()
    ]

    if len(normalized_skills) != len(set(normalized_skills)):
        issues.append(
            ValidationIssue(
                field="skills",
                message="Duplicate skills were extracted.",
                severity=ValidationSeverity.WARNING
            )
        )

    # Determine whether any strong validation errors were found
    has_errors = any(
        issue.severity == ValidationSeverity.ERROR
        for issue in issues
    )

    return ValidationResult(
        is_valid=not has_errors,
        issues=issues
    )

def validate_invoice(invoice: InvoiceData) -> ValidationResult:
    issues = []

    tolerance = 0.01

    # 1. Validate individual line items
    for index, item in enumerate(invoice.items):

        if item.quantity is not None and item.quantity < 0:
            issues.append(
                ValidationIssue(
                    field=f"items[{index}].quantity",
                    message=f"Negative quantity extracted: {item.quantity}",
                    severity=ValidationSeverity.WARNING
                )
            )

        if item.unit_price is not None and item.unit_price < 0:
            issues.append(
                ValidationIssue(
                    field=f"items[{index}].unit_price",
                    message=f"Negative unit price extracted: {item.unit_price}",
                    severity=ValidationSeverity.WARNING
                )
            )

        # Check: quantity × unit price = line total
        if (
            item.quantity is not None
            and item.unit_price is not None
            and item.total_price is not None
        ):
            expected_total = item.quantity * item.unit_price

            if abs(expected_total - item.total_price) > tolerance:
                issues.append(
                    ValidationIssue(
                        field=f"items[{index}].total_price",
                        message=(
                            f"Line item is inconsistent: "
                            f"{item.quantity} × {item.unit_price} "
                            f"= {expected_total:.2f}, "
                            f"but extracted total is {item.total_price:.2f}."
                        ),
                        severity=ValidationSeverity.ERROR
                    )
                )

    # 2. Check: sum of line totals = subtotal
    line_totals = [
        item.total_price
        for item in invoice.items
        if item.total_price is not None
    ]

    all_items_have_totals = (
        len(invoice.items) > 0
        and len(line_totals) == len(invoice.items)
    )

    if all_items_have_totals and invoice.subtotal is not None:
        calculated_subtotal = sum(line_totals)

        if abs(calculated_subtotal - invoice.subtotal) > tolerance:
            issues.append(
                ValidationIssue(
                    field="subtotal",
                    message=(
                        f"Subtotal is inconsistent: line items sum to "
                        f"{calculated_subtotal:.2f}, but extracted subtotal "
                        f"is {invoice.subtotal:.2f}."
                    ),
                    severity=ValidationSeverity.ERROR
                )
            )

    # 3. Check for missing total amount when it can be inferred
    if (
        invoice.total_amount is None
        and invoice.subtotal is not None
        and invoice.tax_rate is not None
    ):
        expected_total = invoice.subtotal * (1 + invoice.tax_rate / 100)

        issues.append(
            ValidationIssue(
                field="total_amount",
                message=(
                    f"Total amount was not extracted, but subtotal and tax rate "
                    f"suggest an expected total of {expected_total:.2f}."
                ),
                severity=ValidationSeverity.WARNING
            )
        )

    # 4. Check total amount when it was extracted
    if (
        invoice.total_amount is not None
        and invoice.subtotal is not None
        and invoice.tax_rate is not None
    ):
        expected_total = invoice.subtotal * (1 + invoice.tax_rate / 100)

        if abs(expected_total - invoice.total_amount) > tolerance:
            issues.append(
                ValidationIssue(
                    field="total_amount",
                    message=(
                        f"Total amount is inconsistent: subtotal and tax rate "
                        f"suggest {expected_total:.2f}, but extracted total "
                        f"is {invoice.total_amount:.2f}."
                    ),
                    severity=ValidationSeverity.ERROR
                )
            )

    # 5. Determine overall validation status
    has_errors = any(
        issue.severity == ValidationSeverity.ERROR
        for issue in issues
    )

    return ValidationResult(
        is_valid=not has_errors,
        issues=issues
    )

def validate_receipt(receipt: ReceiptData) -> ValidationResult:
    issues = []

    tolerance = 0.01

    # 1. Validate individual receipt items
    for index, item in enumerate(receipt.items):

        # Negative quantities are suspicious but can occur in returns
        if item.quantity is not None and item.quantity < 0:
            issues.append(
                ValidationIssue(
                    field=f"items[{index}].quantity",
                    message=f"Negative quantity extracted: {item.quantity}",
                    severity=ValidationSeverity.WARNING
                )
            )

        # Negative prices are suspicious but not automatically wrong
        if item.unit_price is not None and item.unit_price < 0:
            issues.append(
                ValidationIssue(
                    field=f"items[{index}].unit_price",
                    message=f"Negative unit price extracted: {item.unit_price}",
                    severity=ValidationSeverity.WARNING
                )
            )

        # Check: quantity × unit price = item total
        if (
            item.quantity is not None
            and item.unit_price is not None
            and item.total_price is not None
        ):
            expected_total = item.quantity * item.unit_price

            if abs(expected_total - item.total_price) > tolerance:
                issues.append(
                    ValidationIssue(
                        field=f"items[{index}].total_price",
                        message=(
                            f"Receipt item is inconsistent: "
                            f"{item.quantity} × {item.unit_price} "
                            f"= {expected_total:.2f}, "
                            f"but extracted total is {item.total_price:.2f}."
                        ),
                        severity=ValidationSeverity.ERROR
                    )
                )

    # 2. Check: sum of item totals = subtotal
    item_totals = [
        item.total_price
        for item in receipt.items
        if item.total_price is not None
    ]

    all_items_have_totals = (
        len(receipt.items) > 0
        and len(item_totals) == len(receipt.items)
    )

    if all_items_have_totals and receipt.subtotal is not None:
        calculated_subtotal = sum(item_totals)

        if abs(calculated_subtotal - receipt.subtotal) > tolerance:
            issues.append(
                ValidationIssue(
                    field="subtotal",
                    message=(
                        f"Subtotal is inconsistent: receipt items sum to "
                        f"{calculated_subtotal:.2f}, but extracted subtotal "
                        f"is {receipt.subtotal:.2f}."
                    ),
                    severity=ValidationSeverity.ERROR
                )
            )

    # 3. Check: subtotal + tax = total
    if (
        receipt.subtotal is not None
        and receipt.tax is not None
        and receipt.total is not None
    ):
        expected_total = receipt.subtotal + receipt.tax

        if abs(expected_total - receipt.total) > tolerance:
            issues.append(
                ValidationIssue(
                    field="total",
                    message=(
                        f"Total is inconsistent: subtotal + tax gives "
                        f"{expected_total:.2f}, but extracted total "
                        f"is {receipt.total:.2f}."
                    ),
                    severity=ValidationSeverity.ERROR
                )
            )

    # 4. Total is missing even though subtotal and tax allow us to infer it
    if (
        receipt.total is None
        and receipt.subtotal is not None
        and receipt.tax is not None
    ):
        expected_total = receipt.subtotal + receipt.tax

        issues.append(
            ValidationIssue(
                field="total",
                message=(
                    f"Total was not extracted, but subtotal and tax "
                    f"suggest an expected total of {expected_total:.2f}."
                ),
                severity=ValidationSeverity.WARNING
            )
        )

    # 5. Compare amount paid with total
    # A mismatch is only a warning because partial/split payments can exist.
    if (
        receipt.amount_paid is not None
        and receipt.total is not None
        and abs(receipt.amount_paid - receipt.total) > tolerance
    ):
        issues.append(
            ValidationIssue(
                field="amount_paid",
                message=(
                    f"Amount paid ({receipt.amount_paid:.2f}) differs from "
                    f"the receipt total ({receipt.total:.2f})."
                ),
                severity=ValidationSeverity.WARNING
            )
        )

    # 6. Refund amount exists but refund date is missing
    if receipt.refund_amount is not None and receipt.refund_date is None:
        issues.append(
            ValidationIssue(
                field="refund_date",
                message=(
                    "A refund amount was extracted, but no refund date "
                    "was extracted."
                ),
                severity=ValidationSeverity.WARNING
            )
        )

    # 7. Refund date exists but refund amount is missing
    if receipt.refund_date is not None and receipt.refund_amount is None:
        issues.append(
            ValidationIssue(
                field="refund_amount",
                message=(
                    "A refund date was extracted, but no refund amount "
                    "was extracted."
                ),
                severity=ValidationSeverity.WARNING
            )
        )

    # 8. Suspicious negative refund
    if receipt.refund_amount is not None and receipt.refund_amount < 0:
        issues.append(
            ValidationIssue(
                field="refund_amount",
                message=(
                    f"Negative refund amount extracted: "
                    f"{receipt.refund_amount}"
                ),
                severity=ValidationSeverity.WARNING
            )
        )

    # 9. Refund larger than original total
    if (
        receipt.refund_amount is not None
        and receipt.total is not None
        and receipt.refund_amount > receipt.total + tolerance
    ):
        issues.append(
            ValidationIssue(
                field="refund_amount",
                message=(
                    f"Refund amount ({receipt.refund_amount:.2f}) is larger "
                    f"than the original receipt total ({receipt.total:.2f})."
                ),
                severity=ValidationSeverity.WARNING
            )
        )

    # 10. Determine overall validation status
    has_errors = any(
        issue.severity == ValidationSeverity.ERROR
        for issue in issues
    )

    return ValidationResult(
        is_valid=not has_errors,
        issues=issues
    )

def validate_purchase_order(po: PurchaseOrderData) -> ValidationResult:

    issues = []

    tolerance = 0.01

    # 1. Validate individual purchase order items
    for index, item in enumerate(po.items):

        # Negative quantity is suspicious
        if item.quantity is not None and item.quantity < 0:
            issues.append(
                ValidationIssue(
                    field=f"items[{index}].quantity",
                    message=f"Negative quantity extracted: {item.quantity}",
                    severity=ValidationSeverity.WARNING
                )
            )

        # Negative unit price is suspicious
        if item.unit_price is not None and item.unit_price < 0:
            issues.append(
                ValidationIssue(
                    field=f"items[{index}].unit_price",
                    message=f"Negative unit price extracted: {item.unit_price}",
                    severity=ValidationSeverity.WARNING
                )
            )

        # Suspicious tax rate
        if item.tax_rate is not None and (
            item.tax_rate < 0 or item.tax_rate > 100
        ):
            issues.append(
                ValidationIssue(
                    field=f"items[{index}].tax_rate",
                    message=f"Suspicious tax rate extracted: {item.tax_rate}%",
                    severity=ValidationSeverity.WARNING
                )
            )

        # Check: quantity × unit price = line total
        #
        # We currently assume total_price means the line total BEFORE tax.
        if (
            item.quantity is not None
            and item.unit_price is not None
            and item.total_price is not None
        ):
            expected_total = item.quantity * item.unit_price

            if abs(expected_total - item.total_price) > tolerance:
                issues.append(
                    ValidationIssue(
                        field=f"items[{index}].total_price",
                        message=(
                            f"Purchase order item is inconsistent: "
                            f"{item.quantity} × {item.unit_price} "
                            f"= {expected_total:.2f}, "
                            f"but extracted total is {item.total_price:.2f}."
                        ),
                        severity=ValidationSeverity.ERROR
                    )
                )

    # 2. Check: sum of line totals = subtotal
    item_totals = [
        item.total_price
        for item in po.items
        if item.total_price is not None
    ]

    all_items_have_totals = (
        len(po.items) > 0
        and len(item_totals) == len(po.items)
    )

    if all_items_have_totals and po.subtotal is not None:
        calculated_subtotal = sum(item_totals)

        if abs(calculated_subtotal - po.subtotal) > tolerance:
            issues.append(
                ValidationIssue(
                    field="subtotal",
                    message=(
                        f"Subtotal is inconsistent: purchase order items "
                        f"sum to {calculated_subtotal:.2f}, but extracted "
                        f"subtotal is {po.subtotal:.2f}."
                    ),
                    severity=ValidationSeverity.ERROR
                )
            )

    # 3. Check: subtotal + tax = total
    if (
        po.subtotal is not None
        and po.tax is not None
        and po.total is not None
    ):
        expected_total = po.subtotal + po.tax

        if abs(expected_total - po.total) > tolerance:
            issues.append(
                ValidationIssue(
                    field="total",
                    message=(
                        f"Total is inconsistent: subtotal + tax gives "
                        f"{expected_total:.2f}, but extracted total "
                        f"is {po.total:.2f}."
                    ),
                    severity=ValidationSeverity.ERROR
                )
            )

    # 4. Total missing although subtotal and tax are available
    if (
        po.total is None
        and po.subtotal is not None
        and po.tax is not None
    ):
        expected_total = po.subtotal + po.tax

        issues.append(
            ValidationIssue(
                field="total",
                message=(
                    f"Total was not extracted, but subtotal and tax "
                    f"suggest an expected total of {expected_total:.2f}."
                ),
                severity=ValidationSeverity.WARNING
            )
        )

    # 5. Check whether item tax rates agree with the extracted tax amount
    #
    # Only do this when every item contains all information required
    # for calculating its tax.
    items_with_tax_information = [
        item
        for item in po.items
        if (
            item.total_price is not None
            and item.tax_rate is not None
        )
    ]

    all_items_have_tax_information = (
        len(po.items) > 0
        and len(items_with_tax_information) == len(po.items)
    )

    if all_items_have_tax_information and po.tax is not None:
        calculated_tax = sum(
            item.total_price * (item.tax_rate / 100)
            for item in po.items
        )

        if abs(calculated_tax - po.tax) > tolerance:
            issues.append(
                ValidationIssue(
                    field="tax",
                    message=(
                        f"Tax may be inconsistent: item tax rates suggest "
                        f"{calculated_tax:.2f}, but extracted tax is "
                        f"{po.tax:.2f}."
                    ),
                    severity=ValidationSeverity.WARNING
                )
            )

    # 6. Determine overall validation status
    has_errors = any(
        issue.severity == ValidationSeverity.ERROR
        for issue in issues
    )

    return ValidationResult(
        is_valid=not has_errors,
        issues=issues
    )

def validate_contract(contract: ContractData) -> ValidationResult:
    issues = []

    # 1. Party A is present but empty
    if contract.party_a is not None and not contract.party_a.strip():
        issues.append(
            ValidationIssue(
                field="party_a",
                message="Party A was extracted as an empty value.",
                severity=ValidationSeverity.WARNING
            )
        )

    # 2. Party B is present but empty
    if contract.party_b is not None and not contract.party_b.strip():
        issues.append(
            ValidationIssue(
                field="party_b",
                message="Party B was extracted as an empty value.",
                severity=ValidationSeverity.WARNING
            )
        )

    # 3. Same party extracted on both sides
    if (
        contract.party_a is not None
        and contract.party_b is not None
        and contract.party_a.strip()
        and contract.party_b.strip()
        and contract.party_a.strip().lower()
        == contract.party_b.strip().lower()
    ):
        issues.append(
            ValidationIssue(
                field="party_b",
                message=(
                    "The same party was extracted as both "
                    "Party A and Party B."
                ),
                severity=ValidationSeverity.WARNING
            )
        )

    # 4. Subject is present but empty
    if contract.subject is not None and not contract.subject.strip():
        issues.append(
            ValidationIssue(
                field="subject",
                message="Contract subject was extracted as an empty value.",
                severity=ValidationSeverity.WARNING
            )
        )

    # 5. Empty key obligations
    for index, obligation in enumerate(contract.key_obligations):
        if not obligation.strip():
            issues.append(
                ValidationIssue(
                    field=f"key_obligations[{index}]",
                    message="An empty key obligation was extracted.",
                    severity=ValidationSeverity.WARNING
                )
            )

    # 6. Duplicate key obligations
    normalized_obligations = [
        obligation.strip().lower()
        for obligation in contract.key_obligations
        if obligation.strip()
    ]

    if len(normalized_obligations) != len(set(normalized_obligations)):
        issues.append(
            ValidationIssue(
                field="key_obligations",
                message="Duplicate key obligations were extracted.",
                severity=ValidationSeverity.WARNING
            )
        )

    # 7. No signers extracted
    if not contract.signed_by:
        issues.append(
            ValidationIssue(
                field="signed_by",
                message="No signers were extracted from the contract.",
                severity=ValidationSeverity.WARNING
            )
        )

    # 8. Empty signer entries
    for index, signer in enumerate(contract.signed_by):
        if not signer.strip():
            issues.append(
                ValidationIssue(
                    field=f"signed_by[{index}]",
                    message="An empty signer was extracted.",
                    severity=ValidationSeverity.WARNING
                )
            )

    # 9. Duplicate signers
    normalized_signers = [
        signer.strip().lower()
        for signer in contract.signed_by
        if signer.strip()
    ]

    if len(normalized_signers) != len(set(normalized_signers)):
        issues.append(
            ValidationIssue(
                field="signed_by",
                message="Duplicate signers were extracted.",
                severity=ValidationSeverity.WARNING
            )
        )

    # 10. Signature information exists but no parties were extracted
    if (
        len(normalized_signers) > 0
        and contract.party_a is None
        and contract.party_b is None
    ):
        issues.append(
            ValidationIssue(
                field="signed_by",
                message=(
                    "Signer information was extracted, but no contract "
                    "parties were extracted."
                ),
                severity=ValidationSeverity.WARNING
            )
        )

    # 11. Determine overall validation status
    has_errors = any(
        issue.severity == ValidationSeverity.ERROR
        for issue in issues
    )

    return ValidationResult(
        is_valid=not has_errors,
        issues=issues
    )

def validate_bank_statement(
    statement: BankStatementData
) -> ValidationResult:
    issues = []

    tolerance = 0.01

    # 1. Validate individual transactions
    for index, transaction in enumerate(statement.transactions):

        # Empty transaction description
        if not transaction.description.strip():
            issues.append(
                ValidationIssue(
                    field=f"transactions[{index}].description",
                    message="Transaction description is empty.",
                    severity=ValidationSeverity.WARNING
                )
            )

        # Negative withdrawal
        if (
            transaction.withdrawal is not None
            and transaction.withdrawal < 0
        ):
            issues.append(
                ValidationIssue(
                    field=f"transactions[{index}].withdrawal",
                    message=(
                        f"Negative withdrawal extracted: "
                        f"{transaction.withdrawal}"
                    ),
                    severity=ValidationSeverity.WARNING
                )
            )

        # Negative deposit
        if (
            transaction.deposit is not None
            and transaction.deposit < 0
        ):
            issues.append(
                ValidationIssue(
                    field=f"transactions[{index}].deposit",
                    message=(
                        f"Negative deposit extracted: "
                        f"{transaction.deposit}"
                    ),
                    severity=ValidationSeverity.WARNING
                )
            )

        # Both withdrawal and deposit are present
        if (
            transaction.withdrawal is not None
            and transaction.deposit is not None
        ):
            issues.append(
                ValidationIssue(
                    field=f"transactions[{index}]",
                    message=(
                        "Both a withdrawal and a deposit were extracted "
                        "for the same transaction."
                    ),
                    severity=ValidationSeverity.WARNING
                )
            )

        # Neither withdrawal nor deposit is present
        if (
            transaction.withdrawal is None
            and transaction.deposit is None
        ):
            issues.append(
                ValidationIssue(
                    field=f"transactions[{index}]",
                    message=(
                        "Transaction has neither a withdrawal nor a deposit."
                    ),
                    severity=ValidationSeverity.WARNING
                )
            )

    # 2. Validate running balances
    #
    # Formula:
    # previous balance + deposit - withdrawal = current balance

    previous_balance = statement.opening_balance

    for index, transaction in enumerate(statement.transactions):

        if previous_balance is not None and transaction.balance is not None:

            deposit = (
                transaction.deposit
                if transaction.deposit is not None
                else 0.0
            )

            withdrawal = (
                transaction.withdrawal
                if transaction.withdrawal is not None
                else 0.0
            )

            expected_balance = (
                previous_balance
                + deposit
                - withdrawal
            )

            if abs(expected_balance - transaction.balance) > tolerance:
                issues.append(
                    ValidationIssue(
                        field=f"transactions[{index}].balance",
                        message=(
                            f"Running balance is inconsistent: previous "
                            f"balance {previous_balance:.2f} "
                            f"+ deposit {deposit:.2f} "
                            f"- withdrawal {withdrawal:.2f} "
                            f"= {expected_balance:.2f}, "
                            f"but extracted balance is "
                            f"{transaction.balance:.2f}."
                        ),
                        severity=ValidationSeverity.ERROR
                    )
                )

        # Continue from the balance printed for this transaction.
        #
        # We intentionally use the extracted balance instead of our
        # calculated balance so one bad transaction does not cause
        # every later transaction to be marked as wrong.
        if transaction.balance is not None:
            previous_balance = transaction.balance
        else:
            previous_balance = None

    # 3. Check total money in
    deposits = [
        transaction.deposit
        for transaction in statement.transactions
        if transaction.deposit is not None
    ]

    if statement.total_money_in is not None:
        calculated_money_in = sum(deposits)

        if abs(calculated_money_in - statement.total_money_in) > tolerance:
            issues.append(
                ValidationIssue(
                    field="total_money_in",
                    message=(
                        f"Total money in is inconsistent: extracted "
                        f"transactions contain {calculated_money_in:.2f} "
                        f"in deposits, but statement total is "
                        f"{statement.total_money_in:.2f}."
                    ),
                    severity=ValidationSeverity.ERROR
                )
            )

    # 4. Check total money out
    withdrawals = [
        transaction.withdrawal
        for transaction in statement.transactions
        if transaction.withdrawal is not None
    ]

    if statement.total_money_out is not None:
        calculated_money_out = sum(withdrawals)

        if abs(calculated_money_out - statement.total_money_out) > tolerance:
            issues.append(
                ValidationIssue(
                    field="total_money_out",
                    message=(
                        f"Total money out is inconsistent: extracted "
                        f"transactions contain {calculated_money_out:.2f} "
                        f"in withdrawals, but statement total is "
                        f"{statement.total_money_out:.2f}."
                    ),
                    severity=ValidationSeverity.ERROR
                )
            )

    # 5. Check last transaction balance against closing balance
    if statement.transactions and statement.closing_balance is not None:
        last_balance = statement.transactions[-1].balance

        if (
            last_balance is not None
            and abs(last_balance - statement.closing_balance) > tolerance
        ):
            issues.append(
                ValidationIssue(
                    field="closing_balance",
                    message=(
                        f"Closing balance is inconsistent: last transaction "
                        f"balance is {last_balance:.2f}, but extracted closing "
                        f"balance is {statement.closing_balance:.2f}."
                    ),
                    severity=ValidationSeverity.ERROR
                )
            )

    # 6. Check overall statement balance
    #
    # opening balance + money in - money out = closing balance
    if (
        statement.opening_balance is not None
        and statement.total_money_in is not None
        and statement.total_money_out is not None
        and statement.closing_balance is not None
    ):
        expected_closing_balance = (
            statement.opening_balance
            + statement.total_money_in
            - statement.total_money_out
        )

        if (
            abs(
                expected_closing_balance
                - statement.closing_balance
            )
            > tolerance
        ):
            issues.append(
                ValidationIssue(
                    field="closing_balance",
                    message=(
                        f"Statement totals are inconsistent: opening balance "
                        f"{statement.opening_balance:.2f} "
                        f"+ money in {statement.total_money_in:.2f} "
                        f"- money out {statement.total_money_out:.2f} "
                        f"= {expected_closing_balance:.2f}, "
                        f"but extracted closing balance is "
                        f"{statement.closing_balance:.2f}."
                    ),
                    severity=ValidationSeverity.ERROR
                )
            )

    # 7. Determine overall validation status
    has_errors = any(
        issue.severity == ValidationSeverity.ERROR
        for issue in issues
    )

    return ValidationResult(
        is_valid=not has_errors,
        issues=issues
    )