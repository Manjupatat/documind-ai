const chatForm = document.getElementById("chat-form");
const questionInput = document.getElementById("question-input");
const chatMessages = document.getElementById("chat-messages");
const sendButton = document.getElementById("send-btn");


function appendMessage(role, content, sources = []) {
  const message = document.createElement("div");
  message.className = `message ${role}`;

  const text = document.createElement("div");
  text.className = "message-content";
  text.textContent = content;
  message.appendChild(text);

  if (role === "assistant" && sources.length > 0) {
    const sourceContainer = document.createElement("div");
    sourceContainer.className = "source-container";

    const heading = document.createElement("strong");
    heading.textContent = "Sources";
    sourceContainer.appendChild(heading);

    sources.forEach((source, index) => {
      const sourceCard = document.createElement("div");
      sourceCard.className = "source-card";

      if (typeof source === "string") {
        sourceCard.textContent = source;
      } else {
        const filename =
          source.source || source.filename || source.file_name || "Document";

        const page = source.page ?? source.page_number;

        const sourceName = document.createElement("strong");
        sourceName.textContent = `[${index + 1}] ${filename}`;

        const pageText = document.createElement("span");
        pageText.textContent =
          page !== undefined && page !== null
            ? ` — Page ${Number(page) + 1}`
            : "";

        sourceCard.append(sourceName, pageText);

        if (source.content) {
          const excerpt = document.createElement("p");
          excerpt.textContent = source.content;
          sourceCard.appendChild(excerpt);
        }
      }

      sourceContainer.appendChild(sourceCard);
    });

    message.appendChild(sourceContainer);
  }

  chatMessages.appendChild(message);

  // Scroll only the chat messages container, not the entire page.
  requestAnimationFrame(() => {
    chatMessages.scrollTo({
      top: chatMessages.scrollHeight,
      behavior: "smooth"
    });
  });

  return message;
}


function showTypingIndicator() {
  const indicator = document.createElement("div");
  indicator.className = "message assistant thinking-card";
  indicator.id = "typing-indicator";

  const animation = document.createElement("div");
  animation.className = "thinking-animation";
  animation.innerHTML = `
        <span class="thinking-emoji">🧠</span>
        <div class="thinking-text">
            <strong>DocuMind AI</strong>
            <p id="thinking-status">Reading your documents...</p>
        </div>
    `;

  const dots = document.createElement("div");
  dots.className = "thinking-dots";
  dots.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;

  indicator.append(animation, dots);
  chatMessages.appendChild(indicator);

  chatMessages.scrollTop = chatMessages.scrollHeight;

  const messages = [
    "Reading your documents...",
    "Finding relevant passages...",
    "Understanding the context...",
    "Checking relevant information...",
    "Preparing your answer...",
  ];

  let index = 0;

  const interval = setInterval(() => {
    index = (index + 1) % messages.length;

    const status = document.getElementById("thinking-status");

    if (status) {
      status.textContent = messages[index];
    }
  }, 2200);

  // Return a cleanup function to stop the animation.
  return function stopThinking() {
    clearInterval(interval);
    indicator.remove();
  };
}

async function sendQuestion(event) {
  event.preventDefault();

  const question = questionInput.value.trim();

  if (question.length < 3) {
    return;
  }

  appendMessage("user", question);

  questionInput.value = "";
  sendButton.disabled = true;
  sendButton.textContent = "Thinking...";

  const stopThinking = showTypingIndicator();

  try {
    const documentId = document.getElementById("document-filter").value || null;

    const result = await API.chat(question, documentId, 3);

    stopThinking();

    appendMessage(
      "assistant",
      result.answer || "No answer was returned.",
      result.sources || [],
    );
  } catch (error) {
    stopThinking();

    appendMessage(
      "assistant",
      `Sorry, I couldn't process your question: ${error.message}`,
    );
  } finally {
    sendButton.disabled = false;
    sendButton.textContent = "Send";
    questionInput.focus();
  }
}

function initializeChat() {
  chatForm.addEventListener("submit", sendQuestion);
}
