// API Configuration
const API_BASE = 'http://localhost:5000';

// State Management
let currentUser = null;
let selectedFile = null;
let stegoImagePath = null;

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    checkAuthStatus();
});

// Event Listeners
function initializeEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = e.target.getAttribute('href').substring(1);
            scrollToSection(target);
        });
    });

    // Auth Buttons
    document.getElementById('loginBtn').addEventListener('click', () => openModal('loginModal'));
    document.getElementById('registerBtn').addEventListener('click', () => openModal('registerModal'));
    document.getElementById('logoutBtn').addEventListener('click', logout);

    // Modal Close
    document.querySelectorAll('.close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.target.closest('.modal').style.display = 'none';
        });
    });

    // Forms
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    document.getElementById('decryptForm').addEventListener('submit', handleDecrypt);

    // File Upload
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--primary)';
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = 'var(--border)';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--border)';
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            selectedFile = files[0];
            displayFileInfo();
        }
    });

    document.getElementById('removeFile').addEventListener('click', clearFileSelection);
    document.getElementById('uploadBtn').addEventListener('click', handleSecureUpload);
}

// Scroll to Section
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
        
        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${sectionId}`) {
                link.classList.add('active');
            }
        });
    }
}

// Modal Functions
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Auth Functions
function checkAuthStatus() {
    const user = localStorage.getItem('user');
    if (user) {
        currentUser = JSON.parse(user);
        updateUIForLoggedInUser();
    }
}

function updateUIForLoggedInUser() {
    document.getElementById('loginBtn').style.display = 'none';
    document.getElementById('registerBtn').style.display = 'none';
    document.getElementById('userMenu').style.display = 'flex';
    document.getElementById('userName').textContent = currentUser.username;
    
    // Load user files
    loadMyFiles();
    loadSharedFiles();
    
    if (currentUser.role === 'admin') {
        document.querySelector('.admin-only').style.display = 'block';
        document.getElementById('admin').style.display = 'block';
        loadAdminStats();
    }
}

async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            localStorage.setItem('user', JSON.stringify(currentUser));
            closeModal('loginModal');
            updateUIForLoggedInUser();
            showToast('Login successful!', 'success');
        } else {
            showToast(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        showToast('Connection error', 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    
    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            closeModal('registerModal');
            showToast('Registration successful! Please login.', 'success');
            openModal('loginModal');
        } else {
            showToast(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        showToast('Connection error', 'error');
    }
}

function logout() {
    localStorage.removeItem('user');
    currentUser = null;
    location.reload();
}

// File Upload Functions
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        selectedFile = files[0];
        displayFileInfo();
    }
}

function displayFileInfo() {
    document.getElementById('fileName').textContent = selectedFile.name;
    document.getElementById('fileInfo').style.display = 'flex';
    document.getElementById('uploadBtn').disabled = false;
}

function clearFileSelection() {
    selectedFile = null;
    document.getElementById('fileInfo').style.display = 'none';
    document.getElementById('uploadBtn').disabled = true;
    document.getElementById('fileInput').value = '';
}

async function handleSecureUpload() {
    if (!selectedFile) {
        showToast('Please select a file', 'error');
        return;
    }
    
    if (!currentUser) {
        showToast('Please login first', 'error');
        openModal('loginModal');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('user_id', currentUser.id);
    
    const uploadBtn = document.getElementById('uploadBtn');
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Encrypting...';
    
    try {
        const response = await fetch(`${API_BASE}/secure-upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            stegoImagePath = data.stego_image;
            document.getElementById('uploadResult').style.display = 'block';
            
            // Update download button with correct path
            const downloadBtn = document.getElementById('downloadStegoBtn');
            downloadBtn.onclick = () => downloadStegoImage(data.stego_image);
            
            showToast('File encrypted successfully!', 'success');
            clearFileSelection();
            loadMyFiles(); // Refresh file list
        } else {
            showToast(data.error || 'Upload failed', 'error');
        }
    } catch (error) {
        showToast('Connection error', 'error');
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = '<i class="fas fa-lock"></i> Encrypt & Upload';
    }
}

