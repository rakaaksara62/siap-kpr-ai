import re
from pypdf import PdfReader


def redact_sensitive_info(text: str) -> str:
    """Menyensor nomor rekening atau identitas numerik (10-16 digit) sebelum diproses AI."""
    return re.sub(r'\b\d{10,16}\b', '[NO_REK_DISENSOR]', text)


def extract_text_from_file(uploaded_file) -> str:
    """Mengekstrak teks mentah dari file PDF atau CSV yang diunggah."""
    if uploaded_file.name.endswith('.pdf'):
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
        return text
    return uploaded_file.getvalue().decode("utf-8")