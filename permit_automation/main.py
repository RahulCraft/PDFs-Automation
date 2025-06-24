import os

# Add Poppler path for Windows
os.environ["PATH"] += os.pathsep + r"C:\Release-23.08.0-0\poppler-23.08.0\Library\bin"

from utils.google_sheet import get_permit_ids, update_sheet_link
from utils.web_scraper import download_pdfs
from utils.pdf_extractor import extract_contact_info
from utils.excel_writer import write_to_excel
from utils.drive_uploader import upload_to_drive

def main():
    permit_rows = get_permit_ids()
    all_data = []

    for permit_id, row in permit_rows:
        try:
            pdfs = download_pdfs(permit_id)
            for i, pdf in enumerate(pdfs):
                try:
                    info = extract_contact_info(pdf)
                    info["permit_id"] = f"{permit_id}_{i}"
                    all_data.append(info)
                except Exception as e:
                    print(f"Error extracting from {pdf}: {e}")
        except Exception as e:
            print(f"Error processing {permit_id}: {e}")

    if all_data:
        xlsx_path = write_to_excel(all_data)
        drive_link = upload_to_drive(xlsx_path)
        update_sheet_link(2, drive_link)
    else:
        print("No data was extracted.")

if __name__ == "__main__":
    main()