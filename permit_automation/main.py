import os
import platform

# Add Poppler path only if running on Windows
if platform.system() == "Windows":
    os.environ["PATH"] += os.pathsep + r"C:\Release-23.08.0-0\poppler-23.08.0\Library\bin"

from utils.google_sheet import get_permit_ids, update_sheet_link
from utils.web_scraper import download_pdfs
from utils.pdf_extractor import extract_contact_info
from utils.excel_writer import write_to_excel
from utils.drive_uploader import upload_to_drive

def main():
    print("🚀 Starting permit automation process...")

    # Step 1: Get permit IDs from Google Sheet
    permit_rows = get_permit_ids()
    if not permit_rows:
        print("❌ No permit IDs found in Google Sheet.")
        return

    all_data = []

    # Step 2: Loop over each permit ID
    for permit_id, row_index in permit_rows:
        print(f"\n🔍 Processing permit ID: {permit_id}")

        try:
            pdfs = download_pdfs(permit_id)
            for i, pdf_path in enumerate(pdfs):
                print(f"📄 Extracting info from PDF: {pdf_path}")
                try:
                    contact_info = extract_contact_info(pdf_path)
                    contact_info["permit_id"] = f"{permit_id}_{i}"
                    all_data.append(contact_info)
                except Exception as extract_err:
                    print(f"⚠️ Failed to extract info from {pdf_path}: {extract_err}")

        except Exception as fetch_err:
            print(f"⚠️ Error downloading PDF for permit ID {permit_id}: {fetch_err}")

    # Step 3: If data was extracted, write to Excel
    if all_data:
        print("\n✅ Writing extracted data to Excel...")
        xlsx_path = write_to_excel(all_data)

        print("📤 Uploading Excel to Google Drive...")
        drive_link = upload_to_drive(xlsx_path)

        print("🔗 Updating Google Sheet with link...")
        update_sheet_link(2, drive_link)

        print("\n🎉 Process complete! Excel uploaded and linked.")
    else:
        print("⚠️ No data extracted from any PDF.")

if __name__ == "__main__":
    main()
