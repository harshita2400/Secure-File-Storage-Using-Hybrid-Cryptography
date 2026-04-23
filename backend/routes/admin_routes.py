from flask import Blueprint, jsonify
from database import get_connection

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get total users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        users_count = cursor.fetchone()['count']
        
        # Get total files (count encrypted blocks)
        cursor.execute("SELECT COUNT(*) as count FROM files")
        files_count = cursor.fetchone()['count']
        
        # Get total shares
        cursor.execute("SELECT COUNT(*) as count FROM file_shares")
        shares_count = cursor.fetchone()['count']
        
        # Get total downloads
        cursor.execute("SELECT COUNT(*) as count FROM file_downloads")
        downloads_count = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "users": users_count,
            "files": files_count,
            "shares": shares_count,
            "downloads": downloads_count
        })
        
    except Exception as e:
        return jsonify({
            "users": 0,
            "files": 0,
            "shares": 0,
            "downloads": 0
        })
