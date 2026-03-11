from pypdf import PdfReader
from pypdf.errors import PdfStreamError


def read_pdf(file_path: str) -> str:
    text = ""

    try:
        reader = PdfReader(file_path)

        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                return ""

        for page in reader.pages:
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            except Exception:
                continue

    except PdfStreamError:
        return ""

    except Exception:
        return ""

    return text.strip()
