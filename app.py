import os
from flask import Flask, render_template, request
from utils.web_scraper import download_pdfs_from_drive_link
from utils.pdf_extractor import extract_contact_info
from utils.excel_writer import write_to_excel
from utils.drive_uploader import upload_to_drive

app = Flask(__name__)

# Route to accept Google Drive PDF link and extract details
@app.route("/", methods=["GET", "POST"])
def upload_drive_link():
    if request.method == "POST":
        drive_link = request.form.get("drive_link")
        try:
            # Download PDF from Drive
            pdf_paths = download_pdfs_from_drive_link(drive_link)
            results = []

            for path in pdf_paths:
                # Extract info from each PDF
                info = extract_contact_info(path)
                info["permit_id"] = "manual_input"
                results.append(info)

            # Write to Excel
            xlsx_path = write_to_excel(results)

            # Upload Excel to Google Drive
            drive_url = upload_to_drive(xlsx_path)

            # Show results page
            return render_template("result.html", results=results, drive_link=drive_url)
        except Exception as e:
            return render_template("index.html", error=str(e))
    return render_template("index.html")

# Main app runner
if __name__ == "__main__":
    # Add Poppler path (used only in local dev; not needed in Render if Poppler is installed globally)
    poppler_path = r"C:\Release-23.08.0-0\poppler-23.08.0\Library\bin"
    if os.name == 'nt' and os.path.exists(poppler_path):
        os.environ["PATH"] += os.pathsep + poppler_path

    port = int(os.environ.get("PORT", 5000))  # Render requires binding to PORT
    app.run(host='0.0.0.0', port=port, debug=True)
