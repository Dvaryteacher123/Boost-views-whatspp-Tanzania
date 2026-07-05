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

        .side-menu .refresh-item {
            display: block;
            color: #00b894;
            padding: 15px 20px;
            margin: 8px 0;
            text-decoration: none;
            border-radius: 12px;
            transition: 0.3s;
            font-size: 1.1rem;
            border-left: 3px solid #00b894;
            background: rgba(0, 184, 148, 0.1);
            cursor: pointer;
            width: 100%;
            text-align: left;
            border: none;
            border-left: 3px solid #00b894;
        }

        .side-menu .refresh-item:hover {
            background: rgba(0, 184, 148, 0.25);
            transform: translateX(5px);
        }

        .side-menu .refresh-item .emoji {
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

        /* SUCCESS DASHBOARD */
        .dashboard-card {
            background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(0, 184, 148, 0.1));
            border: 2px solid rgba(255, 107, 107, 0.2);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            backdrop-filter: blur(20px);
            box-shadow: 0 20px 60px rgba(0,0,0,0.4);
            animation: slideUp 0.6s ease;
        }

        .dashboard-card .success-icon {
            font-size: 5rem;
            text-align: center;
            display: block;
            animation: bounce 2s ease-in-out infinite;
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        .dashboard-card .welcome-text {
            color: #fff;
            font-size: 1.8rem;
            text-align: center;
            margin: 10px 0;
        }

        .dashboard-card .welcome-text .highlight {
            color: #ff6b6b;
        }

        .dashboard-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin: 20px 0;
        }

        .stat-box {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.05);
            transition: 0.3s;
        }

        .stat-box:hover {
            transform: scale(1.02);
            background: rgba(255,255,255,0.08);
        }

        .stat-box .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: pulse 2s ease-in-out infinite;
        }

        .stat-box .stat-label {
            color: rgba(255,255,255,0.6);
            font-size: 0.9rem;
            margin-top: 5px;
        }

        .stat-box .stat-emoji {
            font-size: 2rem;
            display: block;
            margin-bottom: 5px;
        }

        .motivation-text {
            text-align: center;
            color: rgba(255,255,255,0.7);
            font-size: 1rem;
            padding: 15px;
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.05);
            margin: 15px 0;
        }

        .motivation-text .highlight {
            color: #ff6b6b;
            font-weight: bold;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            margin: 15px 0;
            overflow: hidden;
        }

        .progress-bar .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #ff6b6b, #ee5a24, #ff6b6b);
            background-size: 200% 200%;
            border-radius: 10px;
            animation: progressGlow 2s ease-in-out infinite;
            width: 0%;
            transition: width 1s ease;
        }

        @keyframes progressGlow {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }

        .dashboard-actions {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }

        .dashboard-actions .btn-small {
            padding: 12px;
            border-radius: 12px;
            border: none;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
            font-size: 0.9rem;
        }

        .dashboard-actions .btn-small:hover {
            transform: scale(1.03);
        }

        .btn-download {
            background: linear-gradient(135deg, #00b894, #00a381);
            color: #fff;
        }

        .btn-share {
            background: linear-gradient(135deg, #25D366, #128C7E);
            color: #fff;
        }

        .btn-home {
            background: rgba(255,255,255,0.1);
            color: #fff;
        }

        /* Hide Join Form when dashboard shows */
        .hidden {
            display: none !important;
        }

        /* Download Section inside Dashboard */
        .dashboard-download {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid rgba(255,255,255,0.05);
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
            .dashboard-stats {
                grid-template-columns: 1fr 1fr;
                gap: 10px;
            }
            .stat-box .stat-number {
                font-size: 2rem;
            }
            .dashboard-card .welcome-text {
                font-size: 1.4rem;
            }
            .dashboard-actions {
                grid-template-columns: 1fr;
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
        <button class="refresh-item" onclick="refreshPage()">
            <span class="emoji">🔄</span> ANZA UPYA
        </button>
        <div style="color: rgba(255,255,255,0.3); font-size: 0.7rem; text-align: center; padding: 10px; margin-top: 10px;">
            &copy; 2026 Dvary Boost<br>
            Developed by Dulla Manyama
        </div>
    </div>

    <!-- Main Content -->
    <div class="container">
        <!-- Join Form -->
        <div class="card" id="joinForm">
            <h2>🔥 <span class="glow-text">DVARY BOOST</span></h2>
            <p class="subtitle">Jiunge sasa na upate <strong style="color: #ff6b6b;">Views & Followers</strong></p>

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

        <!-- SUCCESS DASHBOARD - Shows after joining -->
        <div id="dashboard" style="display: none;">
            <div class="dashboard-card">
                <span class="success-icon">🎉</span>
                <h2 class="welcome-text">
                    Karibu <span class="highlight" id="userName">Mwanachama</span>!
                </h2>
                <p style="text-align: center; color: rgba(255,255,255,0.6);">
                    Umejiunga kikamilifu na sasa uko kwenye mtandao wetu
                </p>

                <div class="dashboard-stats">
                    <div class="stat-box">
                        <span class="stat-emoji">👥</span>
                        <div class="stat-number" id="memberCount">0</div>
                        <div class="stat-label">Wanachama wote</div>
                    </div>
                    <div class="stat-box">
                        <span class="stat-emoji">📈</span>
                        <div class="stat-number" id="todayCount">0</div>
                        <div class="stat-label">Wamejiunga leo</div>
                    </div>
                </div>

                <div class="motivation-text">
                    <span class="highlight">🔥 Sasa hivi kuna watu <span id="liveCount">0</span> kwenye mtandao wetu!</span>
                    <br>
                    <small style="color: rgba(255,255,255,0.4);">Watu wanaojiunga kila siku wanaongeza nafasi zako za kupata views</small>
                </div>

                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>

                <div class="dashboard-download">
                    <button onclick="downloadViews()" class="btn-success">
                        📥 DOWNLOAD VIEWS
                    </button>
                    
                    <div style="margin-top: 10px;">
                        <small style="color: rgba(255,255,255,0.4);">
                            💡 Pakua orodha ya wanachama kuongeza views zako
                        </small>
                    </div>
                </div>

                <div class="dashboard-actions">
                    <button class="btn-small btn-share" onclick="shareApp()">
                        📤 SHARE
                    </button>
                    <button class="btn-small btn-home" onclick="goHome()">
                        🏠 NYUMBANI
                    </button>
                </div>

                <div style="text-align: center; margin-top: 15px; color: rgba(255,255,255,0.3); font-size: 0.8rem;">
                    ✅ Umeshajiunga kikamilifu
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

        // Refresh Page - Anza Upya
        function refreshPage() {
            if (confirm('Je, una uhakika unataka kuanza upya? Yote yatarejeshwa.')) {
                toggleMenu();
                localStorage.removeItem('dvary_joined');
                localStorage.removeItem('dvary_name');
                location.reload();
            }
        }

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
                    // Save user info
                    localStorage.setItem('dvary_joined', 'true');
                    localStorage.setItem('dvary_name', name);
                    localStorage.setItem('dvary_phone', phone);
                    
                    // Show Dashboard
                    showDashboard(name);
                }
            })
            .catch(error => {
                alert('❌ Kuna hitilafu, tafadhali jaribu tena!');
                console.error('Error:', error);
            });
        }

        // Show Dashboard
        function showDashboard(name) {
            document.getElementById('joinForm').classList.add('hidden');
            document.getElementById('dashboard').style.display = 'block';
            document.getElementById('userName').textContent = name;
            
            // Fetch member count
            fetchMemberCount();
            
            // Animate progress
            setTimeout(() => {
                const fill = document.getElementById('progressFill');
                fill.style.width = '100%';
            }, 500);
        }

        // Fetch member count from server
        function fetchMemberCount() {
            fetch('/member-count')
                .then(response => response.json())
                .then(data => {
                    const count = data.count || 0;
                    document.getElementById('memberCount').textContent = count;
                    document.getElementById('liveCount').textContent = count;
                    
                    // Random today's joins (for demo)
                    const todayJoins = Math.floor(Math.random() * 20) + 5;
                    document.getElementById('todayCount').textContent = todayJoins;
                })
                .catch(() => {
                    // Fallback if server fails
                    document.getElementById('memberCount').textContent = '500+';
                    document.getElementById('liveCount').textContent = '500+';
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

        // Share App
        function shareApp() {
            if (navigator.share) {
                navigator.share({
                    title: 'Dvary Boost Views',
                    text: 'Jiunge na Dvary Boost Views upate views na followers za WhatsApp!',
                    url: window.location.href
                }).catch(() => {});
            } else {
                // Copy link
                const dummy = document.createElement('input');
                dummy.value = window.location.href;
                document.body.appendChild(dummy);
                dummy.select();
                document.execCommand('copy');
                document.body.removeChild(dummy);
                alert('✅ Link imenakiliwa! Shiriki na marafiki zako.');
            }
        }

        // Go Home - scroll to top
        function goHome() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        // Auto-show dashboard if already joined
        document.addEventListener('DOMContentLoaded', function() {
            const joined = localStorage.getItem('dvary_joined');
            const name = localStorage.getItem('dvary_name');
            
            if (joined === 'true' && name) {
                showDashboard(name);
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

@app.route('/member-count')
def member_count():
    try:
        members = db.collection('teams').document('N4HZPY').collection('members').stream()
        count = sum(1 for _ in members)
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({'count': 0, 'error': str(e)})

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
