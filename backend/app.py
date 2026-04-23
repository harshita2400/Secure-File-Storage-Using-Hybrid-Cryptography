from flask import Flask
from flask_cors import CORS
from routes.file_routes import file_bp
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Secure File Storage Backend Running!"

app.register_blueprint(file_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=True)