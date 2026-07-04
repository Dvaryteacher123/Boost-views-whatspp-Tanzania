from flask import Flask, request, make_response, render_template_string, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import os
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

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="sw">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dvary Boost Views</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            position: relative;
            overflow-x: hidden;
        }

        /* Rain Background */
        .rain {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
        }

        .rain-drop {
            position: absolute;
            background: rgba(255, 255, 255, 0.3);
            width: 2px;
            animation: rainFall linear infinite;
        }

        @keyframes rainFall {
            0% {
                transform: translateY(-100vh) rotate(10deg);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            100% {
                transform: translateY(100vh) rotate(10deg);
                opacity: 0;
            }
        }

        /* Top Bar */
        .top-bar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 1000;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }

        .top-bar .brand {
            color: #fff;
            font-size: 1.3rem;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .top-bar .brand .icon {
            font-size: 1.8rem;
        }

        /* Hamburger Menu */
        .hamburger {
            cursor: pointer;
            padding: 10px;
            background: transparent;
            border: none;
            outline: none;
        }

        .hamburger span {
            display: block;
            width: 28px;
            height: 3px;
            background: #fff;
            margin: 6px 0;
            border-radius: 3px;
            transition: 0.4s;
        }

        .hamburger.active span:nth-child(1) {
            transform: rotate(-45deg) translate(-5px, 6px);
        }

        .hamburger.active span:nth-child(2) {
            opacity: 0;
        }

        .hamburger.active span:nth-child(3) {
            transform: rotate(45deg) translate(-5px, -6px);
        }

        /* Side Menu */
        .side-menu {
            position: fixed;
            top: 0;
            right: -300px;
            width: 280px;
            height: 100vh;
            background: rgba(0, 0, 0, 0.95);
            backdrop-filter: blur(20px);
            z-index: 999;
            transition: 0.4s;
            padding: 80px 20px 20px;
            overflow-y: auto;
        }

        .side-menu.open {
            right: 0;
        }

        .side-menu .menu-item {
            display: block;
            color: #fff;
            padding: 15px 20px;
            margin: 10px 0;
            text-decoration: none;
            border-radius: 10px;
            transition: 0.3s;
            font-size: 1.1rem;
            border-left: 3px solid transparent;
        }

        .side-menu .menu-item:hover {
            background: rgba(255, 255, 255, 0.1);
            border-left-color: #ff6b6b;
            transform: translateX(5px);
        }

        .side-menu .menu-item .emoji {
            margin-right: 12px;
        }

        /* Overlay */
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 998;
            display: none;
        }

        .overlay.show {
            display: block;
        }

        /* Main Container */
        .container {
            position: relative;
            z-index: 1;
            max-width: 500px;
            margin: 100px auto 30px;
            padding: 20px;
        }

        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            animation: slideUp 0.6s ease;
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(40px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .card h2 {
            color: #fff;
            font-size: 1.8rem;
            text-align: center;
            margin-bottom: 20px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }

        .card .subtitle {
            color: rgba(255,255,255,0.8);
            text-align: center;
            margin-bottom: 25px;
            font-size: 0.95rem;
        }

        /* Form */
        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            color: #fff;
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }

        .form-group input {
            width: 100%;
            padding: 15px;
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 12px;
            background: rgba(255,255,255,0.1);
            color: #fff;
            font-size: 1rem;
            transition: 0.3s;
            outline: none;
        }

        .form-group input:focus {
            border-color: #ff6b6b;
            background: rgba(255,255,255,0.15);
        }

        .form-group input::placeholder {
            color: rgba(255,255,255,0.5);
        }

        .btn-primary {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: #fff;
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .btn-primary:hover {
            transform: scale(1.02);
            box-shadow: 0 10px 30px rgba(255, 107, 107, 0.4);
        }

        .btn-primary:active {
            transform: scale(0.98);
        }

        .btn-success {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #00b894, #00a381);
            color: #fff;
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .btn-success:hover {
            transform: scale(1.02);
            box-shadow: 0 10px 30px rgba(0, 184, 148, 0.4);
        }

        /* Download Section */
        .download-section {
            text-align: center;
            padding: 20px;
        }

        .download-section .icon {
            font-size: 4rem;
            margin-bottom: 10px;
            display: block;
        }

        .download-section h3 {
            color: #fff;
            margin-bottom: 10px;
        }

        .download-section p {
            color: rgba(255,255,255,0.8);
            font-size: 0.9rem;
            margin-bottom: 15px;
        }

        .instructions {
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 12px;
            margin-top: 15px;
            text-align: left;
        }

        .instructions ol {
            color: rgba(255,255,255,0.8);
            padding-left: 20px;
            margin: 10px 0;
        }

        .instructions ol li {
            margin: 8px 0;
        }

        /* Success Message */
        .success-msg {
            background: rgba(0, 184, 148, 0.2);
            border: 2px solid #00b894;
            border-radius: 12px;
            padding: 15px;
            color: #fff;
            text-align: center;
            margin-bottom: 20px;
            display: none;
        }

        .success-msg.show {
            display: block;
            animation: pulse 1s ease;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }

        /* Badge */
        .badge {
            display: inline-block;
            background: rgba(255, 107, 107, 0.3);
            padding: 5px 15px;
            border-radius: 20px;
            color: #ff6b6b;
            font-size: 0.8rem;
            margin-top: 10px;
        }

        /* Responsive */
        @media (max-width: 600px) {
            .container {
                padding: 15px;
                margin-top: 80px;
            }
            .card {
                padding: 20px;
            }
            .side-menu {
                width: 260px;
            }
            .top-bar .brand {
                font-size: 1rem;
            }
        }
    </style>
</head>
<body>

    <!-- Rain Background -->
    <div class="rain" id="rain"></div>

    <!-- Top Bar -->
    <div class="top-bar">
        <div class="brand">
            <span class="icon">🚀</span>
            <span>Dvary Boost</span>
        </div>
        <button class="hamburger" onclick="toggleMenu()">
            <span></span>
            <span></span>
            <span></span>
        </button>
    </div>

    <!-- Overlay -->
    <div class="overlay" onclick="toggleMenu()"></div>

    <!-- Side Menu -->
    <div class="side-menu" id="sideMenu">
        <a href="#" class="menu-item" onclick="toggleMenu()">
            <span class="emoji">🏠</span> Nyumbani
        </a>
        <a href="#about" class="menu-item" onclick="toggleMenu()">
            <span class="emoji">ℹ️</span> About
        </a>
        <a href="#boost" class="menu-item" onclick="toggleMenu()">
            <span class="emoji">📈</span> Boost Followers
        </a>
        <a href="#download" class="menu-item" onclick="toggleMenu()">
            <span class="emoji">⬇️</span> Download Views
        </a>
        <a href="https://whatsapp.com/channel/0029VbCRC9b5fM5cruU8PF2M" target="_blank" class="menu-item" onclick="toggleMenu()">
            <span class="emoji">📢</span> Join Channel
        </a>
        <div style="border-top: 1px solid rgba(255,255,255,0.1); margin-top: 20px; padding-top: 20px;">
            <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem; text-align: center;">
                &copy; 2026 Dvary Boost<br>
                Made with ❤️ in Tanzania
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="container">
        <!-- Join Form -->
        <div class="card" id="joinForm">
            <h2>🔥 DVARY BOOST</h2>
            <p class="subtitle">Jiunge sasa na upate <strong>Views & Followers</strong></p>
            
            <div class="success-msg" id="successMsg">
                ✅ Umejiunga kikamilifu! Sasa pakua views zako.
            </div>

            <form id="joinFormSubmit" onsubmit="submitJoin(event)">
                <div class="form-group">
                    <label>👤 Jina Lako</label>
                    <input type="text" id="name" placeholder="Andika jina lako" required>
                </div>
                <div class="form-group">
                    <label>📱 Namba ya WhatsApp</label>
                    <input type="text" id="phone" placeholder="+255 700 000 000" required>
                </div>
                <button type="submit" class="btn-primary">
                    🚀 JIUNGE SASA
                </button>
            </form>
        </div>

        <!-- Download Section -->
        <div class="card" id="downloadSection" style="display: none;">
            <div class="download-section">
                <span class="icon">⬇️</span>
                <h3>PAKUA VIEWS ZAKO</h3>
                <p>Bonyeza hapa chini kupakua orodha ya wanachama</p>
                <button onclick="downloadViews()" class="btn-success">
                    📥 DOWNLOAD VIEWS
                </button>
                
                <div class="instructions">
                    <strong>📌 Maelekezo:</strong>
                    <ol>
                        <li>Bonyeza kitufe cha <strong>"DOWNLOAD VIEWS"</strong></li>
                        <li>Faili ya <strong>.vcf</strong> itapakua kwenye simu yako</li>
                        <li>Fungua faili na uchague <strong>WhatsApp</strong></li>
                        <li>Wanachama wote wataongezwa kwenye WhatsApp yako</li>
                        <li>Anza kuona <strong>Views na Followers</strong> zikiongezeka!</li>
                    </ol>
                    <span class="badge">💡 Tip: Pakua mara moja tu</span>
                </div>
            </div>
        </div>

        <!-- Boost Followers Section -->
        <div class="card" id="boost">
            <h2>📈 BOOST FOLLOWERS</h2>
            <p class="subtitle">Pata mafanikio makubwa kwenye mitandao yako</p>
            <div style="text-align: center; color: rgba(255,255,255,0.8);">
                <div style="font-size: 2.5rem; margin: 15px 0;">🚀</div>
                <p style="margin: 10px 0;"><strong>✅ 1000+ Views</strong> kwa siku</p>
                <p style="margin: 10px 0;"><strong>✅ 500+ Followers</strong> kila wiki</p>
                <p style="margin: 10px 0;"><strong>✅ 24/7 Support</strong> kwa WhatsApp</p>
                <br>
                <a href="https://whatsapp.com/channel/0029VbCRC9b5fM5cruU8PF2M" target="_blank" style="color: #ff6b6b; text-decoration: none; font-weight: bold;">
                    📢 Jiunge na Channel Yetu
                </a>
            </div>
        </div>

        <!-- About Section -->
        <div class="card" id="about">
            <h2>ℹ️ ABOUT US</h2>
            <p class="subtitle">Kuhusu Dvary Boost Views</p>
            <div style="color: rgba(255,255,255,0.8); line-height: 1.8;">
                <p><strong>Dvary Boost Views</strong> ni jukwaa la kusaidia watu kuongeza mtazamo wa WhatsApp status, kujenga biashara na kuongeza mauzo kupitia mitandao ya kijamii.</p>
                <br>
                <p><strong>📞 Wasiliana Nasi:</strong></p>
                <p>📱 <a href="https://wa.me/255712345678" style="color: #00b894; text-decoration: none;">+255 712 345 678</a></p>
                <p>✉️ dvaryboost@gmail.com</p>
                <br>
                <p><strong>👤 Mwanzilishi:</strong> Dvary Team</p>
            </div>
        </div>
    </div>

    <script>
        // Generate Rain
        function createRain() {
            const rainContainer = document.getElementById('rain');
            const drops = 100;
            for (let i = 0; i < drops; i++) {
                const drop = document.createElement('div');
                drop.className = 'rain-drop';
                drop.style.left = Math.random() * 100 + '%';
                drop.style.height = (Math.random() * 30 + 20) + 'px';
                drop.style.animationDuration = (Math.random() * 2 + 1) + 's';
                drop.style.animationDelay = (Math.random() * 3) + 's';
                drop.style.opacity = Math.random() * 0.5 + 0.2;
                rainContainer.appendChild(drop);
            }
        }
        createRain();

        // Toggle Menu
        function toggleMenu() {
            const menu = document.getElementById('sideMenu');
            const overlay = document.querySelector('.overlay');
            const hamburger = document.querySelector('.hamburger');
            
            menu.classList.toggle('open');
            overlay.classList.toggle('show');
            hamburger.classList.toggle('active');
        }

        // Close menu on ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                const menu = document.getElementById('sideMenu');
                if (menu.classList.contains('open')) {
                    toggleMenu();
                }
            }
        });

        // Submit Join Form
        function submitJoin(e) {
            e.preventDefault();
            
            const name = document.getElementById('name').value.trim();
            const phone = document.getElementById('phone').value.trim();

            if (!name || !phone) {
                alert('⚠️ Tafadhali jaza nafasi zote!');
                return;
            }

            // Send to server
            fetch('/jiunge', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `name=${encodeURIComponent(name)}&phone=${encodeURIComponent(phone)}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    document.getElementById('successMsg').classList.add('show');
                    document.getElementById('joinFormSubmit').style.display = 'none';
                    
                    // Show download section
                    document.getElementById('downloadSection').style.display = 'block';
                    document.getElementById('downloadSection').scrollIntoView({ behavior: 'smooth' });
                    
                    // Disable form fields
                    document.getElementById('name').disabled = true;
                    document.getElementById('phone').disabled = true;
                }
            })
            .catch(error => {
                alert('❌ Kuna hitilafu, tafadhali jaribu tena!');
                console.error('Error:', error);
            });
        }

        // Download Views
        function downloadViews() {
            // Force download by redirecting to download endpoint
            window.location.href = '/download';
            
            // Show feedback
            const btn = document.querySelector('.btn-success');
            const originalText = btn.textContent;
            btn.textContent = '✅ IMEPAKUA!';
            setTimeout(() => {
                btn.textContent = originalText;
            }, 3000);
        }

        // Auto-show download if already joined (check from localStorage)
        document.addEventListener('DOMContentLoaded', function() {
            const joined = localStorage.getItem('dvary_joined');
            if (joined === 'true') {
                document.getElementById('downloadSection').style.display = 'block';
                document.getElementById('joinFormSubmit').style.display = 'none';
                document.getElementById('successMsg').classList.add('show');
                document.getElementById('successMsg').textContent = '✅ Umeshajiunga! Pakua views zako hapa chini.';
            }
        });
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
    
    try:
        # Save to Firestore
        db.collection('teams').document('N4HZPY').collection('members').document(phone).set({
            'name': name,
            'phone': phone,
            'joined_at': datetime.now().isoformat()
        })
        return jsonify({'success': True, 'message': 'Umejiunga kikamilifu!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/download')
def download_contacts():
    members = db.collection('teams').document('N4HZPY').collection('members').stream()
    vcf_content = "BEGIN:VCARD\nVERSION:3.0\n"
    for member in members:
        data = member.to_dict()
        vcf_content += f"FN:{data.get('name')}\nTEL;TYPE=CELL:{data.get('phone')}\n"
    vcf_content += "END:VCARD"
    
    response = make_response(vcf_content)
    response.headers["Content-Disposition"] = "attachment; filename=Dvary_Views.vcf"
    response.headers["Content-Type"] = "text/vcard"
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
