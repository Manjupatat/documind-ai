
const API_BASE_URL = "";

async function apiRequest(endpoint, options = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

    let data;

    try {
        data = await response.json();
    } catch {
        data = {};
    }

    if (!response.ok) {
        const detail = data.detail;

        const message =
            typeof detail === "string"
                ? detail
                : detail?.message || "Something went wrong.";

        throw new Error(message);
    }

    return data;
}

const API = {
    checkHealth() {
        return apiRequest("/health");
    },

    uploadDocument(file) {
        const formData = new FormData();
        formData.append("file", file);

        return apiRequest("/api/documents/upload", {
            method: "POST",
            body: formData
        });
    },

    getDocuments() {
        return apiRequest("/api/documents/");
    },

    deleteDocument(documentId) {
        return apiRequest(`/api/documents/${encodeURIComponent(documentId)}`, {
            method: "DELETE"
        });
    },

    chat(question, documentId = null, topK = 3) {
        return apiRequest("/api/documents/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question,
                document_id: documentId,
                top_k: topK
            })
        });
    },

    search(query, documentId = null, topK = 3) {
        const params = new URLSearchParams({
            query,
            top_k: topK
        });

        if (documentId) {
            params.append("document_id", documentId);
        }

        return apiRequest(`/api/documents/search?${params}`);
    }
};