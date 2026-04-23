from flask import Blueprint, request, jsonify
import os
from services.stego_service import hide_key_in_image
import time
# Import services
from services.file_service import split_file
from services.encryption_service import encrypt_data
from services.stego_service import extract_key_from_image
from services.encryption_service import decrypt_data
from flask import send_file
from database import get_connection

file_bp = Blueprint('file', __name__)

# Folder to store uploaded files
UPLOAD_FOLDER = "uploads"

# Ensure folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# 🔹 1. Normal File Upload (Optional)
@file_bp.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        return jsonify({
            "message": "File uploaded successfully",
            "filename": file.filename
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 2. Secure Upload (MAIN FEATURE 🔥)
@file_bp.route('/secure-upload', methods=['POST'])
def secure_upload():
    try:
        file = request.files['file']
        user_id = request.form.get('user_id')  # Get user ID from request

        if not user_id:
            return jsonify({"error": "User not authenticated"}), 401

        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # 🔹 Read file
        file_data = file.read()
        original_filename = file.filename

        # 🔹 STEP 1: Split file
        b1, b2, b3 = split_file(file_data)

        # 🔹 STEP 2: Encrypt blocks
        e1, k1 = encrypt_data(b1, "AES")
        e2, k2 = encrypt_data(b2, "3DES")
        e3, k3 = encrypt_data(b3, "Blowfish")

        # 🔹 STEP 3: Combine keys
        full_key = k1 + b'||' + k2 + b'||' + k3

        # 🔹 STEP 4: Save encrypted blocks with unique names
        if not os.path.exists("uploads"):
            os.makedirs("uploads")

        unique_id = str(int(time.time()))
        block1_path = f"uploads/block1_{unique_id}.enc"
        block2_path = f"uploads/block2_{unique_id}.enc"
        block3_path = f"uploads/block3_{unique_id}.enc"

        with open(block1_path, "wb") as f:
            f.write(e1)

        with open(block2_path, "wb") as f:
            f.write(e2)

        with open(block3_path, "wb") as f:
            f.write(e3)

        # 🔹 STEP 5: Hide key in image (STEGANOGRAPHY)
        input_image = "input.png"
        stego_folder = "stego"

        if not os.path.exists(stego_folder):
            os.makedirs(stego_folder)

        stego_filename = f"stego_{unique_id}_{original_filename}.png"
        output_image = os.path.join(stego_folder, stego_filename)

        hide_key_in_image(input_image, full_key, output_image)

        # 🔹 STEP 6: Save to database
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO files (sender_id, filename, original_filename, stego_image, 
                             block1_path, block2_path, block3_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, stego_filename, original_filename, stego_filename, 
              block1_path, block2_path, block3_path))
        
        file_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()

        # 🔹 RESPONSE
        return jsonify({
            "message": "File encrypted and key hidden in image",
            "stego_image": stego_filename,
            "file_id": file_id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 3. List User's Files
@file_bp.route('/my-files', methods=['GET'])
def my_files():
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({"error": "User not authenticated"}), 401
        
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, filename, original_filename, stego_image, upload_date 
            FROM files 
            WHERE sender_id = %s 
            ORDER BY upload_date DESC
        """, (user_id,))
        
        files = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({"files": files})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 4. Get All Users (for sharing dropdown)
@file_bp.route('/users', methods=['GET'])
def get_users():
    try:
        current_user_id = request.args.get('user_id')
        
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all users except current user
        cursor.execute("""
            SELECT id, username, email 
            FROM users 
            WHERE id != %s
        """, (current_user_id,))
        
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({"users": users})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 5. Share File with Another User
@file_bp.route('/share-file', methods=['POST'])
def share_file():
    try:
        data = request.json
        file_id = data.get('file_id')
        sender_id = data.get('sender_id')
        receiver_id = data.get('receiver_id')
        
        if not all([file_id, sender_id, receiver_id]):
            return jsonify({"error": "Missing required fields"}), 400
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if already shared
        cursor.execute("""
            SELECT id FROM shared_files 
            WHERE file_id = %s AND receiver_id = %s
        """, (file_id, receiver_id))
        
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "File already shared with this user"}), 400
        
        # Share the file
        cursor.execute("""
            INSERT INTO shared_files (file_id, sender_id, receiver_id)
            VALUES (%s, %s, %s)
        """, (file_id, sender_id, receiver_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "File shared successfully"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 6. Get Shared Files (files shared with me)
@file_bp.route('/shared-with-me', methods=['GET'])
def shared_with_me():
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({"error": "User not authenticated"}), 401
        
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                f.id, 
                f.filename, 
                f.original_filename, 
                f.stego_image,
                u.username as sender_name,
                sf.shared_date
            FROM shared_files sf
            JOIN files f ON sf.file_id = f.id
            JOIN users u ON sf.sender_id = u.id
            WHERE sf.receiver_id = %s
            ORDER BY sf.shared_date DESC
        """, (user_id,))
        
        files = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({"files": files})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 7. List Uploaded Files (for testing)
@file_bp.route('/files', methods=['GET'])
def list_files():
    try:
        files = os.listdir(UPLOAD_FOLDER)

        return jsonify({
            "files": files
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔹 4. Delete File (optional utility)
@file_bp.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        path = os.path.join(UPLOAD_FOLDER, filename)

        if os.path.exists(path):
            os.remove(path)
            return jsonify({"message": "File deleted"})
        else:
            return jsonify({"error": "File not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@file_bp.route('/download-stego/<path:filename>', methods=['GET'])
def download_stego(filename):
    try:
        # Remove 'stego/' prefix if it exists in the filename
        if filename.startswith('stego/'):
            filename = filename[6:]
        
        file_path = os.path.join("stego", filename)
        
        if os.path.exists(file_path):
            response = send_file(os.path.join("stego", filename), as_attachment=True)
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response
        else:
            return jsonify({"error": "Stego-image not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@file_bp.route('/decrypt-file', methods=['POST'])
def decrypt_file():
    try:
        # Step 1: Get stego image and file_id
        stego_image = request.files['image']
        file_id = request.form.get('file_id')

        if not file_id:
            return jsonify({"error": "File ID required"}), 400

        # Get file info from database
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT block1_path, block2_path, block3_path, original_filename
            FROM files WHERE id = %s
        """, (file_id,))
        
        file_info = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not file_info:
            return jsonify({"error": "File not found"}), 404

        # Save uploaded stego image temporarily
        temp_stego_path = os.path.join("stego", f"temp_{stego_image.filename}")
        stego_image.save(temp_stego_path)

        # Step 2: Extract combined key
        full_key = extract_key_from_image(temp_stego_path, 60)

        # Step 3: Split keys
        parts = full_key.split(b'||')
        k1 = parts[0]
        k2 = parts[1]
        k3 = parts[2]

        # Step 4: Read encrypted blocks
        with open(file_info['block1_path'], "rb") as f:
            e1 = f.read()

        with open(file_info['block2_path'], "rb") as f:
            e2 = f.read()

        with open(file_info['block3_path'], "rb") as f:
            e3 = f.read()

        # Step 5: Decrypt
        d1 = decrypt_data(e1, k1, "AES")
        d2 = decrypt_data(e2, k2, "3DES")
        d3 = decrypt_data(e3, k3, "Blowfish")

        # Step 6: Merge
        original_data = d1 + d2 + d3

        # Step 7: Save original file
        output_path = os.path.join("uploads", f"recovered_{file_info['original_filename']}")
        with open(output_path, "wb") as f:
            f.write(original_data)

        # Clean up temp stego image
        if os.path.exists(temp_stego_path):
            os.remove(temp_stego_path)

        return send_file(output_path, as_attachment=True, download_name=file_info['original_filename'])

    except Exception as e:
        return jsonify({"error": str(e)}), 500