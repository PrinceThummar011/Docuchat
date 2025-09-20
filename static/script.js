// Global variables
let apiKey = localStorage.getItem('groqApiKey') || '';
let uploadedFiles = [];
let currentConversation = [];
let sessionId = localStorage.getItem('sessionId') || generateSessionId();

// API endpoints
const API_BASE = '/api';

// DOM Elements
const elements = {
    sidebar: document.getElementById('sidebar'),
    menuToggle: document.getElementById('menuToggle'),
    sidebarToggle: document.getElementById('sidebarToggle'),
    uploadArea: document.getElementById('uploadArea'),
    fileInput: document.getElementById('fileInput'),
    filesList: document.getElementById('filesList'),
    apiKeyInput: document.getElementById('apiKey'),
    saveApiKeyBtn: document.getElementById('saveApiKey'),
    apiKeyValidation: document.getElementById('apiKeyValidation'),
    welcomeScreen: document.getElementById('welcomeScreen'),
    chatMessages: document.getElementById('chatMessages'),
    messageInput: document.getElementById('messageInput'),
    sendButton: document.getElementById('sendButton'),
    clearChatBtn: document.getElementById('clearChat'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    toastContainer: document.getElementById('toastContainer'),
    modeIndicator: document.getElementById('modeIndicator')
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadApiKey();
    updateUI();
});

function initializeApp() {
    // Auto-resize textarea
    if (elements.messageInput) {
        elements.messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 200) + 'px';
        });
    }
}

function setupEventListeners() {
    // Sidebar toggle
    if (elements.menuToggle) {
        elements.menuToggle.addEventListener('click', toggleSidebar);
    }
    
    if (elements.sidebarToggle) {
        elements.sidebarToggle.addEventListener('click', toggleSidebar);
    }

    // File upload
    if (elements.uploadArea) {
        elements.uploadArea.addEventListener('click', () => elements.fileInput?.click());
        elements.uploadArea.addEventListener('dragover', handleDragOver);
        elements.uploadArea.addEventListener('dragleave', handleDragLeave);
        elements.uploadArea.addEventListener('drop', handleDrop);
    }

    if (elements.fileInput) {
        elements.fileInput.addEventListener('change', handleFileSelect);
    }

    // API Key
    if (elements.saveApiKeyBtn) {
        elements.saveApiKeyBtn.addEventListener('click', saveApiKey);
    }

    if (elements.apiKeyInput) {
        elements.apiKeyInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                saveApiKey();
            }
        });
        
        // Real-time validation
        elements.apiKeyInput.addEventListener('input', function(e) {
            const apiKey = e.target.value.trim();
            if (apiKey.length > 0) {
                const validation = validateGroqApiKey(apiKey);
                showValidationMessage(validation);
            } else {
                hideValidationMessage();
            }
        });
    }

    // Chat functionality
    if (elements.sendButton) {
        elements.sendButton.addEventListener('click', sendMessage);
    }

    if (elements.messageInput) {
        elements.messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        elements.messageInput.addEventListener('input', function() {
            elements.sendButton.disabled = !this.value.trim();
        });
    }

    // Clear chat
    if (elements.clearChatBtn) {
        elements.clearChatBtn.addEventListener('click', clearChat);
    }

    // Click outside sidebar to close on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768 && elements.sidebar.classList.contains('open')) {
            if (!elements.sidebar.contains(e.target) && !elements.menuToggle.contains(e.target)) {
                toggleSidebar();
            }
        }
    });
}

function toggleSidebar() {
    if (elements.sidebar) {
        elements.sidebar.classList.toggle('open');
    }
}

// File handling functions
function handleDragOver(e) {
    e.preventDefault();
    elements.uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    elements.uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    elements.uploadArea.classList.remove('dragover');
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
}

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    handleFiles(files);
}

function handleFiles(files) {
    const validTypes = ['.pdf', '.txt', '.docx', '.doc'];
    const validFiles = files.filter(file => {
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        return validTypes.includes(extension);
    });

    if (validFiles.length === 0) {
        showToast('Please select valid document files (PDF, TXT, DOCX, DOC)', 'error');
        return;
    }

    uploadFilesToServer(validFiles);
}

