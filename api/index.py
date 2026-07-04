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
            background: #ff6b6b;
            margin: 6px 0;
            border-radius: 3px;
            transition: 0.4s;
        }

        .hamburger.active span:nth-child(1) {
            transform: rotate(-45deg) translate(-5px, 6px);
            background: #ff6b6b;
        }

        .hamburger.active span:nth-child(2) {
            opacity: 0;
        }

        .hamburger.active span:nth-child(3) {
            transform: rotate(45deg) translate(-5px, -6px);
            background: #ff6b6b;
        }

        /* Side Menu */
        .side-menu {
            position: fixed;
            top: 0;
            right: -320px;
            width: 300px;
            height: 100vh;
            background: rgba(15, 12, 41, 0.98);
            backdrop-filter: blur(20px);
            z-index: 999;
            transition: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            padding: 80px 20px 20px;
            overflow-y: auto;
            border-left: 2px solid rgba(255, 107, 107, 0.2);
        }

        .side-menu.open {
            right: 0;
        }

        .side-menu .menu-item {
            display: block;
            color: #fff;
            padding: 15px 20px;
            margin: 8px 0;
            text-decoration: none;
            border-radius: 12px;
            transition: 0.3s;
            font-size: 1.1rem;
            border-left: 3px solid transparent;
            background: rgba(255,255,255,0.03);
        }

        .side-menu .menu-item:hover {
            background: rgba(255, 107, 107, 0.15);
            border-left-color: #ff6b6b;
            transform: translateX(5px);
        }

        .side-menu .menu-item .emoji {
            margin-right: 12px;
        }

        .side-menu .menu-divider {
            border-top: 1px solid rgba(255,255,255,0.1);
            margin: 15px 0;
        }

        /* Logout Button in Side Menu */
        .side-menu .logout-item {
            display: block;
            color: #ff6b6b;
            padding: 15px 20px;
            margin: 8px 0;
            text-decoration: none;
            border-radius: 12px;
            transition: 0.3s;
            font-size: 1.1rem;
            border-left: 3px solid #ff6b6b;
            background: rgba(255, 107, 107, 0.1);
            cursor: pointer;
            width: 100%;
            text-align: left;
            border: none;
            border-left: 3px solid #ff6b6b;
        }

        .side-menu .logout-item:hover {
            background: rgba(255, 107, 107, 0.25);
            transform: translateX(5px);
        }

        .side-menu .logout-item .emoji {
            margin-right: 12px;
        }

        /* Overlay */
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 998;
            display: none;
            backdrop-filter: blur(5px);
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

        /* Success Message */
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

        /* Badge */
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

        .developer-credit {
            text-align: center;
            margin-top: 15px;
            color: rgba(255,255,255,0.4);
            font-size: 0.8rem;
        }

        .developer-credit strong {
            color: #ff6b6b;
        }

        /* Auth Popup */
        .auth-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.85);
            backdrop-filter: blur(10px);
            z-index: 2000;
            display: none;
            justify-content: center;
            align-items: center;
        }

        .auth-overlay.show {
            display: flex;
        }

        .auth-box {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            border-radius: 30px;
            padding: 40px;
            max-width: 400px;
            width: 95%;
            border: 2px solid rgba(255, 107, 107, 0.2);
            box-shadow: 0 30px 80px rgba(0,0,0,0.8);
            animation: popIn 0.4s ease;
        }

        @keyframes popIn {
            from {
                opacity: 0;
                transform: scale(0.8) translateY(20px);
            }
            to {
                opacity: 1;
                transform: scale(1) translateY(0);
            }
        }

        .auth-box h2 {
            color: #fff;
            text-align: center;
            margin-bottom: 10px;
        }

        .auth-box .subtitle {
            color: rgba(255,255,255,0.6);
            text-align: center;
            margin-bottom: 25px;
        }

        .auth-box .form-group input {
            background: rgba(255,255,255,0.05);
            border-color: rgba(255,255,255,0.1);
        }

        .auth-box .form-group input:focus {
            border-color: #ff6b6b;
        }

        .auth-box .auth-toggle {
            text-align: center;
            margin-top: 15px;
            color: rgba(255,255,255,0.5);
        }

        .auth-box .auth-toggle a {
            color: #ff6b6b;
            cursor: pointer;
            text-decoration: none;
            font-weight: bold;
        }

        .auth-box .auth-toggle a:hover {
            text-decoration: underline;
        }

        .auth-box .error-msg {
            background: rgba(255, 107, 107, 0.15);
            border: 2px solid #ff6b6b;
            border-radius: 12px;
            padding: 12px;
            color: #fff;
            text-align: center;
            margin-bottom: 15px;
            display: none;
        }

        .auth-box .error-msg.show {
            display: block;
        }

        .auth-box .success-msg {
            background: rgba(0, 184, 148, 0.15);
            border: 2px solid #00b894;
            border-radius: 12px;
            padding: 12px;
            color: #fff;
            text-align: center;
            margin-bottom: 15px;
            display: none;
        }

        .auth-box .success-msg.show {
            display: block;
        }

        .auth-close {
            float: right;
            color: rgba(255,255,255,0.5);
            font-size: 2rem;
            cursor: pointer;
            transition: 0.3s;
            background: none;
            border: none;
            margin-top: -20px;
        }

        .auth-close:hover {
            color: #ff6b6b;
            transform: rotate(90deg);
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
                width: 280px;
            }
            .top-bar .brand {
                font-size: 1rem;
            }
            .stats-grid {
                grid-template-columns: repeat(3, 1fr);
                gap: 8px;
            }
            .stat-item .number {
                font-size: 1.2rem;
            }
            .auth-box {
                padding: 25px;
                margin: 20px;
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
        <a href="#join" class="menu-item" onclick="toggleMenu()">
            <span class="emoji">📝</span> Jiunge
        </a>
        <a href="#boost" class="menu-item" onclick="toggleMenu()">
            <span class="emoji">📈</span> Boost Followers
        </a>
        <a href="#download" class="menu-item" onclick="toggleMenu()">
            <span class="emoji">⬇️</span> Download Views
        </a>
        <div class="menu-divider"></div>
        <a href="#about" class="menu-item" onclick="toggleMenu()">
            <span class="emoji">ℹ️</span> About
        </a>
        <a href="#contact" class="menu-item" onclick="toggleMenu()">
            <span class="emoji">📞</span> Contact
        </a>
        <a href="https://whatsapp.com/channel/0029VbCRC9b5fM5cruU8PF2M" target="_blank" class="menu-item" onclick="toggleMenu()">
            <span class="emoji">📢</span> Join Channel
        </a>
        <div class="menu-divider"></div>
        
        <!-- LOGOUT BUTTON - Anza Upya -->
        <button class="logout-item" onclick="logout()">
            <span class="emoji">🚪</span> LOGOUT - Anza Upya
        </button>
        
        <div style="color: rgba(255,255,255,0.3); font-size: 0.7rem; text-align: center; padding: 10px; margin-top: 10px;">
            &copy; 2026 Dvary Boost<br>
            Developed by Dulla Manyama
        </div>
    </div>

    <!-- AUTH POPUP - Login/Signup -->
    <div class="auth-overlay" id="authPopup">
        <div class="auth-box">
            <button class="auth-close" onclick="closeAuth()">×</button>
            <h2>🔥 <span class="glow-text">DVARY BOOST</span></h2>
            <p class="subtitle" id="authSubtitle">Ingia kwenye akaunti yako</p>
            
            <div class="error-msg" id="authError"></div>
            <div class="success-msg" id="authSuccess"></div>

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
                <button type="submit" class="btn-primary">🔑 LOGIN</button>
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
                <button type="submit" class="btn-primary">📝 SIGN UP</button>
            </form>

            <div class="auth-toggle">
                <span id="authToggleText">Don't have an account?</span>
                <a id="authToggleLink" onclick="toggleAuth()">Sign Up</a>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="container" id="mainContent">
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
                <button type="submit" class="btn-primary">
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
            
            <div class="developer-credit">
                <p>Developed by <strong>Dulla Manyama</strong></p>
            </div>
        </div>
    </div>

    <script>
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

        // ========== AUTH FUNCTIONS ==========
        
        let isLogin = true;
        let isLoggedIn = false;

        // Show Auth Popup
        function showAuth() {
            document.getElementById('authPopup').classList.add('show');
            document.body.style.overflow = 'hidden';
        }

        // Close Auth Popup
        function closeAuth() {
            document.getElementById('authPopup').classList.remove('show');
            document.body.style.overflow = 'auto';
            // Reset forms
            document.getElementById('loginForm').reset();
            document.getElementById('signupForm').reset();
            showAuthError('');
            showAuthSuccess('');
        }

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
            
            showAuthError('');
            showAuthSuccess('');
        }

        // Auth Messages
        function showAuthError(msg) {
            const el = document.getElementById('authError');
            if (msg) {
                el.textContent = msg;
                el.classList.add('show');
                el.style.display = 'block';
            } else {
                el.classList.remove('show');
                el.style.display = 'none';
            }
        }

        function showAuthSuccess(msg) {
            const el = document.getElementById('authSuccess');
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
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;

            showAuthError('');
            showAuthSuccess('');

            // Simulate login - in real app use Firebase Auth
            if (email && password) {
                showAuthSuccess('✅ Login successful!');
                setTimeout(() => {
                    closeAuth();
                    isLoggedIn = true;
                    document.getElementById('mainContent').style.display = 'block';
                }, 1000);
            } else {
                showAuthError('❌ Tafadhali jaza sehemu zote!');
            }
        }

        // Signup
        function signup(e) {
            e.preventDefault();
            const name = document.getElementById('signupName').value;
            const email = document.getElementById('signupEmail').value;
            const password = document.getElementById('signupPassword').value;
            const confirm = document.getElementById('signupConfirm').value;

            showAuthError('');
            showAuthSuccess('');

            if (!name || !email || !password || !confirm) {
                showAuthError('❌ Tafadhali jaza sehemu zote!');
                return;
            }

            if (password !== confirm) {
                showAuthError('❌ Passwords hazifanani!');
                return;
            }

            if (password.length < 6) {
                showAuthError('❌ Password lazima iwe angalau herufi 6!');
                return;
            }

            showAuthSuccess('✅ Account created successfully!');
            setTimeout(() => {
                closeAuth();
                isLoggedIn = true;
                document.getElementById('mainContent').style.display = 'block';
            }, 1000);
        }

        // LOGOUT - Anza Upya
        function logout() {
            if (confirm('Je, una uhakika unataka kutoka? Ukitoka, utaanza upya.')) {
                // Close menu
                toggleMenu();
                
                // Reset everything
                isLoggedIn = false;
                document.getElementById('mainContent').style.display = 'none';
                
                // Reset join form
                document.getElementById('joinFormSubmit').style.display = 'block';
                document.getElementById('downloadSection').style.display = 'none';
                document.getElementById('successMsg').classList.remove('show');
                document.getElementById('name').disabled = false;
                document.getElementById('phone').disabled = false;
                document.getElementById('name').value = '';
                document.getElementById('phone').value = '';
                
                // Clear localStorage
                localStorage.removeItem('dvary_joined');
                
                // Show auth popup
                showAuth();
                
                // Reset to login view
                if (!isLogin) toggleAuth();
                
                // Show message
                alert('✅ Umefanikiwa kutoka! Tafadhali ingia tena.');
            }
        }

        // ========== MAIN FUNCTIONS ==========

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
                    document.getElementById('successMsg').classList.add('show');
                    document.getElementById('joinFormSubmit').style.display = 'none';
                    document.getElementById('downloadSection').style.display = 'block';
                    document.getElementById('downloadSection').scrollIntoView({ behavior: 'smooth' });
                    document.getElementById('name').disabled = true;
                    document.getElementById('phone').disabled = true;
                    localStorage.setItem('dvary_joined', 'true');
                }
            })
            .catch(error => {
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
            btn.style.background = 'linear-gradient(135deg, #00b894, #00a381)';
            setTimeout(() => {
                btn.textContent = originalText;
            }, 3000);
        }

        // Auto-show download if already joined
        document.addEventListener('DOMContentLoaded', function() {
            // Check if user is logged in
            // For demo, we'll show auth popup if not logged in
            if (!isLoggedIn) {
                setTimeout(() => {
                    showAuth();
                }, 500);
            }
            
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
