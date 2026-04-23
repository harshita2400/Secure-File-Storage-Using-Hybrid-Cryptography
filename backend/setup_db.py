import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Connect without database first
try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    cursor = conn.cursor()
    
    # Create database
    cursor.execute("CREATE DATABASE IF NOT EXISTS secure_storage")
    print("✓ Database 'secure_storage' created/verified")
    
    # Use the database
    cursor.execute("USE secure_storage")
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Table 'users' created/verified")
    
    # Create files table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sender_id INT NOT NULL,
            filename VARCHAR(255) NOT NULL,
            original_filename VARCHAR(255) NOT NULL,
            stego_image VARCHAR(255) NOT NULL,
            block1_path VARCHAR(255) NOT NULL,
            block2_path VARCHAR(255) NOT NULL,
            block3_path VARCHAR(255) NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users(id)
        )
    """)
    print("✓ Table 'files' created/verified")
    
    # Create shared_files table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shared_files (
            id INT AUTO_INCREMENT PRIMARY KEY,
            file_id INT NOT NULL,
            sender_id INT NOT NULL,
            receiver_id INT NOT NULL,
            shared_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (file_id) REFERENCES files(id),
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )
    """)
    print("✓ Table 'shared_files' created/verified")
    
    # Create file_downloads table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_downloads (
            id INT AUTO_INCREMENT PRIMARY KEY,
            file_id INT NOT NULL,
            user_id INT NOT NULL,
            downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (file_id) REFERENCES files(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    print("✓ Table 'file_downloads' created/verified")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n✅ Database setup completed successfully!")
    
except mysql.connector.Error as err:
    print(f"❌ Error: {err}")
    print("\nPlease check your database credentials in .env file")
    print("Make sure MySQL server is running")
