from flask import Flask, request, render_template_string
import firebase_admin
from firebase_admin import credentials, firestore
import os

app = Flask(__name__)

# Firebase setup
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
    "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
})
firebase_admin.initialize_app(cred)
db = firestore.client()

# Hapa ndipo HTML yako inakaa
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Dvary Status Boost</title></head>
    <body>
        <h1>Karibu kwenye Dvary</h1>
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
    db.collection('teams').document('N4HZPY').collection('members').document(phone).set({
        'name': name,
        'phone': phone
    })
    return "Hongera! Namba yako imehifadhiwa."

if __name__ == '__main__':
    app.run()

