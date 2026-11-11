
from io import BytesIO

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class DocumentProcessor:

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )

    def process_pdf(self, file_bytes: bytes, filename: str):

        # Step 1: Read PDF
        reader = PdfReader(BytesIO(file_bytes))

        documents = []

        # Step 2: Extract text page by page
        for page_number, page in enumerate(reader.pages, start=1):

            text = page.extract_text()

            if not text or not text.strip():
                continue

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": filename,
                        "page": page_number
                    }
                )
            )

        if not documents:
            raise ValueError(
                "No extractable text found in this PDF."
            )

        # Step 3: Split text into chunks
        chunks = self.text_splitter.split_documents(
            documents
        )

        return chunks
