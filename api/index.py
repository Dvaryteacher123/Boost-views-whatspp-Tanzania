from flask import Flask, request, make_response, render_template_string
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from datetime import datetime

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

# HTML template with all features
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="sw">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dvary Boost Views</title>
    <style>
        :root {
            --bg-color: #000;
            --text-color: #0F0;
            --border-color: #0F0;
            --shadow-color: #0F0;
            --card-bg: #111;
            --input-bg: #111;
            --button-bg: #0F0;
            --button-text: #000;
            --whatsapp-color: #25D366;
        }
        
        [data-theme="light"] {
            --bg-color: #f0f0f0;
            --text-color: #333;
            --border-color: #25D366;
            --shadow-color: #25D366;
            --card-bg: #fff;
            --input-bg: #fff;
            --button-bg: #25D366;
            --button-text: #fff;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            transition: all 0.3s ease;
        }
        
        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            padding: 20px;
        }
        
        .navbar {
            background: var(--card-bg);
            padding: 15px 20px;
            border-radius: 15px;
            border: 2px solid var(--border-color);
            box-shadow: 0 0 30px var(--shadow-color);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .navbar-brand {
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--border-color);
            text-decoration: none;
        }
        
        .navbar-menu {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .nav-btn {
            padding: 10px 20px;
            background: transparent;
            color: var(--text-color);
            border: 2px solid var(--border-color);
            border-radius: 10px;
            cursor: pointer;
            font-size: 1rem;
            transition: 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        
        .nav-btn:hover, .nav-btn.active {
            background: var(--border-color);
            color: var(--bg-color);
            transform: scale(1.05);
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .page {
            display: none;
            animation: fadeIn 0.5s ease;
        }
        
        .page.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .card {
            background: var(--card-bg);
            border: 2px solid var(--border-color);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 0 30px var(--shadow-color);
            margin-bottom: 20px;
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 20px;
            color: var(--border-color);
            text-align: center;
        }
        
        h2 {
            font-size: 2rem;
            margin-bottom: 15px;
            color: var(--border-color);
        }
        
        input, select {
            display: block;
            margin: 15px auto;
            padding: 15px;
            width: 100%;
            background: var(--input-bg);
            color: var(--text-color);
            border: 2px solid var(--border-color);
            border-radius: 10px;
            font-size: 1.2rem;
            text-align: center;
        }
        
        button {
            padding: 15px 30px;
            font-size: 1.3rem;
            background: var(--button-bg);
            color: var(--button-text);
            border: none;
            cursor: pointer;
            font-weight: bold;
            width: 100%;
            border-radius: 10px;
            transition: 0.3s;
        }
        
        button:hover {
            transform: scale(1.02);
            box-shadow: 0 0 20px var(--border-color);
        }
        
        .whatsapp-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .whatsapp-item {
            background: var(--card-bg);
            border: 2px solid var(--whatsapp-color);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            transition: 0.3s;
        }
        
        .whatsapp-item:hover {
            transform: translateY(-5px);
            box-shadow: 0 0 20px var(--whatsapp-color);
        }
        
        .whatsapp-item .icon {
            font-size: 3rem;
            margin-bottom: 10px;
        }
        
        .whatsapp-item .label {
            font-size: 0.9rem;
            color: var(--text-color);
        }
        
        .whatsapp-item .number {
            font-size: 1.1rem;
            font-weight: bold;
            color: var(--whatsapp-color);
        }
        
        .about-content {
            line-height: 1.8;
        }
        
        .about-content p {
            margin-bottom: 15px;
            font-size: 1.1rem;
        }
        
        .channel-link {
            display: inline-block;
            padding: 15px 30px;
            background: var(--whatsapp-color);
            color: #fff;
            text-decoration: none;
            border-radius: 10px;
            font-weight: bold;
            margin: 15px 0;
            transition: 0.3s;
        }
        
        .channel-link:hover {
            transform: scale(1.05);
            box-shadow: 0 0 30px var(--whatsapp-color);
        }
        
        .contact-info {
            background: var(--input-bg);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid var(--border-color);
            margin: 15px 0;
        }
        
        .status-badge {
            display: inline-block;
            padding: 10px 20px;
            background: var(--border-color);
            color: var(--bg-color);
            border-radius: 20px;
            font-weight: bold;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            border-top: 2px solid var(--border-color);
            font-size: 0.9rem;
        }
        
        .language-selector, .theme-selector {
            display: inline-block;
            margin: 0 10px;
        }
        
        .language-selector select, .theme-selector select {
            padding: 8px 15px;
            border-radius: 10px;
            background: var(--input-bg);
            color: var(--text-color);
            border: 2px solid var(--border-color);
            font-size: 0.9rem;
            margin: 0;
            width: auto;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        @media (max-width: 600px) {
            .navbar {
                flex-direction: column;
                align-items: stretch;
            }
            .navbar-menu {
                justify-content: center;
            }
            .card {
                padding: 20px;
            }
            h1 {
                font-size: 2rem;
            }
            .whatsapp-grid {
                grid-template-columns: 1fr 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Navigation Bar -->
        <nav class="navbar">
            <a href="#" class="navbar-brand" onclick="showPage('home')">DVARY</a>
            <div class="navbar-menu">
                <button class="nav-btn active" onclick="showPage('home')">🏠 Nyumbani</button>
                <button class="nav-btn" onclick="showPage('about')">ℹ️ About</button>
                <button class="nav-btn" onclick="showPage('status')">📊 Status</button>
            </div>
            <div class="controls">
                <div class="language-selector">
                    <select onchange="changeLanguage(this.value)">
                        <option value="sw">🇹🇿 Kiswahili</option>
                        <option value="en">🇬🇧 English</option>
                    </select>
                </div>
                <div class="theme-selector">
                    <select onchange="changeTheme(this.value)">
                        <option value="dark">🌙 Dark</option>
                        <option value="light">☀️ Light</option>
                    </select>
                </div>
            </div>
        </nav>

        <!-- Home Page -->
        <div id="home" class="page active">
            <div class="card">
                <h1>DVARY STATUS</h1>
                <p style="text-align:center; margin-bottom:20px;">Jiunge na timu yetu na upate mafanikio makubwa!</p>
                <form action="/jiunge" method="POST">
                    <input type="text" name="name" placeholder="Jina lako" required>
                    <input type="text" name="phone" placeholder="Namba ya WhatsApp" required>
                    <button type="submit">JIUNGE SASA</button>
                </form>
            </div>
            
            <!-- WhatsApp Groups Section -->
            <div class="card">
                <h2>📱 WhatsApp Groups</h2>
                <div class="whatsapp-grid">
                    <div class="whatsapp-item">
                        <div class="icon">💬</div>
                        <div class="label">Group 1</div>
                        <div class="number">+255 712 345 678</div>
                    </div>
                    <div class="whatsapp-item">
                        <div class="icon">💬</div>
                        <div class="label">Group 2</div>
                        <div class="number">+255 712 345 679</div>
                    </div>
                    <div class="whatsapp-item">
                        <div class="icon">💬</div>
                        <div class="label">Group 3</div>
                        <div class="number">+255 712 345 680</div>
                    </div>
                    <div class="whatsapp-item">
                        <div class="icon">💬</div>
                        <div class="label">Group 4</div>
                        <div class="number">+255 712 345 681</div>
                    </div>
                    <div class="whatsapp-item">
                        <div class="icon">💬</div>
                        <div class="label">Group 5</div>
                        <div class="number">+255 712 345 682</div>
                    </div>
                    <div class="whatsapp-item">
                        <div class="icon">💬</div>
                        <div class="label">Group 6</div>
                        <div class="number">+255 712 345 683</div>
                    </div>
                </div>
                <p style="text-align:center; font-size:0.9rem; margin-top:15px;">
                    💡 Bofya nambari kuongeza kwenye WhatsApp
                </p>
            </div>
        </div>

        <!-- About Page -->
        <div id="about" class="page">
            <div class="card">
                <h2>ℹ️ About Dvary Boost Views</h2>
                <div class="about-content">
                    <p>
                        <strong>Dvary Boost Views</strong> ni jukwaa la kusaidia watu kuongeza mtazamo wa 
                        WhatsApp status, kujenga biashara na kuongeza mauzo kupitia mitandao ya kijamii.
                    </p>
                    <p>
                        Tumejenga jamii kubwa ya watu wanaosaidiana katika masoko ya kidijitali, 
                        kujifunza na kukua pamoja.
                    </p>
                    
                    <div class="contact-info">
                        <h3>📞 Wasiliana Nasi</h3>
                        <p><strong>Jina:</strong> Dvary Boost</p>
                        <p><strong>WhatsApp:</strong> <span style="color: var(--whatsapp-color);">+255 712 345 678</span></p>
                        <p><strong>Email:</strong> dvaryboost@gmail.com</p>
                    </div>
                    
                    <div style="text-align:center; margin: 20px 0;">
                        <a href="https://whatsapp.com/channel/0029VbCRC9b5fM5cruU8PF2M" 
                           target="_blank" 
                           class="channel-link">
                            📢 Jiunge na Channel Yetu
                        </a>
                        <p style="font-size:0.9rem; margin-top:10px;">
                            Pata taarifa na mafunzo ya kila siku kwenye channel yetu
                        </p>
                    </div>
                    
                    <p style="text-align:center; margin-top:20px;">
                        <span class="status-badge">✅ Tuko Hapa Kukusaidia</span>
                    </p>
                </div>
            </div>
        </div>

        <!-- Status Page -->
        <div id="status" class="page">
            <div class="card">
                <h2>📊 Status ya Timu</h2>
                <div style="text-align:center; padding:20px;">
                    <p style="font-size:1.2rem; margin-bottom:20px;">
                        Idadi ya Wanachama: <strong id="member-count">0</strong>
                    </p>
                    <p style="font-size:1.2rem; margin-bottom:20px;">
                        Status: <span class="status-badge" style="background: var(--whatsapp-color);">Inaendelea</span>
                    </p>
                    <div style="margin:20px 0;">
                        <a href="/download" class="channel-link" style="background: var(--border-color); color: var(--bg-color);">
                            ⬇️ PAKUA ORODHA YA WANACHAMA
                        </a>
                    </div>
                    <p style="font-size:0.9rem;">
                        💾 VCF file itakusaidia kuongeza wanachama kwenye simu yako
                    </p>
                </div>
            </div>
        </div>

        <div class="footer">
            &copy; 2026 Dvary Boost Views | Made with ❤️ in Tanzania
        </div>
    </div>

    <script>
        // Page navigation
        function showPage(pageId) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById(pageId).classList.add('active');
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(b => {
                if(b.textContent.includes(pageId === 'home' ? 'Nyumbani' : 
                   pageId === 'about' ? 'About' : 'Status')) {
                    b.classList.add('active');
                }
            });
        }

        // Change language
        function changeLanguage(lang) {
            const texts = {
                'sw': {
                    'home': '🏠 Nyumbani',
                    'about': 'ℹ️ About',
                    'status': '📊 Status',
                    'title': 'DVARY STATUS',
                    'join': 'JIUNGE SASA',
                    'name': 'Jina lako',
                    'phone': 'Namba ya WhatsApp'
                },
                'en': {
                    'home': '🏠 Home',
                    'about': 'ℹ️ About',
                    'status': '📊 Status',
                    'title': 'DVARY STATUS',
                    'join': 'JOIN NOW',
                    'name': 'Your Name',
                    'phone': 'WhatsApp Number'
                }
            };
            
            const t = texts[lang] || texts['sw'];
            document.querySelector('h1').textContent = t.title;
            document.querySelector('button[type="submit"]').textContent = t.join;
            document.querySelector('input[name="name"]').placeholder = t.name;
            document.querySelector('input[name="phone"]').placeholder = t.phone;
            
            document.querySelectorAll('.nav-btn').forEach(b => {
                if(b.textContent.includes('Nyumbani') || b.textContent.includes('Home')) {
                    b.textContent = t.home;
                } else if(b.textContent.includes('About')) {
                    b.textContent = t.about;
                } else if(b.textContent.includes('Status')) {
                    b.textContent = t.status;
                }
            });
        }

        // Change theme
        function changeTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
        }

        // Load saved theme
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        document.querySelector('.theme-selector select').value = savedTheme;

        // Get member count from server
        fetch('/member-count')
            .then(response => response.json())
            .then(data => {
                document.getElementById('member-count').textContent = data.count;
            })
            .catch(err => console.error('Error fetching count:', err));
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
    
    # Save to Firestore
    db.collection('teams').document('N4HZPY').collection('members').document(phone).set({
        'name': name, 
        'phone': phone,
        'joined_at': datetime.now().isoformat()
    })
    
    # Return success with redirect back to home
    return '''
    <script>
        alert('✅ Namba imehifadhiwa! Umefanikiwa kujiunga.');
        window.location.href = '/';
    </script>
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

@app.route('/member-count')
def member_count():
    members = db.collection('teams').document('N4HZPY').collection('members').stream()
    count = sum(1 for _ in members)
    return {'count': count}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
