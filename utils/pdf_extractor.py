from pdf2image import convert_from_path
import pytesseract
import re

def extract_contact_info(pdf_path):
    # Convert PDF pages to images
    images = convert_from_path(pdf_path)

    # Extract text from each image
    text = "\n".join(pytesseract.image_to_string(img) for img in images)

    # Helper function: extract text after label (even if on same line)
    def extract_field_after_label(label, full_text):
        # Match: Label followed by any character(s) on the same line
        pattern = rf"{label}\s*[:\-]?\s*(.+)"
        match = re.search(pattern, full_text, re.IGNORECASE)
        return match.group(1).strip().title() if match else None

    # Helper function: find email near label
    def extract_email_near_label(label, full_text):
        label_index = full_text.lower().find(label.lower())
        if label_index == -1:
            return None
        snippet = full_text[label_index : label_index + 300]
        match = re.search(r"([\w\.-]+@[\w\.-]+)", snippet)
        return match.group(1).strip() if match else None

    # Extract names/emails from official and local contact sections
    official_name = extract_field_after_label("Official Contact Person Name", text)
    official_email = extract_email_near_label("Official Contact Person Name", text)

    local_name = extract_field_after_label("Local Contact Person Name", text)
    local_email = extract_email_near_label("Local Contact Person Name", text)

    contacts = []
    if official_name and official_email:
        contacts.append((official_name, official_email))
    if local_name and local_email:
        contacts.append((local_name, local_email))

    # Fallback: up to 3 names + emails from whole text
    fallback_contacts = re.findall(
        r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)+).*?([\w\.-]+@[\w\.-]+)',
        text, re.DOTALL
    )
    for contact in fallback_contacts:
        if contact not in contacts:
            contacts.append(contact)
        if len(contacts) >= 3:
            break

    # Try to extract Company Name or Owner
    company_match = re.search(r'(Company Name|Owner):?\s*(.+)', text, re.IGNORECASE)
    if not company_match:
        company_match = re.search(r'([A-Z][\w\.\s&,-]+(?:LLC|Inc|Ltd|Corporation|Services))', text)

    company = (
        company_match.group(2).strip() if company_match and company_match.lastindex == 2
        else company_match.group(1).strip() if company_match
        else "Unknown Company"
    )

    return {
        "company": company,
        "contacts": contacts[:3]
    }
