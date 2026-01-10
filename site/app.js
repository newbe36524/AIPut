const input = document.getElementById('textInput');
const status = document.getElementById('status');
const historyList = document.getElementById('historyList');
const menuBtn = document.getElementById('menuBtn');
const menuClose = document.getElementById('menuClose');
const menuOverlay = document.getElementById('menuOverlay');
const sideMenu = document.getElementById('sideMenu');
const braveModeCheckbox = document.getElementById('braveMode');
const braveModeIndicator = document.getElementById('braveModeIndicator');
const promptSelect = document.getElementById('promptSelect');
const loadingOverlay = document.getElementById('loadingOverlay');
const loadingText = document.getElementById('loadingText');
const sendBtn = document.getElementById('sendBtn');
const resendArea = document.getElementById('resendArea');
const resendPreview = document.getElementById('resendPreview');
const MAX_HISTORY = 10;

// Store loaded prompts
let availablePrompts = [];
let currentPrompt = 'normal';

// Store last sent content for quick resend
let lastSentContent = null;

// Touch detection for swipe gestures
let touchStartY = 0;
let touchEndY = 0;
let disableTouchGestures = false;

// Loading state management
// These variables and functions manage the UI state during text submission and AI processing
let isLoading = false;          // Tracks if a submission is currently in progress
let savedInputText = '';        // Preserves input text for potential recovery

/**
 * Display loading overlay and disable user interactions
 * @param {string} message - The loading message to display (e.g., "发送中...", "AI处理中...")
 */
function showLoading(message) {
    isLoading = true;
    savedInputText = input.value;

    // Update loading message based on processing phase
    loadingText.textContent = message;

    // Show loading overlay with spinner animation
    loadingOverlay.classList.add('active');

    // Disable input field to prevent text entry during processing
    input.readOnly = true;
    input.style.pointerEvents = 'none';

    // Disable send button to prevent duplicate submissions
    sendBtn.disabled = true;

    // Disable swipe gestures to prevent conflicts during processing
    disableTouchGestures = true;
}

/**
 * Hide loading overlay and restore user interactions
 * Called after successful completion or error
 */
function hideLoading() {
    isLoading = false;

    // Hide loading overlay
    loadingOverlay.classList.remove('active');

    // Re-enable input field
    input.readOnly = false;
    input.style.pointerEvents = 'auto';

    // Enable send button
    sendBtn.disabled = false;

    // Re-enable swipe gestures
    disableTouchGestures = false;

    // Restore focus to input for better UX
    input.focus();
}

// Resend area functions
/**
 * Load last sent content from localStorage
 */
function loadLastSentContent() {
    const stored = localStorage.getItem('lastSentContent');
    lastSentContent = stored ? stored : null;
}

/**
 * Update last sent content and save to localStorage
 * @param {string} text - The text to save as last sent
 */
function updateLastSentContent(text) {
    lastSentContent = text;
    localStorage.setItem('lastSentContent', text);
    renderResendArea();
}

/**
 * Render resend area based on last sent content state
 * Shows/hides the resend area and updates preview text
 */
function renderResendArea() {
    if (lastSentContent) {
        resendArea.classList.remove('hidden');
        resendPreview.textContent = lastSentContent;
    } else {
        resendArea.classList.add('hidden');
        resendPreview.textContent = '';
    }
}

/**
 * Handle resend button click
 * Sends the last sent content again
 */
function handleResend() {
    if (!lastSentContent) return;
    sendRequest(lastSentContent);
}

// Load prompts configuration
async function loadPrompts() {
    try {
        const response = await fetch('/static/config/prompts.json');
        const data = await response.json();
        availablePrompts = data.prompts;

        // Clear existing options
        promptSelect.innerHTML = '';

        // Add options to select
        availablePrompts.forEach(prompt => {
            const option = document.createElement('option');
            option.value = prompt.id;
            option.textContent = prompt.name;
            option.title = prompt.description;
            promptSelect.appendChild(option);
        });

        // Load saved prompt or default to general-refine (口语书面化)
        const savedPrompt = localStorage.getItem('selectedPrompt') || 'general-refine';
        currentPrompt = savedPrompt;
        promptSelect.value = currentPrompt;

    } catch (error) {
        console.error('Failed to load prompts:', error);
        // Fallback to basic options
        promptSelect.innerHTML = `
            <option value="normal">无处理</option>
        `;
        availablePrompts = [{id: 'normal', name: '无处理', prompt: ''}];
    }
}

