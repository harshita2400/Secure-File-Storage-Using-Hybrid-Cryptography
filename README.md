# 🔐 SecureVault - Multi-User Encrypted File Storage System

<div align="center">

**A comprehensive web-based file storage system featuring hybrid cryptography, LSB steganography, and secure multi-user file sharing.**

</div>

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Security](#-security)
- [Screenshots](#-screenshots)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

SecureVault is a secure file storage and sharing platform that implements military-grade encryption combined with steganography to protect sensitive data. The system splits files into three blocks, encrypts each with a different algorithm (AES, 3DES, Blowfish), and hides the decryption keys inside images using LSB steganography.

### Why SecureVault?

- **Triple-Layer Encryption**: Files are encrypted using three different algorithms
- **Steganography**: Encryption keys are hidden inside images, invisible to the naked eye
- **Multi-User Support**: Secure user authentication and controlled file sharing
- **Zero-Knowledge Architecture**: Keys are never stored on the server
- **User-Friendly**: Modern, intuitive interface with drag-and-drop functionality

---

## ✨ Features

### 🔒 Security Features

- **Hybrid Encryption**
  - AES-256 encryption for Block 1
  - 3DES encryption for Block 2
  - Blowfish encryption for Block 3
  
- **LSB Steganography**
  - Encryption keys hidden in images
  - Invisible to human eye
  - No metadata exposure

- **User Authentication**
  - Bcrypt password hashing with salt
  - Secure session management
  - Role-based access control (User/Admin)

- **Controlled File Sharing**
  - Share encrypted files with specific users
  - Recipient needs stego-image to decrypt
  - Complete audit trail

### 👥 User Features

- **File Management**
  - Upload any file type
  - View uploaded files
  - Download stego-images
  - Track file history

- **Secure Sharing**
  - Share files with other users
  - View files shared with you
  - Sender information displayed
  - Share tracking

- **File Recovery**
  - Upload stego-image to decrypt
  - Automatic block retrieval
  - Original filename preservation
  - Integrity verification

### 📊 Admin Features

- **Dashboard Analytics**
  - Total users count
  - Encrypted files statistics
  - File sharing metrics
  - Download tracking

- **System Monitoring**
  - User activity logs
  - Storage usage
  - Share history
  - System health

### 🎨 UI/UX Features

- **Modern Interface**
  - Clean gradient design
  - Responsive layout
  - Smooth animations
  - Intuitive navigation

- **User Experience**
  - Drag-and-drop upload
  - Real-time notifications
  - Progress indicators
  - Error handling

---

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask 3.0.0
- **Database**: MySQL 8.0+
- **Encryption**: PyCryptodome (AES, 3DES, Blowfish)
- **Steganography**: Pillow (PIL) for LSB implementation
- **Authentication**: bcrypt for password hashing
- **CORS**: flask-cors for cross-origin requests

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Custom properties, Grid, Flexbox
- **JavaScript**: ES6+ vanilla JavaScript
- **Icons**: Font Awesome 6.4.0

### Database Schema
```sql
users
├── id, username, email, password (hashed)
└── role, created_at

files
├── id, sender_id, filename, original_filename
├── stego_image, block1_path, block2_path, block3_path
└── upload_date

shared_files
├── id, file_id, sender_id, receiver_id
└── shared_date

file_downloads
├── id, file_id, user_id
└── downloaded_at
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
│  HTML5 + CSS3 + Vanilla JavaScript                      │
│  ├─ User Interface                                       │
│  ├─ File Upload/Download                                │
│  ├─ Authentication UI                                    │
│  └─ Real-time Notifications                             │
└─────────────────────────────────────────────────────────┘
                         ↓ REST API
┌─────────────────────────────────────────────────────────┐
│                    Backend Layer                         │
│  Flask + Python                                          │
│  ├─ Authentication (bcrypt)                             │
│  ├─ File Processing                                     │
│  ├─ Encryption Service (AES, 3DES, Blowfish)           │
│  ├─ Steganography Service (LSB)                        │
│  └─ File Sharing Management                            │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                    Database Layer                        │
│  MySQL 8.0+                                             │
│  ├─ users (authentication)                              │
│  ├─ files (metadata)                                    │
│  ├─ shared_files (sharing records)                     │
│  └─ file_downloads (audit trail)                       │
└─────────────────────────────────────────────────────────┘
```

### Encryption Flow

```
Original File
     ↓
Split into 3 equal blocks
     ↓
┌────────────────────────────────────┐
│ Block 1 → AES-256 → Encrypted 1   │
│ Block 2 → 3DES → Encrypted 2      │
│ Block 3 → Blowfish → Encrypted 3  │
└────────────────────────────────────┘
     ↓
Generate 3 encryption keys (K1, K2, K3)
     ↓
Combine keys: K1 || K2 || K3
     ↓
Hide combined key in image using LSB
     ↓
Stego-Image (contains hidden keys)
```

### Decryption Flow

```
Upload Stego-Image
     ↓
Extract hidden keys using LSB
     ↓
Split keys: K1, K2, K3
     ↓
┌────────────────────────────────────┐
│ Decrypt Block 1 with K1 (AES)     │
│ Decrypt Block 2 with K2 (3DES)    │
│ Decrypt Block 3 with K3 (Blowfish)│
└────────────────────────────────────┘
     ↓
Merge decrypted blocks
     ↓
Original File Recovered
```

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- MySQL Server 8.0 or higher
- Modern web browser (Chrome, Firefox, Edge)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/securevault.git
cd securevault
```

### Step 2: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Dependencies:**
- Flask==3.0.0
- flask-cors==4.0.0
- bcrypt==4.1.2
- mysql-connector-python==8.2.0
- Pillow==10.2.0
- pycryptodome==3.19.1
- python-dotenv==1.0.0

### Step 3: Configure Database

1. **Create MySQL Database**:
```sql
CREATE DATABASE secure_storage;
```

2. **Update Configuration**:
Edit `backend/.env`:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=secure_storage
SECRET_KEY=your_secret_key_here
```

3. **Initialize Database**:
```bash
cd backend
python setup_db.py
```



### Step 4: Add Base Image for Steganography

Place a PNG image named `input.png` in the `backend/` directory. This image will be used as the carrier for hiding encryption keys.


### Step 5: Start the Application

### Step 6: Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:8000
- **Backend API**: http://localhost:5000

---



## 🤝 Contributing

Contributions are welcome!

### Development Guidelines

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Write tests for new features
- Update documentation

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Authors

- **Harshita** 

---


---



</div>
