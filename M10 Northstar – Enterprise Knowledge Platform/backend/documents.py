from io import BytesIO
from pathlib import Path

import pandas as pd
from docx import Document as WordDocument
from langchain_core.documents import Document
from pypdf import PdfReader


def extract_documents(filename: str, content: bytes) -> list[Document]:
    suffix = Path(filename).suffix.lower()

    if suffix == ".pdf":
        pages = [
            Document(page_content=page.extract_text() or "", metadata={"page": page_number})
            for page_number, page in enumerate(PdfReader(BytesIO(content)).pages, start=1)
        ]
    elif suffix == ".docx":
        word_doc = WordDocument(BytesIO(content))
        parts = [paragraph.text for paragraph in word_doc.paragraphs if paragraph.text.strip()]
        parts.extend(
            " | ".join(cell.text.strip() for cell in row.cells)
            for table in word_doc.tables
            for row in table.rows
        )
        pages = [Document(page_content="\n".join(parts))]
    elif suffix in {".xlsx", ".xlsm"}:
        sheets = pd.read_excel(BytesIO(content), sheet_name=None, engine="openpyxl")
        pages = [
            Document(page_content=dataframe.to_string(index=False), metadata={"sheet": sheet_name})
            for sheet_name, dataframe in sheets.items()
            if not dataframe.empty
        ]
    elif suffix == ".csv":
        dataframe = pd.read_csv(BytesIO(content))
        pages = [Document(page_content=dataframe.to_string(index=False))] if not dataframe.empty else []
    elif suffix in {".txt", ".md"}:
        text = content.decode("utf-8-sig").strip()
        pages = [Document(page_content=text)] if text else []
    else:
        raise ValueError("Supported formats are PDF, DOCX, XLSX, XLSM, CSV, TXT, and Markdown.")

    pages = [page for page in pages if page.page_content.strip()]
    if not pages:
        raise ValueError("No readable text was found in this file.")
    return pages
