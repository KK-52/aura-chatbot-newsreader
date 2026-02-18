// --- Constants & Selectors ---
const chatHistory = document.getElementById('chat-history');
const welcomeScreen = document.getElementById('welcome-screen');
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const sendBtn = document.getElementById('send-btn');
const urlInput = document.getElementById('urlInput');

// --- Session Management ---
// --- Session Management ---
let sessionId = localStorage.getItem('rag_session_id');
const loginModal = document.getElementById('login-modal');
const usernameInput = document.getElementById('username-input');

// Check if user is logged in
if (!sessionId) {
    showLoginModal();
} else {
    // Restore session
    console.log(`Restored Session ID: ${sessionId}`);
    updateProfileUI(sessionId);
}

function showLoginModal() {
    loginModal.classList.add('active');
    usernameInput.focus();
}

function handleLogin() {
    const rawUsername = usernameInput.value.trim();
    if (!rawUsername) return;

    // Create a consistent ID from username (or just use it directly)
    // For simplicity, we use the username as the session ID so it can be memorized/reused.
    sessionId = rawUsername.toLowerCase().replace(/\s+/g, '-');

    completeLogin(sessionId);
}

function handleGuestLogin() {
    // Generate random UUID for guest
    sessionId = crypto.randomUUID();
    completeLogin(sessionId);
}

function completeLogin(id) {
    localStorage.setItem('rag_session_id', id);
    loginModal.classList.remove('active');
    console.log(`Session Started: ${id}`);
    updateProfileUI(id);
}

function updateProfileUI(id) {
    const nameEl = document.querySelector('.user-info .name');
    const avatarEl = document.querySelector('.user-profile .avatar-sm');

    if (nameEl && avatarEl) {
        // Truncate if long UUID
        const displayName = id.length > 15 ? 'Guest' : id;
        nameEl.innerText = displayName;
        avatarEl.innerText = displayName.charAt(0).toUpperCase();
    }
}

// Allow Enter key in login
usernameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleLogin();
});

// --- Ingestion Logic ---
async function ingestUrl() {
    const url = urlInput.value.trim();

    if (!url) {
        logToSidebar('No URL provided');
        return;
    }

    // UI Updates
    showStatus('Indexing...');
    logToSidebar(`Indexing: ${url}`);

    try {
        const response = await fetch('/ingest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: url,
                session_id: sessionId
            })
        });

        const result = await response.json();

        if (response.ok) {
            logToSidebar('Success');
            addSourceToSidebar(url);
            hideStatus();
        } else {
            const errorMsg = result.detail || 'Unknown Error';
            logToSidebar(`Failed: ${errorMsg}`);
            showStatus(`Error: ${errorMsg}`, true);
        }
    } catch (error) {
        logToSidebar('Network Error');
        showStatus('Error', true);
    }
}

function handleIngestEnter(e) {
    if (e.key === 'Enter') ingestUrl();
}

function addSourceToSidebar(url) {
    const list = document.getElementById('source-list');
    const empty = list.querySelector('.empty-state-sidebar');
    if (empty) empty.remove();

    const item = document.createElement('div');
    item.className = 'source-item';
    const displayUrl = url.replace(/^https?:\/\//, '').replace(/^www\./, '').substring(0, 25);

    item.innerHTML = `
        <i class="fa-solid fa-globe"></i>
        <span>${displayUrl}</span>
    `;
    list.prepend(item);
}

function logToSidebar(msg) {
    console.log(`[System]: ${msg}`);
}

function showStatus(text, isError = false) {
    statusIndicator.className = 'status-mini'; // Reset
    statusText.innerText = text;
    statusText.style.color = isError ? '#ff6b6b' : 'var(--text-secondary)';
}

function hideStatus() {
    setTimeout(() => {
        statusIndicator.className = 'status-mini hidden';
    }, 2000);
}

// --- Chat Logic ---
function handleEnter(e) {
    if (e.key === 'Enter') sendQuery();
}

async function sendQuery() {
    const input = document.getElementById('user-query');
    const query = input.value.trim();
    if (!query) return;

    // Hide Welcome Screen on first message
    if (welcomeScreen) welcomeScreen.style.display = 'none';

    // Add User Message
    appendMessage(query, 'user');
    input.value = '';

    // Create placeholder for bot response
    const botMsgId = appendMessage('<div class="spinner-xs"></div>', 'bot');

    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                session_id: sessionId
            })
        });

        const result = await response.json();

        if (response.ok) {
            updateBotMessage(botMsgId, result.answer);
        } else {
            updateBotMessage(botMsgId, "**Error:** Failed to generate response.");
        }
    } catch (error) {
        updateBotMessage(botMsgId, "**Connection Error:** Could not reach the neural core.");
    }
}

// --- Message Rendering ---
function appendMessage(text, sender) {
    const div = document.createElement('div');
    div.className = 'message-row';
    const msgId = Date.now();
    div.dataset.id = msgId;

    const isBot = sender === 'bot';

    // Avatar
    const avatar = document.createElement('div');
    avatar.className = `message-avatar ${isBot ? 'bot-avatar' : 'user-avatar'}`;
    avatar.innerHTML = isBot ? '<i class="fa-solid fa-sparkles"></i>' : 'U';

    // Content
    const content = document.createElement('div');
    content.className = 'message-content';
    content.innerHTML = text; // Initial content

    div.appendChild(avatar);
    div.appendChild(content);

    chatHistory.appendChild(div);
    scrollToBottom();
    return msgId;
}

function updateBotMessage(id, text) {
    const msgRow = document.querySelector(`[data-id="${id}"]`);
    if (!msgRow) return;

    const contentDiv = msgRow.querySelector('.message-content');

    // Simple Markdown Parsing
    let html = text
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
        .replace(/\n/g, '<br>');

    contentDiv.innerHTML = html;

    // Re-highlight code blocks
    contentDiv.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });

    scrollToBottom();
}

function scrollToBottom() {
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Enable/Disable Send Button
document.getElementById('user-query').addEventListener('input', function (e) {
    sendBtn.disabled = e.target.value.trim() === '';
});
