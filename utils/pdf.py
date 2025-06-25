from PyPDF2 import PdfReader
from datetime import datetime

def extract_pdf_metadata(path):
    reader = PdfReader(path)
    info = reader.metadata
    created = None
    if info.creation_date:
        try:
            s = info.creation_date
            if s.startswith("D:"):
                s = s[2:]
            created = datetime.strptime(s[:14], "%Y%m%d%H%M%S")
        except Exception:
            created = None
    return {
        'title': info.title or None,
        'author': info.author or None,
        'created_at': created
    }