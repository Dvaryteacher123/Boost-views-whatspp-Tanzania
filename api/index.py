from flask import Flask, request, render_template_string
import firebase_admin
from firebase_admin import credentials, firestore
import os

app = Flask(__name__)

# Firebase configuration
firebase_config = {
    "type": "service_account",
    "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
    "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_CERT_URL")
}

# Initialize Firebase
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dvary Boost Views</title>
        <style>
            body { 
                background-color: #000; 
                color: #0F0; 
                font-family: 'Courier New', monospace; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                margin: 0; 
            }
            .container { 
                text-align: center; 
                border: 2px solid #0F0; 
                padding: 50px; 
                border-radius: 20px; 
                width: 90%;
                box-shadow: 0 0 30px #0F0;
            }
            .boost-text { font-size: 1.5rem; color: #fff; margin-bottom: 10px; }
            h1 { font-size: 4rem; margin: 0 0 30px 0; text-shadow: 0 0 20px #0F0; }
            input { 
                display: block; 
                margin: 20px auto; 
                padding: 20px; 
                width: 90%; 
                background: #111; 
                color: #0F0; 
                border: 2px solid #0F0; 
                font-size: 1.5rem; 
                text-align: center;
            }
            button { 
                padding: 20px 50px; 
                font-size: 2rem; 
                background: #0F0; 
                color: #000; 
                border: none; 
                cursor: pointer; 
                font-weight: bold;
                text-transform: uppercase;
            }
            button:hover { background: #0A0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="boost-text">BOOST VIEWS</div>
            <h1>DVARY STATUS</h1>
            <form action="/jiunge" method="POST">
                <input type="text" name="name" placeholder="Jina lako" required>
                <input type="text" name="phone" placeholder="Namba ya WhatsApp" required>
                <button type="submit">JIUNGE SASA</button>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/jiunge', methods=['POST'])
def jiunge():
    name = request.form.get('name')
    phone = request.form.get('phone')
    db.collection('teams').document('N4HZPY').collection('members').document(phone).set({
        'name': name,
        'phone': phone
    })
    return "<h1 style='color:#0F0; text-align:center; font-family:monospace; margin-top:50px;'>SUCCESS! Namba imehifadhiwa.</h1>"

if __name__ == '__main__':
    app.run()