async function uploadFilesToServer(files) {
    showLoading();
    
    try {
        const formData = new FormData();
        files.forEach(file => {
            formData.append('files', file);
        });
        formData.append('session_id', sessionId);

        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            showToast('Upload failed: Server not reachable or error occurred.', 'error');
            hideLoading();
            return;
        }

        const data = await response.json();
        
        if (data.success) {
            // Update session ID if new
            if (data.session_id !== sessionId) {
                sessionId = data.session_id;
                localStorage.setItem('sessionId', sessionId);
            }
            
            // Add files to our local list
            data.files.forEach(fileData => {
                if (!uploadedFiles.find(f => f.id === fileData.id)) {
                    uploadedFiles.push({
                        id: fileData.id,
                        name: fileData.name,
                        size: formatFileSize(fileData.size)
                    });
                }
            });
            
            updateFilesList();
            updateUI();
            showToast(data.message, 'success');
        } else {
            showToast(data.error || 'Upload failed', 'error');
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        showToast('Upload failed. Please check your server and try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function removeFile(fileId) {
    try {
        const response = await fetch(`${API_BASE}/remove_file`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                file_id: fileId
            })
        });

        const data = await response.json();
        
        if (data.success) {
            uploadedFiles = uploadedFiles.filter(f => f.id !== fileId);
            updateFilesList();
            updateUI();
            showToast('File removed', 'info');
        } else {
            showToast(data.error || 'Failed to remove file', 'error');
        }
    } catch (error) {
        console.error('Remove file error:', error);
        showToast('Failed to remove file', 'error');
    }
}

function updateFilesList() {
    if (!elements.filesList) return;

    elements.filesList.innerHTML = '';
    
    uploadedFiles.forEach(fileData => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-info">
                <i class="fas fa-file-alt"></i>
                <div class="file-details">
                    <div class="file-name" title="${fileData.name}">${fileData.name}</div>
                    <div class="file-size">${fileData.size}</div>
                </div>
            </div>
            <div class="file-actions">
                <button class="file-remove" onclick="removeFile(${fileData.id})" title="Remove file">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        elements.filesList.appendChild(fileItem);
    });
}

// API Key functions
function validateGroqApiKey(apiKey) {
    if (!apiKey || typeof apiKey !== 'string') {
        return { valid: false, message: 'API key is required' };
    }
    
    apiKey = apiKey.trim();
    
    // Check for placeholder values
    if (['no-key-needed', '123', 'test', 'demo', ''].includes(apiKey.toLowerCase())) {
        return { valid: false, message: 'Please enter a valid GROQ API key' };
    }
    
    // GROQ API keys start with 'gsk_'
    if (!apiKey.startsWith('gsk_')) {
        return { valid: false, message: 'GROQ API keys must start with "gsk_"' };
    }
    
    // Check length
    if (apiKey.length < 30) {
        return { valid: false, message: 'API key is too short' };
    }
    
    if (apiKey.length > 100) {
        return { valid: false, message: 'API key is too long' };
    }
    
    // Check characters
    if (!/^gsk_[A-Za-z0-9_]+$/.test(apiKey)) {
        return { valid: false, message: 'API key contains invalid characters' };
    }
    
    return { valid: true, message: 'API key format is valid' };
}

function loadApiKey() {
    if (apiKey && elements.apiKeyInput) {
        elements.apiKeyInput.value = apiKey;
    }
}

function showValidationMessage(validation) {
    if (elements.apiKeyValidation) {
        elements.apiKeyValidation.style.display = 'block';
        elements.apiKeyValidation.className = `api-validation ${validation.valid ? 'valid' : 'invalid'}`;
        elements.apiKeyValidation.innerHTML = validation.valid ? 
            '✅ Valid GROQ API key format' : 
            `❌ ${validation.message}`;
    }
}

function hideValidationMessage() {
    if (elements.apiKeyValidation) {
        elements.apiKeyValidation.style.display = 'none';
    }
}

function saveApiKey() {
    const newApiKey = elements.apiKeyInput?.value.trim();
    
    if (newApiKey) {
        // Validate API key format
        const validation = validateGroqApiKey(newApiKey);
        
        if (!validation.valid) {
            showToast(`❌ Invalid API Key: ${validation.message}`, 'error');
            return;
        }
        
        apiKey = newApiKey;
        localStorage.setItem('groqApiKey', apiKey);
        showToast('✅ Valid GROQ API key saved! Enhanced AI responses enabled 🚀', 'success');
        updateUI();
    } else {
        // Clear API key
        apiKey = '';
        localStorage.removeItem('groqApiKey');
        showToast('Your API key cleared. Using smart analysis mode 📄', 'info');
        updateUI();
    }
}

// Chat functions
async function sendMessage() {
    const message = elements.messageInput?.value.trim();
    if (!message) return;

    if (uploadedFiles.length === 0) {
        showToast('Please upload at least one document first', 'warning');
        return;
    }

    // Add user message
    addMessage(message, 'user');
    elements.messageInput.value = '';
    elements.messageInput.style.height = 'auto';
    elements.sendButton.disabled = true;

    // Show loading
    showLoading();

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
                api_key: apiKey || 'no-key-needed'
            })
        });

        const data = await response.json();
        
        if (data.success) {
            addMessage(data.response, 'assistant');
        } else {
            addMessage(data.response || 'Sorry, I encountered an error while processing your request.', 'assistant');
            if (data.error) {
                showToast(data.error, 'error');
            }
        }
    } catch (error) {
        console.error('Chat error:', error);
        addMessage('Sorry, I encountered an error while processing your request. Please try again.', 'assistant');
        showToast('Error processing message', 'error');
    } finally {
        hideLoading();
        updateUI();
    }
}