// Initialize
window.onload = function() {
    // Load prompts first
    loadPrompts().then(() => {
        renderHistory();
        input.focus();
    });

    // Load last sent content for resend area
    loadLastSentContent();
    renderResendArea();

    // Load brave mode setting from localStorage (default to true)
    const storedBraveMode = localStorage.getItem('braveMode');
    // Default to true if not set
    const braveMode = storedBraveMode === null ? true : storedBraveMode === 'true';
    braveModeCheckbox.checked = braveMode;
    updateBraveModeIndicator(braveMode);

    // Save brave mode setting when changed
    braveModeCheckbox.addEventListener('change', function() {
        localStorage.setItem('braveMode', this.checked);
        updateBraveModeIndicator(this.checked);
    });

    // Handle brave mode indicator click
    braveModeIndicator.addEventListener('click', function() {
        // Toggle brave mode
        braveModeCheckbox.checked = !braveModeCheckbox.checked;
        localStorage.setItem('braveMode', braveModeCheckbox.checked);
        updateBraveModeIndicator(braveModeCheckbox.checked);
    });

    // Handle prompt selection change
    promptSelect.addEventListener('change', function() {
        currentPrompt = this.value;
        localStorage.setItem('selectedPrompt', currentPrompt);
        input.focus(); // Keep focus on input after selection
    });

    // Calculate and set fixed height on page load
    function calculateTextareaHeight() {
        // Get viewport height
        const viewportHeight = window.innerHeight;
        // Get header height
        const header = document.querySelector('.header');
        const headerHeight = header ? header.offsetHeight : 0;
        // Get status height
        const status = document.getElementById('status');
        const statusHeight = status ? status.offsetHeight : 24; // Default status height
        // Calculate available height for textarea
        // Subtract padding (20px top and bottom) and some margin
        const availableHeight = viewportHeight - headerHeight - statusHeight - 80;
        // Set minimum and maximum height
        const minHeight = 300;
        const maxHeight = 800;
        const finalHeight = Math.max(minHeight, Math.min(availableHeight, maxHeight));

        // Set fixed height
        input.style.height = finalHeight + 'px';
        input.style.minHeight = finalHeight + 'px';
        input.style.maxHeight = finalHeight + 'px';
    }

    // Calculate initial height
    calculateTextareaHeight();

    // Recalculate on window resize
    window.addEventListener('resize', calculateTextareaHeight);
};

// Keyboard event handlers
input.addEventListener("keydown", function(event) {
    // Ignore keyboard events during loading
    if (isLoading) return;

    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        handleSend();
    }
});

// Menu controls
menuBtn.addEventListener('click', openMenu);
menuClose.addEventListener('click', closeMenu);
menuOverlay.addEventListener('click', closeMenu);

function openMenu() {
    menuBtn.classList.add('active');
    menuOverlay.classList.add('active');
    sideMenu.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeMenu() {
    menuBtn.classList.remove('active');
    menuOverlay.classList.remove('active');
    sideMenu.classList.remove('active');
    document.body.style.overflow = '';
    setTimeout(() => input.focus(), 100);
}

// Click outside to focus input
document.body.addEventListener('click', function(event) {
    const target = event.target;
    if (!target.closest('button') &&
        !target.closest('.menu-button') &&
        !target.closest('.side-menu') &&
        !target.closest('select') &&
        target !== input) {
        input.focus();
    }
});

// Touch gesture handling
input.addEventListener('touchstart', function(e) {
    touchStartY = e.changedTouches[0].screenY;
}, false);

input.addEventListener('touchend', function(e) {
    touchEndY = e.changedTouches[0].screenY;
    handleSwipe();
}, false);

function handleSwipe() {
    // Don't handle swipe gestures when disabled
    if (disableTouchGestures) return;

    const swipeThreshold = 50;
    const diff = touchStartY - touchEndY;

    if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
            // Swipe up - send
            handleSend();
        } else {
            // Swipe down - clear
            handleClear();
        }
    }
}

// Core functions
function handleSend() {
    // Prevent submission if already loading
    if (isLoading) return;

    const text = input.value.trim();
    if (!text) return;
    saveToHistory(text);
    sendRequest(text);
}

function handleClear() {
    input.value = '';
    input.focus();
}

/**
 * Send text to the server with loading states
 * Shows appropriate loading message based on AI processing mode
 * @param {string} text - The text to send
 */
