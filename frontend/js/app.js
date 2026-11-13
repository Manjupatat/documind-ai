
// Get search elements
const searchForm = document.getElementById("search-form");
const searchInput = document.getElementById("search-input");
const searchResults = document.getElementById("search-results");

// Initialize application tabs
function initializeTabs() {
    const tabs = document.querySelectorAll(".tab");

    tabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            tabs.forEach(item => item.classList.remove("active"));

            document.querySelectorAll(".panel").forEach(panel => {
                panel.classList.remove("active");
            });

            tab.classList.add("active");

            const selectedPanel = document.getElementById(
                `${tab.dataset.tab}-panel`
            );

            if (selectedPanel) {
                selectedPanel.classList.add("active");
            }
        });
    });
}

// Check backend connection
async function checkBackend() {
    const status = document.getElementById("backend-status");

    try {
        await API.checkHealth();

        status.textContent = "● Backend connected";
        status.className = "backend-online";

    } catch (error) {
        status.textContent = "● Backend unavailable";
        status.className = "backend-offline";

        console.error("Backend health check failed:", error);
    }
}

// Perform semantic search
async function performSearch(event) {
    event.preventDefault();

    const query = searchInput.value.trim();

    if (query.length < 3) {
        searchResults.textContent =
            "Please enter at least 3 characters.";
        return;
    }

    const button = searchForm.querySelector("button");

    button.disabled = true;
    button.textContent = "Searching...";

    searchResults.textContent = "Searching documents...";

    try {
        const documentId =
            document.getElementById("document-filter").value || null;

        const result = await API.search(query, documentId, 3);

        searchResults.replaceChildren();

        if (!result.results || result.results.length === 0) {
            searchResults.textContent = "No relevant passages found.";
            return;
        }

        result.results.forEach((item, index) => {
            const card = document.createElement("article");
            card.className = "search-result";

            const heading = document.createElement("h3");
            heading.textContent = `Result ${index + 1}`;

            const metadata = document.createElement("p");
            metadata.className = "result-metadata";

            const page = item.page;

            metadata.textContent =
                `${item.source || "Document"} · ${
                    page !== undefined && page !== null
                        ? `Page ${Number(page) + 1}`
                        : "Page unavailable"
                }`;

            const content = document.createElement("p");
            content.textContent = item.content || "";

            card.append(heading, metadata, content);
            searchResults.appendChild(card);
        });

    } catch (error) {
        searchResults.textContent = `Search failed: ${error.message}`;
        console.error("Search error:", error);

    } finally {
        button.disabled = false;
        button.textContent = "Search";
    }
}

// Initialize all frontend features
document.addEventListener("DOMContentLoaded", () => {
    console.log("DocuMind AI frontend initializing...");

    initializeTabs();
    initializeDocuments();
    initializeChat();

    searchForm.addEventListener("submit", performSearch);

    checkBackend();

    console.log("DocuMind AI frontend initialized successfully.");
});