async function simulateApiCall(message) {
    // This function is no longer needed as we use the real API
    // Keeping it for backwards compatibility
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const responses = [
        `Based on your uploaded documents, I can see you're asking about "${message}". This is a simulated response that would normally be generated by analyzing your documents with AI.`,
        `I've analyzed your documents regarding "${message}". Here are the key points I found...`,
        `According to the content in your uploaded files, "${message}" relates to several important aspects that I can help explain.`,
        `Thank you for your question about "${message}". Based on the document analysis, I can provide you with the following insights...`
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
}

function addMessage(content, sender) {
    if (!elements.chatMessages) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const avatar = sender === 'user' ? 
        '<i class="fas fa-user"></i>' : 
        '<i class="fas fa-robot"></i>';
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <p>${formatMessage(content)}</p>
            <div class="message-timestamp">${formatTime(new Date())}</div>
        </div>
    `;

    elements.chatMessages.appendChild(messageDiv);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;

    // Store in conversation
    currentConversation.push({ role: sender, content, timestamp: new Date() });
}

function formatMessage(content) {
    // Basic formatting - can be enhanced
    return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
}

async function clearChat() {
    try {
        const response = await fetch(`${API_BASE}/clear`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId
            })
        });

        const data = await response.json();
        
        if (data.success) {
            if (elements.chatMessages) {
                elements.chatMessages.innerHTML = '';
            }
            currentConversation = [];
            updateUI();
            showToast('Chat cleared', 'info');
        } else {
            showToast(data.error || 'Failed to clear chat', 'error');
        }
    } catch (error) {
        console.error('Clear chat error:', error);
        showToast('Failed to clear chat', 'error');
    }
}

// UI update functions
function updateUI() {
    const hasFiles = uploadedFiles.length > 0;
    const hasApiKey = !!apiKey && apiKey.length > 10;
    const canChat = hasFiles;

    // Update mode indicator
    if (elements.modeIndicator) {
        const modeText = elements.modeIndicator.querySelector('.mode-text');
        if (hasApiKey) {
            modeText.textContent = '🤖 AI Enhanced';
            elements.modeIndicator.classList.add('ai-mode');
        } else {
            modeText.textContent = '📄 Smart Mode';
            elements.modeIndicator.classList.remove('ai-mode');
        }
    }

    // Show/hide welcome screen
    if (elements.welcomeScreen && elements.chatMessages) {
        if (currentConversation.length === 0) {
            elements.welcomeScreen.style.display = 'flex';
            elements.chatMessages.style.display = 'none';
        } else {
            elements.welcomeScreen.style.display = 'none';
            elements.chatMessages.style.display = 'flex';
        }
    }

    // Enable/disable send button
    if (elements.sendButton) {
        const hasMessage = elements.messageInput?.value.trim();
        elements.sendButton.disabled = !canChat || !hasMessage;
    }

    // Update input placeholder
    if (elements.messageInput) {
        if (!hasFiles) {
            elements.messageInput.placeholder = 'Upload documents to start chatting...';
            elements.messageInput.disabled = true;
        } else {
            const mode = hasApiKey ? 'AI-enhanced analysis' : 'smart document analysis';
            elements.messageInput.placeholder = `Ask questions for ${mode}...`;
            elements.messageInput.disabled = false;
        }
    }
}

// Utility functions
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatTime(date) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function showLoading() {
    if (elements.loadingOverlay) {
        elements.loadingOverlay.classList.add('show');
    }
}

function hideLoading() {
    if (elements.loadingOverlay) {
        elements.loadingOverlay.classList.remove('show');
    }
}

function showToast(message, type = 'info') {
    if (!elements.toastContainer) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    elements.toastContainer.appendChild(toast);

    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Example question insertion
function insertQuestion(element) {
    const question = element.querySelector('span')?.textContent;
    if (question && elements.messageInput) {
        elements.messageInput.value = question;
        elements.messageInput.focus();
        elements.messageInput.dispatchEvent(new Event('input'));
    }
}

// Handle window resize
window.addEventListener('resize', function() {
    if (window.innerWidth > 768) {
        elements.sidebar?.classList.remove('open');
    }
});

// Export functions for global access
window.removeFile = removeFile;
window.insertQuestion = insertQuestion;