function downloadStegoImage(imagePath) {
    // Create download link
    const link = document.createElement('a');
    link.href = `${API_BASE}/download-stego/${imagePath}`;
    link.download = imagePath.split('/').pop();
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// File Decrypt Function
async function handleDecrypt(e) {
    e.preventDefault();
    
    const stegoInput = document.getElementById('stegoInput');
    if (!stegoInput.files.length) {
        showToast('Please select a stego-image', 'error');
        return;
    }
    
    if (!selectedFileForDecryption) {
        showToast('No file selected for decryption', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('image', stegoInput.files[0]);
    formData.append('file_id', selectedFileForDecryption);
    
    try {
        const response = await fetch(`${API_BASE}/decrypt-file`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'decrypted_file';
            link.click();
            
            closeModal('decryptModal');
            showToast('File decrypted successfully!', 'success');
            stegoInput.value = '';
            selectedFileForDecryption = null;
        } else {
            const data = await response.json();
            showToast(data.error || 'Decryption failed', 'error');
        }
    } catch (error) {
        showToast('Connection error', 'error');
    }
}

// Load Files
async function loadFiles() {
    try {
        const response = await fetch(`${API_BASE}/files`);
        const data = await response.json();
        
        const filesGrid = document.getElementById('filesGrid');
        filesGrid.innerHTML = '';
        
        if (data.files && data.files.length > 0) {
            data.files.forEach(file => {
                const fileCard = createFileCard(file);
                filesGrid.appendChild(fileCard);
            });
        } else {
            filesGrid.innerHTML = '<p style="text-align: center; color: var(--gray);">No files uploaded yet</p>';
        }
    } catch (error) {
        showToast('Failed to load files', 'error');
    }
}

function createFileCard(fileName) {
    const card = document.createElement('div');
    card.className = 'file-card';
    card.innerHTML = `
        <i class="fas fa-file-alt"></i>
        <h4>${fileName}</h4>
        <p>Encrypted file</p>
    `;
    return card;
}

// Admin Functions
async function loadAdminStats() {
    try {
        const response = await fetch(`${API_BASE}/admin/stats`);
        const data = await response.json();
        
        document.getElementById('totalUsers').textContent = data.users || 0;
        document.getElementById('totalFiles').textContent = data.files || 0;
        document.getElementById('totalShares').textContent = data.shares || 0;
        document.getElementById('totalDownloads').textContent = data.downloads || 0;
    } catch (error) {
        console.error('Failed to load admin stats');
    }
}

// Toast Notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Load My Files
async function loadMyFiles() {
    if (!currentUser) return;
    
    try {
        const response = await fetch(`${API_BASE}/my-files?user_id=${currentUser.id}`);
        const data = await response.json();
        
        const filesGrid = document.getElementById('myFilesGrid');
        filesGrid.innerHTML = '';
        
        if (data.files && data.files.length > 0) {
            data.files.forEach(file => {
                const fileCard = createMyFileCard(file);
                filesGrid.appendChild(fileCard);
            });
        } else {
            filesGrid.innerHTML = '<p style="text-align: center; color: var(--gray); grid-column: 1/-1;">No files uploaded yet</p>';
        }
    } catch (error) {
        showToast('Failed to load files', 'error');
    }
}

function createMyFileCard(file) {
    const card = document.createElement('div');
    card.className = 'file-card';
    card.innerHTML = `
        <i class="fas fa-file-alt"></i>
        <h4>${file.original_filename}</h4>
        <p>Uploaded: ${new Date(file.upload_date).toLocaleDateString()}</p>
        <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
            <button class="btn btn-primary" onclick="downloadStegoImage('${file.stego_image}')" style="flex: 1; padding: 0.5rem;">
                <i class="fas fa-download"></i> Stego
            </button>
            <button class="btn btn-outline" onclick="openShareModal(${file.id}, '${file.original_filename}')" style="flex: 1; padding: 0.5rem;">
                <i class="fas fa-share"></i> Share
            </button>
        </div>
    `;
    return card;
}

// Load Shared Files
async function loadSharedFiles() {
    if (!currentUser) return;
    
    try {
        const response = await fetch(`${API_BASE}/shared-with-me?user_id=${currentUser.id}`);
        const data = await response.json();
        
        const filesGrid = document.getElementById('sharedFilesGrid');
        filesGrid.innerHTML = '';
        
        if (data.files && data.files.length > 0) {
            data.files.forEach(file => {
                const fileCard = createSharedFileCard(file);
                filesGrid.appendChild(fileCard);
            });
        } else {
            filesGrid.innerHTML = '<p style="text-align: center; color: var(--gray); grid-column: 1/-1;">No files shared with you</p>';
        }
    } catch (error) {
        showToast('Failed to load shared files', 'error');
    }
}

function createSharedFileCard(file) {
    const card = document.createElement('div');
    card.className = 'file-card';
    card.innerHTML = `
        <i class="fas fa-file-alt"></i>
        <h4>${file.original_filename}</h4>
        <p>From: ${file.sender_name}</p>
        <p style="font-size: 0.75rem;">Shared: ${new Date(file.shared_date).toLocaleDateString()}</p>
        <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
            <button class="btn btn-primary" onclick="downloadStegoImage('${file.stego_image}')" style="flex: 1; padding: 0.5rem;">
                <i class="fas fa-download"></i> Stego
            </button>
            <button class="btn btn-outline" onclick="openDecryptModal(${file.id})" style="flex: 1; padding: 0.5rem;">
                <i class="fas fa-unlock"></i> Decrypt
            </button>
        </div>
    `;
    return card;
}

// Open Share Modal
let selectedFileForSharing = null;

async function openShareModal(fileId, filename) {
    selectedFileForSharing = fileId;
    document.getElementById('shareFilename').textContent = filename;
    
    // Load users
    try {
        const response = await fetch(`${API_BASE}/users?user_id=${currentUser.id}`);
        const data = await response.json();
        
        const userSelect = document.getElementById('shareUserSelect');
        userSelect.innerHTML = '<option value="">Select a user...</option>';
        
        data.users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.id;
            option.textContent = `${user.username} (${user.email})`;
            userSelect.appendChild(option);
        });
        
        openModal('shareModal');
    } catch (error) {
        showToast('Failed to load users', 'error');
    }
}

// Share File
async function shareFile() {
    const receiverId = document.getElementById('shareUserSelect').value;
    
    if (!receiverId) {
        showToast('Please select a user', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/share-file`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file_id: selectedFileForSharing,
                sender_id: currentUser.id,
                receiver_id: receiverId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('File shared successfully!', 'success');
            closeModal('shareModal');
        } else {
            showToast(data.error || 'Failed to share file', 'error');
        }
    } catch (error) {
        showToast('Connection error', 'error');
    }
}

// Open Decrypt Modal with file ID
let selectedFileForDecryption = null;

function openDecryptModal(fileId) {
    selectedFileForDecryption = fileId;
    openModal('decryptModal');
}
