
import pytest

from app.services.document_processor import DocumentProcessor


class FakePage:
    """Simulates a PDF page."""

    def __init__(self, text):
        self.text = text

    def extract_text(self):
        return self.text


class FakePdfReader:
    """Simulates a PDF reader with multiple pages."""

    def __init__(self, pages):
        self.pages = pages


def test_extracts_text_and_preserves_page_metadata(monkeypatch):
    fake_pages = [
        FakePage("This is the first page of the document."),
        FakePage("   \n"),
        FakePage("This is the third page of the document.")
    ]

    monkeypatch.setattr(
        "app.services.document_processor.PdfReader",
        lambda file: FakePdfReader(fake_pages)
    )

    processor = DocumentProcessor()

    chunks = processor.process_pdf(
        file_bytes=b"fake pdf content",
        filename="sample.pdf"
    )

    assert len(chunks) == 2

    assert chunks[0].metadata["source"] == "sample.pdf"
    assert chunks[0].metadata["page"] == 1

    assert chunks[1].metadata["source"] == "sample.pdf"
    assert chunks[1].metadata["page"] == 3

    assert "first page" in chunks[0].page_content
    assert "third page" in chunks[1].page_content


def test_splits_long_text_into_chunks(monkeypatch):
    long_text = "word " * 300

    fake_pages = [FakePage(long_text)]

    monkeypatch.setattr(
        "app.services.document_processor.PdfReader",
        lambda file: FakePdfReader(fake_pages)
    )

    processor = DocumentProcessor()

    chunks = processor.process_pdf(
        file_bytes=b"fake pdf content",
        filename="long_document.pdf"
    )

    assert len(chunks) > 1

    for chunk in chunks:
        assert len(chunk.page_content) <= 500
        assert chunk.metadata["source"] == "long_document.pdf"
        assert chunk.metadata["page"] == 1


@pytest.mark.parametrize(
    "page_texts",
    [
        [],
        ["", "   ", "\n\n"]
    ]
)
def test_raises_error_when_pdf_has_no_extractable_text(
    monkeypatch,
    page_texts
):
    fake_pages = [FakePage(text) for text in page_texts]

    monkeypatch.setattr(
        "app.services.document_processor.PdfReader",
        lambda file: FakePdfReader(fake_pages)
    )

    processor = DocumentProcessor()

    with pytest.raises(
        ValueError,
        match="No extractable text found in this PDF."
    ):
        processor.process_pdf(
            file_bytes=b"fake pdf content",
            filename="empty.pdf"
        )
