from flask import Flask, request, make_response
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
            body { background-color: #000; color: #0F0; font-family: 'Courier New', monospace; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
            .container { text-align: center; border: 2px solid #0F0; padding: 40px; border-radius: 20px; width: 85%; box-shadow: 0 0 30px #0F0; }
            h1 { font-size: 2.5rem; margin-bottom: 20px; }
            input { display: block; margin: 15px auto; padding: 15px; width: 90%; background: #111; color: #0F0; border: 2px solid #0F0; font-size: 1.2rem; text-align: center; }
            button { padding: 15px 30px; font-size: 1.5rem; background: #0F0; color: #000; border: none; cursor: pointer; font-weight: bold; width: 90%; }
        </style>
    </head>
    <body>
        <div class="container">
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
    # Hifadhi kwenye Firestore
    db.collection('teams').document('N4HZPY').collection('members').document(phone).set({'name': name, 'phone': phone})
    
    # Baada ya kuhifadhi, muonyeshe kitufe cha download
    return '''
    <h1 style='color:#0F0; text-align:center; font-family:monospace; margin-top:50px;'>SUCCESS! Namba imehifadhiwa.</h1>
    <div style="text-align:center;">
        <a href="/download" style="padding:20px; background:#008CBA; color:#fff; text-decoration:none; font-size:1.5rem; border-radius:10px;">PAKUA ORODHA YA WANACHAMA</a>
        <br><br><br>
        <a href="/" style="color:#FFF;">Rudi Nyuma</a>
    </div>
    '''

@app.route('/download')
def download_contacts():
    members = db.collection('teams').document('N4HZPY').collection('members').stream()
    vcf_content = ""
    for member in members:
        data = member.to_dict()
        vcf_content += f"BEGIN:VCARD\nVERSION:3.0\nFN:{data.get('name')}\nTEL;TYPE=CELL:{data.get('phone')}\nEND:VCARD\n"
    
    response = make_response(vcf_content)
    response.headers["Content-Disposition"] = "attachment; filename=Dvary_Contacts.vcf"
    response.headers["Content-Type"] = "text/vcard"
    return response

if __name__ == '__main__':
    app.run(debug=True)
