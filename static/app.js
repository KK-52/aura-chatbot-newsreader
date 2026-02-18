// --- Constants & Selectors ---
const chatHistory = document.getElementById('chat-history');
const welcomeScreen = document.getElementById('welcome-screen');
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const sendBtn = document.getElementById('send-btn');
const urlInput = document.getElementById('urlInput');

// --- Session Management ---
let authToken = localStorage.getItem('rag_auth_token');
let username = localStorage.getItem('rag_username');
let isRegisterMode = false;

const loginModal = document.getElementById('login-modal');
const usernameInput = document.getElementById('username-input');
const passwordInput = document.getElementById('password-input');
const loginBtn = document.getElementById('login-btn');
const toggleLink = document.getElementById('toggle-auth');

// Check if user is logged in
if (!authToken) {
    showLoginModal();
} else {
    // Restore session
    console.log(`Restored Session for: ${username}`);
    updateProfileUI(username);
    fetchUrls();
}

function showLoginModal() {
    loginModal.classList.add('active');
    usernameInput.focus();
}

function toggleAuthMode() {
    isRegisterMode = !isRegisterMode;
    if (isRegisterMode) {
        loginBtn.innerText = "Register";
        document.querySelector('.login-header h2').innerText = "Create Account";
        document.querySelector('.login-header p').innerText = "Sign up to start chatting";
        toggleLink.innerText = "Login";
    } else {
        loginBtn.innerText = "Login";
        document.querySelector('.login-header h2').innerText = "Welcome back";
        document.querySelector('.login-header p').innerText = "Enter your credentials to access your session";
        toggleLink.innerText = "Register";
    }
}

async function handleAuthAction() {
    const user = usernameInput.value.trim();
    const pass = passwordInput.value.trim();

    if (!user || !pass) {
        alert("Please enter both username and password.");
        return;
    }

    loginBtn.disabled = true;
    loginBtn.innerText = "Processing...";

    try {
        if (isRegisterMode) {
            await registerUser(user, pass);
        } else {
            await loginUser(user, pass);
        }
    } catch (error) {
        alert(error.message);
        loginBtn.disabled = false;
        loginBtn.innerText = isRegisterMode ? "Register" : "Login";
    }
}

async function loginUser(user, pass) {
    const formData = new URLSearchParams();
    formData.append('username', user);
    formData.append('password', pass);

    const response = await fetch('/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Login failed');

    setSession(user, data.access_token);
}

async function registerUser(user, pass) {
    const formData = new URLSearchParams();
    formData.append('username', user);
    formData.append('password', pass);

    const response = await fetch('/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Registration failed');

    setSession(user, data.access_token);
}

function setSession(user, token) {
    authToken = token;
    username = user;
    localStorage.setItem('rag_auth_token', token);
    localStorage.setItem('rag_username', user);

    loginModal.classList.remove('active');
    updateProfileUI(user);
    fetchUrls();
}

function handleGuestLogin() {
    // Generate random guest credentials
    const guestUser = `guest_${Math.random().toString(36).substr(2, 6)}`;
    const guestPass = "guest123";

    // We need to register this guest user first
    isRegisterMode = true;
    registerUser(guestUser, guestPass).catch(err => {
        // If already exists (rare), try login
        loginUser(guestUser, guestPass);
    });
}

function logout() {
    localStorage.removeItem('rag_auth_token');
    localStorage.removeItem('rag_username');
    location.reload();
}

function updateProfileUI(name) {
    const nameEl = document.querySelector('.user-info .name');
    const avatarEl = document.querySelector('.user-profile .avatar-sm');

    if (nameEl && avatarEl) {
        nameEl.innerText = name;
        avatarEl.innerText = name.charAt(0).toUpperCase();

        // Add logout handler to profile
        document.querySelector('.user-profile').onclick = () => {
            if (confirm("Log out?")) logout();
        };
    }
}

// Allow Enter key in login
passwordInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleAuthAction();
});

// --- Ingestion Logic ---
async function ingestUrl() {
    const url = urlInput.value.trim();
    if (!url) return;

    showStatus('Indexing...');
    logToSidebar(`Indexing: ${url}`);

    try {
        const response = await fetch('/ingest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ url: url })
        });

        const result = await response.json();

        if (response.ok) {
            logToSidebar('Success');
            addSourceToSidebar(url);
            hideStatus();
        } else {
            if (response.status === 401) { logout(); return; }
            const errorMsg = result.detail || 'Unknown Error';
            showStatus(`Error: ${errorMsg}`, true);
        }
    } catch (error) {
        showStatus('Network Error', true);
    }
}

async function fetchUrls() {
    try {
        const response = await fetch('/session/urls', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (response.ok) {
            const data = await response.json();
            const list = document.getElementById('source-list');
            list.innerHTML = ''; // Clear existing

            if (data.urls.length === 0) {
                list.innerHTML = '<div class="empty-state-sidebar">No sources added.</div>';
            } else {
                data.urls.forEach(url => addSourceToSidebar(url));
            }
        } else if (response.status === 401) {
            logout();
        }
    } catch (e) {
        console.error("Failed to fetch URLs", e);
    }
}

function handleIngestEnter(e) {
    if (e.key === 'Enter') ingestUrl();
}

function addSourceToSidebar(url) {
    const list = document.getElementById('source-list');
    const empty = list.querySelector('.empty-state-sidebar');
    if (empty) empty.remove();

    // Check if already exists
    const existing = Array.from(list.children).find(child => child.dataset.url === url);
    if (existing) return;

    const item = document.createElement('div');
    item.className = 'source-item';
    item.dataset.url = url;
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

    if (welcomeScreen) welcomeScreen.style.display = 'none';

    appendMessage(query, 'user');
    input.value = '';

    const botMsgId = appendMessage('<div class="spinner-xs"></div>', 'bot');

    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ query: query })
        });

        const result = await response.json();

        if (response.ok) {
            updateBotMessage(botMsgId, result.answer);
        } else {
            if (response.status === 401) { logout(); return; }
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

    const avatar = document.createElement('div');
    avatar.className = `message-avatar ${isBot ? 'bot-avatar' : 'user-avatar'}`;
    avatar.innerHTML = isBot ? '<i class="fa-solid fa-sparkles"></i>' : 'U';

    const content = document.createElement('div');
    content.className = 'message-content';
    content.innerHTML = text;

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

    let html = text
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
        .replace(/\n/g, '<br>');

    contentDiv.innerHTML = html;

    contentDiv.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
    });

    scrollToBottom();
}

function scrollToBottom() {
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

document.getElementById('user-query').addEventListener('input', function (e) {
    sendBtn.disabled = e.target.value.trim() === '';
});
