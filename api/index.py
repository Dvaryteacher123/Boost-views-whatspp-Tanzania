from flask import Flask, request, make_response, render_template_string, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import os
from datetime import datetime

app = Flask(__name__)

# Firebase configuration
firebase_config = {
    "type": "service_account",
    "project_id": "dvary-9a7d0",
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
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
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
            background: linear-gradient(180deg, rgba(255,255,255,0.1), rgba(255,255,255,0.3));
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
            background: rgba(15, 12, 41, 0.95);
            backdrop-filter: blur(10px);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 1000;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            border-bottom: 2px solid rgba(255, 107, 107, 0.3);
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
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }

        .top-bar .user-info {
            color: rgba(255,255,255,0.7);
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .top-bar .user-info .logout-btn {
            padding: 8px 15px;
            background: rgba(255, 107, 107, 0.2);
            border: 1px solid #ff6b6b;
            border-radius: 8px;
            color: #ff6b6b;
            cursor: pointer;
            transition: 0.3s;
        }

        .top-bar .user-info .logout-btn:hover {
            background: #ff6b6b;
            color: #fff;
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
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.08);
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
            font-size: 2rem;
            text-align: center;
            margin-bottom: 10px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }

        .card .subtitle {
            color: rgba(255,255,255,0.7);
            text-align: center;
            margin-bottom: 25px;
            font-size: 0.95rem;
        }

        .glow-text {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24, #ff6b6b);
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: glow 3s ease-in-out infinite;
        }

        @keyframes glow {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }

        /* Form */
        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            color: rgba(255,255,255,0.9);
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            font-size: 0.95rem;
        }

        .form-group input {
            width: 100%;
            padding: 15px;
            border: 2px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            background: rgba(255,255,255,0.05);
            color: #fff;
            font-size: 1rem;
            transition: 0.3s;
            outline: none;
        }

        .form-group input:focus {
            border-color: #ff6b6b;
            background: rgba(255,255,255,0.1);
            box-shadow: 0 0 20px rgba(255, 107, 107, 0.1);
        }

        .form-group input::placeholder {
            color: rgba(255,255,255,0.3);
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

        .btn-primary:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .btn-secondary {
            width: 100%;
            padding: 16px;
            background: transparent;
            color: #fff;
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .btn-secondary:hover {
            background: rgba(255,255,255,0.05);
            border-color: #ff6b6b;
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

        /* Auth Pages */
        .auth-page {
            display: block;
        }

        .auth-page.hidden {
            display: none;
        }

        .auth-toggle {
            text-align: center;
            margin-top: 15px;
            color: rgba(255,255,255,0.5);
        }

        .auth-toggle a {
            color: #ff6b6b;
            cursor: pointer;
            text-decoration: none;
            font-weight: bold;
        }

        .auth-toggle a:hover {
            text-decoration: underline;
        }

        /* Main App */
        .app-content {
            display: none;
        }

        .app-content.show {
            display: block;
        }

        /* Download Section */
        .download-section {
            text-align: center;
            padding: 10px 0;
        }

        .download-section .icon {
            font-size: 4rem;
            margin-bottom: 10px;
            display: block;
            animation: bounce 2s ease-in-out infinite;
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        .download-section h3 {
            color: #fff;
            margin-bottom: 10px;
        }

        .download-section p {
            color: rgba(255,255,255,0.7);
            font-size: 0.95rem;
            margin-bottom: 15px;
        }

        .instructions {
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 12px;
            margin-top: 15px;
            text-align: left;
            border: 1px solid rgba(255,255,255,0.05);
        }

        .instructions strong {
            color: #ff6b6b;
        }

        .instructions ol {
            color: rgba(255,255,255,0.8);
            padding-left: 20px;
            margin: 10px 0;
        }

        .instructions ol li {
            margin: 8px 0;
        }

        .badge {
            display: inline-block;
            background: rgba(255, 107, 107, 0.2);
            padding: 5px 15px;
            border-radius: 20px;
            color: #ff6b6b;
            font-size: 0.8rem;
            margin-top: 10px;
            border: 1px solid rgba(255, 107, 107, 0.2);
        }

        /* Contact Cards */
        .contact-card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 15px;
            margin: 10px 0;
            display: flex;
            align-items: center;
            gap: 15px;
            border: 1px solid rgba(255,255,255,0.05);
            transition: 0.3s;
        }

        .contact-card:hover {
            background: rgba(255,255,255,0.08);
            transform: translateX(5px);
        }

        .contact-card .contact-icon {
            font-size: 2rem;
        }

        .contact-card .contact-info {
            flex: 1;
        }

        .contact-card .contact-info .label {
            color: rgba(255,255,255,0.5);
            font-size: 0.8rem;
        }

        .contact-card .contact-info .value {
            color: #fff;
            font-size: 1rem;
            font-weight: 500;
        }

        .contact-card .contact-info .value a {
            color: #ff6b6b;
            text-decoration: none;
        }

        .contact-card .contact-info .value a:hover {
            text-decoration: underline;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin: 15px 0;
        }

        .stat-item {
            text-align: center;
            padding: 15px;
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
        }

        .stat-item .number {
            font-size: 1.8rem;
            font-weight: bold;
            color: #ff6b6b;
        }

        .stat-item .label {
            font-size: 0.8rem;
            color: rgba(255,255,255,0.5);
            margin-top: 5px;
        }

        .channel-btn {
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(135deg, #25D366, #128C7E);
            color: #fff;
            text-decoration: none;
            border-radius: 12px;
            font-weight: bold;
            transition: 0.3s;
            margin: 10px 0;
        }

        .channel-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 10px 30px rgba(37, 211, 102, 0.3);
        }

        .success-msg {
            background: rgba(0, 184, 148, 0.15);
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

        .error-msg {
            background: rgba(255, 107, 107, 0.15);
            border: 2px solid #ff6b6b;
            border-radius: 12px;
            padding: 15px;
            color: #fff;
            text-align: center;
            margin-bottom: 20px;
            display: none;
        }

        .error-msg.show {
            display: block;
            animation: shake 0.5s ease;
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }

        .loading-spinner {
            display: none;
            text-align: center;
            margin: 10px 0;
        }

        .loading-spinner.show {
            display: block;
        }

        .spinner {
            border: 3px solid rgba(255,255,255,0.1);
            border-top: 3px solid #ff6b6b;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 0.8s linear infinite;
            margin: 0 auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
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
            .top-bar .brand {
                font-size: 1rem;
            }
            .top-bar .user-info {
                font-size: 0.8rem;
            }
            .stats-grid {
                grid-template-columns: repeat(3, 1fr);
                gap: 8px;
            }
            .stat-item .number {
                font-size: 1.2rem;
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
            <span>Dvary <span style="color: #ff6b6b;">Boost</span></span>
        </div>
        <div class="user-info" id="userInfo" style="display: none;">
            <span id="userEmail">user@email.com</span>
            <button class="logout-btn" onclick="logout()">🚪 Logout</button>
        </div>
    </div>

    <!-- Main Container -->
    <div class="container">
        
        <!-- AUTH PAGE - Login/Signup -->
        <div id="authPage">
            <div class="card">
                <h2>🔥 <span class="glow-text">DVARY BOOST</span></h2>
                <p class="subtitle" id="authSubtitle">Ingia kwenye akaunti yako</p>
                
                <div class="error-msg" id="authError"></div>
                <div class="success-msg" id="authSuccess"></div>
                <div class="loading-spinner" id="authLoading">
                    <div class="spinner"></div>
                </div>

                <!-- Login Form -->
                <form id="loginForm" onsubmit="login(event)">
                    <div class="form-group">
                        <label>📧 Email</label>
                        <input type="email" id="loginEmail" placeholder="Enter your email" required>
                    </div>
                    <div class="form-group">
                        <label>🔒 Password</label>
                        <input type="password" id="loginPassword" placeholder="Enter your password" required>
                    </div>
                    <button type="submit" class="btn-primary" id="loginBtn">🔑 LOGIN</button>
                </form>

                <!-- Signup Form -->
                <form id="signupForm" style="display: none;" onsubmit="signup(event)">
                    <div class="form-group">
                        <label>👤 Full Name</label>
                        <input type="text" id="signupName" placeholder="Enter your full name" required>
                    </div>
                    <div class="form-group">
                        <label>📧 Email</label>
                        <input type="email" id="signupEmail" placeholder="Enter your email" required>
                    </div>
                    <div class="form-group">
                        <label>🔒 Password</label>
                        <input type="password" id="signupPassword" placeholder="Create a password (min 6 chars)" required minlength="6">
                    </div>
                    <div class="form-group">
                        <label>🔒 Confirm Password</label>
                        <input type="password" id="signupConfirm" placeholder="Confirm your password" required>
                    </div>
                    <button type="submit" class="btn-primary" id="signupBtn">📝 SIGN UP</button>
                </form>

                <div class="auth-toggle">
                    <span id="authToggleText">Don't have an account?</span>
                    <a id="authToggleLink" onclick="toggleAuth()">Sign Up</a>
                </div>
            </div>
        </div>

        <!-- MAIN APP - Only visible after login -->
        <div id="appContent" class="app-content">
            
            <!-- Join Form -->
            <div class="card" id="join">
                <h2>🔥 <span class="glow-text">DVARY BOOST</span></h2>
                <p class="subtitle">Jiunge sasa na upate <strong style="color: #ff6b6b;">Views & Followers</strong></p>
                
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
                    <button type="submit" class="btn-primary" id="joinBtn">
                        🚀 JIUNGE SASA
                    </button>
                </form>
            </div>

            <!-- Download Section -->
            <div class="card" id="downloadSection" style="display: none;">
                <div class="download-section">
                    <span class="icon">⬇️</span>
                    <h3>PAKUA <span style="color: #ff6b6b;">VIEWS</span> ZAKO</h3>
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
                <h2>📈 <span class="glow-text">BOOST FOLLOWERS</span></h2>
                <p class="subtitle">Pata mafanikio makubwa kwenye mitandao yako</p>
                
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="number">1000+</div>
                        <div class="label">Views kwa siku</div>
                    </div>
                    <div class="stat-item">
                        <div class="number">500+</div>
                        <div class="label">Followers kila wiki</div>
                    </div>
                    <div class="stat-item">
                        <div class="number">24/7</div>
                        <div class="label">Support</div>
                    </div>
                </div>
                
                <div style="text-align: center;">
                    <p style="color: rgba(255,255,255,0.7); margin: 15px 0;">
                        ✅ Ongeza wateja wako kwa kujiunga na timu yetu
                    </p>
                    <a href="https://whatsapp.com/channel/0029VbCRC9b5fM5cruU8PF2M" target="_blank" class="channel-btn">
                        📢 Jiunge na Channel Yetu
                    </a>
                </div>
            </div>

            <!-- About Section -->
            <div class="card" id="about">
                <h2>ℹ️ <span class="glow-text">ABOUT</span></h2>
                <p class="subtitle">Kuhusu Dvary Boost Views</p>
                <div style="color: rgba(255,255,255,0.8); line-height: 1.8;">
                    <p><strong>Dvary Boost Views</strong> ni jukwaa la kusaidia watu kuongeza mtazamo wa WhatsApp status, kujenga biashara na kuongeza mauzo kupitia mitandao ya kijamii.</p>
                    <br>
                    <p><strong>Misioni yetu:</strong></p>
                    <p style="color: rgba(255,255,255,0.6);">Kusaidia watu wafikie malengo yao ya kibiashara kupitia mitandao ya kijamii kwa kuwapatia views na followers wa kweli.</p>
                </div>
            </div>

            <!-- Contact Section -->
            <div class="card" id="contact">
                <h2>📞 <span class="glow-text">CONTACT</span></h2>
                <p class="subtitle">Wasiliana nasi kwa mawasiliano yoyote</p>
                
                <div class="contact-card">
                    <div class="contact-icon">📱</div>
                    <div class="contact-info">
                        <div class="label">WhatsApp</div>
                        <div class="value">
                            <a href="https://wa.me/255724525910" target="_blank">+255 724 525 910</a>
                        </div>
                    </div>
                </div>
                
                <div class="contact-card">
                    <div class="contact-icon">📧</div>
                    <div class="contact-info">
                        <div class="label">Email</div>
                        <div class="value">
                            <a href="mailto:dullamanyama0@gmail.com">dullamanyama0@gmail.com</a>
                        </div>
                    </div>
                </div>
                
                <div class="contact-card">
                    <div class="contact-icon">🌐</div>
                    <div class="contact-info">
                        <div class="label">Channel</div>
                        <div class="value">
                            <a href="https://whatsapp.com/channel/0029VbCRC9b5fM5cruU8PF2M" target="_blank">WhatsApp Channel</a>
                        </div>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 15px; color: rgba(255,255,255,0.4); font-size: 0.8rem;">
                    <p>Developed by <strong style="color: #ff6b6b;">Dulla Manyama</strong></p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Firebase Config from your google-services.json
        const firebaseConfig = {
            apiKey: "AIzaSyDpFyANpjv2dMUvXoMSSmqoT3s1UwJLUkg",
            authDomain: "dvary-9a7d0.firebaseapp.com",
            projectId: "dvary-9a7d0",
            storageBucket: "dvary-9a7d0.firebasestorage.app",
            appId: "1:107370806066:android:e954fb03d99e52ac09f52b"
        };

        // Initialize Firebase
        firebase.initializeApp(firebaseConfig);
        const auth = firebase.auth();

        let isLogin = true;

        // Generate Rain
        function createRain() {
            const rainContainer = document.getElementById('rain');
            const drops = 150;
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

        // Toggle Auth (Login/Signup)
        function toggleAuth() {
            isLogin = !isLogin;
            const loginForm = document.getElementById('loginForm');
            const signupForm = document.getElementById('signupForm');
            const subtitle = document.getElementById('authSubtitle');
            const toggleText = document.getElementById('authToggleText');
            const toggleLink = document.getElementById('authToggleLink');

            if (isLogin) {
                loginForm.style.display = 'block';
                signupForm.style.display = 'none';
                subtitle.textContent = 'Ingia kwenye akaunti yako';
                toggleText.textContent = "Don't have an account?";
                toggleLink.textContent = 'Sign Up';
            } else {
                loginForm.style.display = 'none';
                signupForm.style.display = 'block';
                subtitle.textContent = 'Unda akaunti mpya';
                toggleText.textContent = "Already have an account?";
                toggleLink.textContent = 'Login';
            }
            
            // Clear any messages
            showError('', 'authError');
            showSuccess('', 'authSuccess');
        }

        // Show/Hide Loading
        function showLoading(show) {
            const spinner = document.getElementById('authLoading');
            if (show) {
                spinner.classList.add('show');
            } else {
                spinner.classList.remove('show');
            }
        }

        // Show/Hide messages
        function showError(msg, id) {
            const el = document.getElementById(id);
            if (msg) {
                el.textContent = msg;
                el.classList.add('show');
                el.style.display = 'block';
            } else {
                el.classList.remove('show');
                el.style.display = 'none';
            }
        }

        function showSuccess(msg, id) {
            const el = document.getElementById(id);
            if (msg) {
                el.textContent = msg;
                el.classList.add('show');
                el.style.display = 'block';
            } else {
                el.classList.remove('show');
                el.style.display = 'none';
            }
        }

        // Login
        function login(e) {
            e.preventDefault();
            
            const email = document.getElementById('loginEmail').value.trim();
            const password = document.getElementById('loginPassword').value;

            if (!email || !password) {
                showError('❌ Tafadhali jaza sehemu zote!', 'authError');
                return;
            }

            showError('', 'authError');
            showSuccess('', 'authSuccess');
            showLoading(true);
            document.getElementById('loginBtn').disabled = true;
            document.getElementById('loginBtn').textContent = '⏳ LOADING...';

            auth.signInWithEmailAndPassword(email, password)
                .then((userCredential) => {
                    const user = userCredential.user;
                    showLoading(false);
                    document.getElementById('loginBtn').disabled = false;
                    document.getElementById('loginBtn').textContent = '🔑 LOGIN';
                    showSuccess('✅ Login successful!', 'authSuccess');
                    
                    setTimeout(() => {
                        document.getElementById('authPage').style.display = 'none';
                        document.getElementById('appContent').classList.add('show');
                        document.getElementById('userInfo').style.display = 'flex';
                        document.getElementById('userEmail').textContent = user.email;
                        
                        // Check if already joined
                        const joined = localStorage.getItem('dvary_joined_' + user.uid);
                        if (joined === 'true') {
                            document.getElementById('downloadSection').style.display = 'block';
                            document.getElementById('joinFormSubmit').style.display = 'none';
                            document.getElementById('successMsg').classList.add('show');
                            document.getElementById('successMsg').textContent = '✅ Umeshajiunga! Pakua views zako hapa chini.';
                        }
                    }, 1000);
                })
                .catch((error) => {
                    showLoading(false);
                    document.getElementById('loginBtn').disabled = false;
                    document.getElementById('loginBtn').textContent = '🔑 LOGIN';
                    
                    let msg = error.message;
                    if (error.code === 'auth/user-not-found') {
                        msg = '❌ Email haijapatikana. Tafadhali jiandikisha.';
                    } else if (error.code === 'auth/wrong-password') {
                        msg = '❌ Password si sahihi. Jaribu tena.';
                    } else if (error.code === 'auth/invalid-email') {
                        msg = '❌ Email si sahihi.';
                    } else if (error.code === 'auth/too-many-requests') {
                        msg = '❌ Imeshindwa mara nyingi. Jaribu baadaye.';
                    }
                    showError(msg, 'authError');
                });
        }

        // Signup
        function signup(e) {
            e.preventDefault();
            
            const name = document.getElementById('signupName').value.trim();
            const email = document.getElementById('signupEmail').value.trim();
            const password = document.getElementById('signupPassword').value;
            const confirm = document.getElementById('signupConfirm').value;

            showError('', 'authError');
            showSuccess('', 'authSuccess');

            if (!name || !email || !password || !confirm) {
                showError('❌ Tafadhali jaza sehemu zote!', 'authError');
                return;
            }

            if (password !== confirm) {
                showError('❌ Passwords hazifanani!', 'authError');
                return;
            }

            if (password.length < 6) {
                showError('❌ Password lazima iwe angalau herufi 6!', 'authError');
                return;
            }

            showLoading(true);
            document.getElementById('signupBtn').disabled = true;
            document.getElementById('signupBtn').textContent = '⏳ LOADING...';

            auth.createUserWithEmailAndPassword(email, password)
                .then((userCredential) => {
                    const user = userCredential.user;
                    // Update profile with name
                    return user.updateProfile({
                        displayName: name
                    }).then(() => {
                        showLoading(false);
                        document.getElementById('signupBtn').disabled = false;
                        document.getElementById('signupBtn').textContent = '📝 SIGN UP';
                        showSuccess('✅ Account created successfully!', 'authSuccess');
                        
                        setTimeout(() => {
                            document.getElementById('authPage').style.display = 'none';
                            document.getElementById('appContent').classList.add('show');
                            document.getElementById('userInfo').style.display = 'flex';
                            document.getElementById('userEmail').textContent = email;
                        }, 1000);
                    });
                })
                .catch((error) => {
                    showLoading(false);
                    document.getElementById('signupBtn').disabled = false;
                    document.getElementById('signupBtn').textContent = '📝 SIGN UP';
                    
                    let msg = error.message;
                    if (error.code === 'auth/email-already-in-use') {
                        msg = '❌ Email hii tayari imesajiliwa!';
                    } else if (error.code === 'auth/invalid-email') {
                        msg = '❌ Email si sahihi.';
                    } else if (error.code === 'auth/weak-password') {
                        msg = '❌ Password ni dhaifu. Tafadhali tumia herufi 6 au zaidi.';
                    } else if (error.code === 'auth/network-request-failed') {
                        msg = '❌ Mtandao haufanyi kazi. Tafadhali hakikisha umeconnect.';
                    }
                    showError(msg, 'authError');
                });
        }

        // Logout
        function logout() {
            auth.signOut().then(() => {
                document.getElementById('authPage').style.display = 'block';
                document.getElementById('appContent').classList.remove('show');
                document.getElementById('userInfo').style.display = 'none';
                // Reset forms
                document.getElementById('loginForm').reset();
                document.getElementById('signupForm').reset();
                // Reset to login
                if (!isLogin) toggleAuth();
                showSuccess('', 'authSuccess');
                showError('', 'authError');
                // Reset join form
                document.getElementById('joinFormSubmit').style.display = 'block';
                document.getElementById('downloadSection').style.display = 'none';
                document.getElementById('successMsg').classList.remove('show');
                document.getElementById('name').disabled = false;
                document.getElementById('phone').disabled = false;
            }).catch((error) => {
                showError('❌ Logout failed: ' + error.message, 'authError');
            });
        }

        // Check auth state on load
        auth.onAuthStateChanged((user) => {
            if (user) {
                document.getElementById('authPage').style.display = 'none';
                document.getElementById('appContent').classList.add('show');
                document.getElementById('userInfo').style.display = 'flex';
                document.getElementById('userEmail').textContent = user.email || user.displayName || 'User';
                
                // Check if already joined
                const joined = localStorage.getItem('dvary_joined_' + user.uid);
                if (joined === 'true') {
                    document.getElementById('downloadSection').style.display = 'block';
                    document.getElementById('joinFormSubmit').style.display = 'none';
                    document.getElementById('successMsg').classList.add('show');
                    document.getElementById('successMsg').textContent = '✅ Umeshajiunga! Pakua views zako hapa chini.';
                }
            } else {
                document.getElementById('authPage').style.display = 'block';
                document.getElementById('appContent').classList.remove('show');
                document.getElementById('userInfo').style.display = 'none';
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

            const user = auth.currentUser;
            if (!user) {
                alert('⚠️ Tafadhali ingia kwanza!');
                return;
            }

            const joinBtn = document.getElementById('joinBtn');
            joinBtn.disabled = true;
            joinBtn.textContent = '⏳ LOADING...';

            fetch('/jiunge', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `name=${encodeURIComponent(name)}&phone=${encodeURIComponent(phone)}&email=${encodeURIComponent(user.email)}`
            })
            .then(response => response.json())
            .then(data => {
                joinBtn.disabled = false;
                joinBtn.textContent = '🚀 JIUNGE SASA';
                
                if (data.success) {
                    document.getElementById('successMsg').classList.add('show');
                    document.getElementById('joinFormSubmit').style.display = 'none';
                    document.getElementById('downloadSection').style.display = 'block';
                    
                    setTimeout(() => {
                        document.getElementById('downloadSection').scrollIntoView({ behavior: 'smooth' });
                    }, 500);
                    
                    document.getElementById('name').disabled = true;
                    document.getElementById('phone').disabled = true;
                    
                    // Save to localStorage with user UID
                    localStorage.setItem('dvary_joined_' + user.uid, 'true');
                } else {
                    alert('❌ ' + data.message);
                }
            })
            .catch(error => {
                joinBtn.disabled = false;
                joinBtn.textContent = '🚀 JIUNGE SASA';
                alert('❌ Kuna hitilafu, tafadhali jaribu tena!');
                console.error('Error:', error);
            });
        }

        // Download Views
        function downloadViews() {
            window.location.href = '/download';
            
            const btn = document.querySelector('.btn-success');
            const originalText = btn.textContent;
            btn.textContent = '✅ IMEPAKUA!';
            setTimeout(() => {
                btn.textContent = originalText;
            }, 3000);
        }
    </script>

    <!-- Firebase SDK -->
    <script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-auth-compat.js"></script>
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
    email = request.form.get('email', 'unknown')
    
    try:
        # Save to Firestore
        db.collection('users').document(email).set({
            'name': name,
            'phone': phone,
            'email': email,
            'joined_at': datetime.now().isoformat()
        }, merge=True)
        
        # Also save to members collection
        db.collection('teams').document('N4HZPY').collection('members').document(phone).set({
            'name': name,
            'phone': phone,
            'email': email,
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
