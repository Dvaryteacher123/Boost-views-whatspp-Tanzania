from flask import Flask, request, render_template_string
import firebase_admin
from firebase_admin import credentials, firestore
import os

app = Flask(__name__)

# Firebase configuration dictionary kamili
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
    <head><title>Dvary Status Boost</title></head>
    <body>
        <h1>Karibu Dvary</h1>
        <form action="/jiunge" method="POST">
            <input type="text" name="name" placeholder="Jina lako" required><br>
            <input type="text" name="phone" placeholder="Namba ya WhatsApp" required><br>
            <button type="submit">Jiunge na Team</button>
        </form>
    </body>
    </html>
    '''

@app.route('/jiunge', methods=['POST'])
def jiunge():
    name = request.form.get('name')
    phone = request.form.get('phone')
    # Kuhifadhi data kwenye Firestore
    db.collection('teams').document('N4HZPY').collection('members').document(phone).set({
        'name': name,
        'phone': phone
    })
    return "<h1>Hongera! Namba yako imehifadhiwa.</h1><a href='/'>Rudi Nyuma</a>"

if __name__ == '__main__':
    app.run()
