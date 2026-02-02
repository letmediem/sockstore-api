from flask import Flask, jsonify
from flask_cors import CORS
import json
import os

print("=== SOCKSTORE BACKEND STARTING ===")

app = Flask(__name__)
app.json.ensure_ascii = False
CORS(app)

DATA_FILE = 'socks.json'

@app.after_request
def after_request(response):
    if response.content_type.startswith('application/json'):
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

def load_socks():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Loaded {len(data.get('socks', []))} socks")
                return data
        else:
            print(f"File {DATA_FILE} not found, creating default")
            default_data = {"socks": []}
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=2, ensure_ascii=False)
            return default_data
    except Exception as e:
        print(f"Error loading socks: {e}")
        return {"socks": []}

def save_socks(data):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving socks: {e}")
        return False

# ========== API ENDPOINTS ==========

@app.route('/api/health', methods=['GET'])
def health_check():
    print("Health check called")
    return jsonify({"status": "healthy", "service": "sockstore-backend"})

@app.route('/api/socks', methods=['GET'])
def get_socks():
    print("GET /api/socks")
    data = load_socks()
    for sock in data.get('socks', []):
        if 'image' in sock:
            sock['image_url'] = f"/static/images/{sock['image']}"
    return jsonify(data)

@app.route('/api/socks/<int:sock_id>', methods=['GET'])
def get_sock(sock_id):
    print(f"GET /api/socks/{sock_id}")
    data = load_socks()
    for sock in data.get('socks', []):
        if sock['id'] == sock_id:
            if 'image' in sock:
                sock['image_url'] = f"/static/images/{sock['image']}"
            return jsonify(sock)
    return jsonify({"error": "Носки не найдены"}), 404

@app.route('/api/socks/<int:sock_id>/purchase', methods=['POST'])
def purchase_sock(sock_id):
    print(f"POST /api/socks/{sock_id}/purchase")
    data = load_socks()
    socks = data.get('socks', [])
    for sock in socks:
        if sock['id'] == sock_id:
            if not sock.get('inStock', True):
                return jsonify({"error": "Нет в наличии"}), 400
            sock['inStock'] = False
            if save_socks(data):
                if 'image' in sock:
                    sock['image_url'] = f"/static/images/{sock['image']}"
                return jsonify({
                    "message": f"Успешно куплено: {sock['name']}!",
                    "sock": sock
                })
            else:
                return jsonify({"error": "Ошибка сохранения"}), 500
    return jsonify({"error": "Носки не найдены"}), 404

if __name__ == '__main__':
    print("Starting Flask server on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)