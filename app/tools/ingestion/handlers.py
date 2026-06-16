import pandas as pd
from fpdf import FPDF
from docx import Document
import os

class FileIngestor:
    @staticmethod
    def read_file(filepath: str):
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".csv":
            return pd.read_csv(filepath)
        elif ext in [".xls", ".xlsx"]:
            return pd.read_excel(filepath)
        elif ext == ".json":
            return pd.read_json(filepath)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

class ReportGenerator:
    @staticmethod
    def create_pdf(content: str, filename: str):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=content)
        pdf.output(filename)

ingestor = FileIngestor()
reporter = ReportGenerator()
