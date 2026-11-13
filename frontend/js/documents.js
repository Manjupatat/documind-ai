
const documentList = document.getElementById("document-list");
const documentFilter = document.getElementById("document-filter");
const uploadButton = document.getElementById("upload-btn");
const pdfInput = document.getElementById("pdf-input");
const uploadStatus = document.getElementById("upload-status");

async function loadDocuments() {
    try {
        const response = await API.getDocuments();
        const documents = response.documents || [];

        renderDocuments(documents);
        renderDocumentFilter(documents);

    } catch (error) {
        documentList.textContent = "Unable to load documents: " + error.message;
        documentList.classList.add("error-text");
    }
}

function renderDocuments(documents) {
    documentList.replaceChildren();

    if (documents.length === 0) {
        const empty = document.createElement("p");
        empty.className = "muted";
        empty.textContent = "No documents uploaded yet.";
        documentList.appendChild(empty);
        return;
    }

    documents.forEach((doc) => {
        const item = document.createElement("div");
        item.className = "document-item";

        const name = document.createElement("p");
        name.className = "document-name";
        name.textContent = doc.filename || "Untitled PDF";

        const details = document.createElement("p");
        details.className = "document-details";
        details.textContent = `${doc.total_chunks ?? 0} chunks`;

        const actions = document.createElement("div");
        actions.className = "document-actions";

        const selectButton = document.createElement("button");
        selectButton.className = "select-document-btn";
        selectButton.textContent = "Use document";
        selectButton.addEventListener("click", () => {
            documentFilter.value = doc.document_id;
            documentFilter.dispatchEvent(new Event("change"));
        });

        const deleteButton = document.createElement("button");
        deleteButton.className = "delete-document-btn";
        deleteButton.textContent = "Delete";
        deleteButton.addEventListener("click", () => {
            deleteDocument(doc.document_id, doc.filename);
        });

        actions.append(selectButton, deleteButton);
        item.append(name, details, actions);
        documentList.appendChild(item);
    });
}

function renderDocumentFilter(documents) {
    const currentSelection = documentFilter.value;

    documentFilter.replaceChildren();

    const allOption = document.createElement("option");
    allOption.value = "";
    allOption.textContent = "All documents";
    documentFilter.appendChild(allOption);

    documents.forEach((doc) => {
        const option = document.createElement("option");
        option.value = doc.document_id;
        option.textContent = doc.filename || "Untitled PDF";
        documentFilter.appendChild(option);
    });

    const selectionStillExists = documents.some(
        doc => doc.document_id === currentSelection
    );

    documentFilter.value = selectionStillExists ? currentSelection : "";
}

async function uploadDocument() {
    const file = pdfInput.files[0];

    if (!file) {
        showUploadStatus("Please select a PDF first.", "error");
        return;
    }

    if (!file.name.toLowerCase().endsWith(".pdf")) {
        showUploadStatus("Only PDF files are supported.", "error");
        return;
    }

    if (file.size === 0) {
        showUploadStatus("The selected file is empty.", "error");
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        showUploadStatus("File size must be 10 MB or less.", "error");
        return;
    }

    uploadButton.disabled = true;
    uploadButton.textContent = "Uploading...";
    showUploadStatus("Uploading and indexing your PDF...", "loading");

    try {
        const result = await API.uploadDocument(file);

        showUploadStatus(
            `${result.filename} uploaded successfully! ${result.total_chunks} chunks indexed.`,
            "success"
        );

        pdfInput.value = "";
        await loadDocuments();

        // Automatically select the newly uploaded document.
        if (result.document_id) {
            documentFilter.value = result.document_id;
            documentFilter.dispatchEvent(new Event("change"));
        }

    } catch (error) {
        showUploadStatus(error.message, "error");
    } finally {
        uploadButton.disabled = false;
        uploadButton.textContent = "Upload PDF";
    }
}

function showUploadStatus(message, type) {
    uploadStatus.textContent = message;
    uploadStatus.className = `status-message ${type}`;
}

async function deleteDocument(documentId, filename) {
    const confirmed = window.confirm(
        `Are you sure you want to delete "${filename}"?`
    );

    if (!confirmed) return;

    try {
        await API.deleteDocument(documentId);

        if (documentFilter.value === documentId) {
            documentFilter.value = "";
            documentFilter.dispatchEvent(new Event("change"));
        }

        await loadDocuments();

    } catch (error) {
        window.alert("Unable to delete document: " + error.message);
    }
}

function initializeDocuments() {
    uploadButton.addEventListener("click", uploadDocument);
    loadDocuments();
}