function sendRequest(text) {
    // Check if brave mode is enabled
    const braveMode = braveModeCheckbox.checked;

    // Get current prompt info
    const promptInfo = availablePrompts.find(p => p.id === currentPrompt);

    // Show initial loading state
    let loadingMessage = "发送中...";

    // Determine loading message based on processing mode
    if (promptInfo && promptInfo.prompt && promptInfo.id !== 'normal') {
        loadingMessage = "AI处理中...";
        if (braveMode) {
            loadingMessage = "AI处理中... (勇敢模式)";
        }
    }

    showLoading(loadingMessage);

    // Prepare request body
    const requestBody = { text: text };

    // Add AI processing parameters if not in normal mode
    if (promptInfo && promptInfo.prompt && promptInfo.id !== 'normal') {
        requestBody.prompt = promptInfo.prompt;
        requestBody.mode = promptInfo.id;
        requestBody.provider = 'zai';
    }

    if (braveMode) {
        requestBody.auto_submit = true;
    }

    fetch('/type', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();

        if (data.success) {
            if (data.warning) {
                status.innerText = "⚠ " + data.warning;
                status.style.color = "#ff9500";
            } else {
                // Check if AI was used
                if (data.ai_processed) {
                    const processedInfo = data.original_length && data.processed_length
                        ? ` (${data.original_length}→${data.processed_length}字)`
                        : '';
                    status.innerText = "✓ AI处理完成" + processedInfo +
                        (braveMode ? " (Ctrl+Enter)" : "");
                    status.style.color = "#34c759";
                } else {
                    status.innerText = braveMode ? "✓ 已发送 (Ctrl+Enter)" : "✓ 已发送";
                    status.style.color = "#34c759";
                }
            }
            input.value = '';
            setTimeout(() => {
                status.innerText = "";
                input.focus();
            }, 1500);
        } else {
            throw new Error(data.error || "Server error");
        }
    })
    .catch(err => {
        hideLoading();

        // Check if it's a network error
        if (err.message === 'Failed to fetch' || err.name === 'TypeError') {
            status.innerText = "✕ 网络错误，请检查连接";
        } else {
            status.innerText = "✕ 发送失败";
        }
        status.style.color = "#ff3b30";
        console.error('Error:', err);

        // If AI processing failed, show option to send without AI
        if (promptInfo && promptInfo.id !== 'normal') {
            setTimeout(() => {
                if (confirm("AI处理失败，是否发送原始文本？")) {
                    // Send without AI processing
                    sendPlainRequest(text, braveMode);
                } else {
                    setTimeout(() => {
                        status.innerText = "";
                        input.focus();
                    }, 500);
                }
            }, 100);
        } else {
            setTimeout(() => {
                status.innerText = "";
                input.focus();
            }, 2000);
        }
    });

    // Update last sent content after every send attempt (success or failure)
    updateLastSentContent(text);
}

// Helper function to send plain request without AI processing
function sendPlainRequest(text, braveMode) {
    showLoading("发送中...");

    const plainRequestBody = {
        text: text,
        auto_submit: braveMode
    };

    fetch('/type', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(plainRequestBody)
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();

        if (data.success) {
            status.innerText = "✓ 已发送（原始文本）";
            status.style.color = "#34c759";
            input.value = '';
            setTimeout(() => {
                status.innerText = "";
                input.focus();
            }, 1500);
        }
    })
    .catch(() => {
        hideLoading();
        status.innerText = "✕ 发送失败";
        status.style.color = "#ff3b30";
        setTimeout(() => {
            status.innerText = "";
            input.focus();
        }, 2000);
    });

    // Update last sent content after every send attempt (success or failure)
    updateLastSentContent(text);
}

// History functions
function getHistory() {
    const stored = localStorage.getItem('typeHistory');
    return stored ? JSON.parse(stored) : [];
}

function saveToHistory(text) {
    let history = getHistory();
    history = history.filter(item => item !== text);
    history.unshift(text);
    if (history.length > MAX_HISTORY) {
        history = history.slice(0, MAX_HISTORY);
    }
    localStorage.setItem('typeHistory', JSON.stringify(history));
    renderHistory();
}

function renderHistory() {
    const history = getHistory();
    historyList.innerHTML = '';

    if (history.length === 0) {
        historyList.innerHTML = '<div style="text-align: center; color: #999; padding: 20px;">暂无历史记录</div>';
        return;
    }

    history.forEach(text => {
        const li = document.createElement('li');
        li.className = 'history-item';
        li.onclick = () => {
            closeMenu();
            input.value = text;
            handleSend();
        };
        li.innerHTML = `
            <span class="history-text">${escapeHtml(text)}</span>
            <span class="history-arrow">▶</span>
        `;
        historyList.appendChild(li);
    });
}

function clearHistory() {
    if (confirm('确定要清空所有历史记录吗？')) {
        localStorage.removeItem('typeHistory');
        renderHistory();
    }
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) {
        return map[m];
    });
}

// Update brave mode indicator
function updateBraveModeIndicator(isEnabled) {
    if (isEnabled) {
        braveModeIndicator.classList.add('active');
        braveModeIndicator.title = '勇敢模式已开启 (点击关闭)';
    } else {
        braveModeIndicator.classList.remove('active');
        braveModeIndicator.title = '勇敢模式已关闭 (点击开启)';
    }
}

// Prevent zoom on double tap
let lastTouchEnd = 0;
document.addEventListener('touchend', function(event) {
    const now = Date.now();
    if (now - lastTouchEnd <= 300) {
        event.preventDefault();
    }
    lastTouchEnd = now;
}, false);