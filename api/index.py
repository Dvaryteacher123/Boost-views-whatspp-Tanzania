from flask import Flask, request, render_template_string
import firebase_admin
from firebase_admin import credentials, firestore
import os

app = Flask(__name__)

# Firebase Initialization
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
    "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
})
firebase_admin.initialize_app(cred)
db = firestore.client()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { transition: background 0.3s, color 0.3s; padding: 20px; font-family: sans-serif; }
        .dark-mode { background: #121212; color: white; }
        .light-mode { background: #f4f4f4; color: black; }
        input { display: block; margin: 10px 0; padding: 10px; width: 100%; max-width: 300px; }
        button { padding: 10px 20px; cursor: pointer; }
    </style>
</head>
<body class="light-mode">
    <button onclick="toggleTheme()">Badilisha Rangi</button>
    <h1>Jiunge na Status Boost</h1>
    <form action="/jiunge" method="POST">
        <input type="text" name="name" placeholder="Jina lako" required>
        <input type="text" name="phone" placeholder="Namba (mfano: 2557...)" required>
        <input type="hidden" name="team_id" value="N4HZPY">
        <button type="submit">Jiunge na Team</button>
    </form>
    <script>
        function toggleTheme() {
            document.body.classList.toggle('dark-mode');
            document.body.classList.toggle('light-mode');
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/jiunge', methods=['POST'])
def jiunge():
    name = request.form.get('name')
    phone = request.form.get('phone')
    db.collection('teams').document('N4HZPY').collection('members').document(phone).set({'name': name, 'phone': phone})
    return "<h1>Hongera! Umejiunga na timu.</h1><a href='/'>Rudi Nyuma</a>"

