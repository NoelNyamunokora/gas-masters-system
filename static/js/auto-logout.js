/**
 * Auto-Logout Reminder System
 * Shows a popup reminder before session expires
 */

(function() {
    // Configuration
    const SESSION_TIMEOUT = 3600000; // 1 hour in milliseconds (matches PERMANENT_SESSION_LIFETIME)
    const WARNING_TIME = 300000; // Show warning 5 minutes before timeout
    const POPUP_DISPLAY_TIME = SESSION_TIMEOUT - WARNING_TIME;
    
    let warningTimeout;
    let logoutTimeout;
    let lastActivity = Date.now();
    
    // Create popup HTML
    function createLogoutPopup() {
        const popup = document.createElement('div');
        popup.id = 'logout-warning-popup';
        popup.innerHTML = `
            <div class="logout-popup-overlay"></div>
            <div class="logout-popup-content">
                <div class="logout-popup-icon">
                    <i class="fas fa-clock"></i>
                </div>
                <h3>Session Expiring Soon</h3>
                <p>Your session will expire in <strong><span id="countdown">5:00</span></strong> due to inactivity.</p>
                <p class="logout-hint">Don't forget: <strong>Logout</strong> is in the top-right corner!</p>
                <div class="logout-popup-buttons">
                    <button id="stay-logged-in" class="btn-stay">Stay Logged In</button>
                    <button id="logout-now" class="btn-logout">Logout Now</button>
                </div>
            </div>
        `;
        document.body.appendChild(popup);
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            #logout-warning-popup {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 10000;
                display: none;
                animation: fadeIn 0.3s ease;
            }
            
            #logout-warning-popup.show {
                display: block;
            }
            
            .logout-popup-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                backdrop-filter: blur(4px);
            }
            
            .logout-popup-content {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 2.5rem;
                border-radius: 16px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                max-width: 450px;
                width: 90%;
                text-align: center;
                animation: slideUp 0.3s ease;
            }
            
            .logout-popup-icon {
                width: 80px;
                height: 80px;
                margin: 0 auto 1.5rem;
                background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                animation: pulse 2s infinite;
            }
            
            .logout-popup-icon i {
                font-size: 2.5rem;
                color: white;
            }
            
            .logout-popup-content h3 {
                font-size: 1.75rem;
                color: #1a1a1a;
                margin-bottom: 1rem;
                font-weight: 600;
            }
            
            .logout-popup-content p {
                color: #666;
                font-size: 1.1rem;
                margin-bottom: 1rem;
                line-height: 1.6;
            }
            
            .logout-hint {
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 0.75rem 1rem;
                border-radius: 8px;
                margin: 1.5rem 0;
                font-size: 1rem !important;
            }
            
            #countdown {
                color: #dc3545;
                font-size: 1.3rem;
                font-weight: 700;
            }
            
            .logout-popup-buttons {
                display: flex;
                gap: 1rem;
                margin-top: 2rem;
            }
            
            .logout-popup-buttons button {
                flex: 1;
                padding: 0.875rem 1.5rem;
                border: none;
                border-radius: 8px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .btn-stay {
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                color: white;
            }
            
            .btn-stay:hover {
                background: linear-gradient(135deg, #218838 0%, #1aa179 100%);
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
            }
            
            .btn-logout {
                background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
                color: white;
            }
            
            .btn-logout:hover {
                background: linear-gradient(135deg, #c82333 0%, #bd2130 100%);
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translate(-50%, -40%);
                }
                to {
                    opacity: 1;
                    transform: translate(-50%, -50%);
                }
            }
            
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
            
            @media (max-width: 576px) {
                .logout-popup-content {
                    padding: 2rem 1.5rem;
                }
                
                .logout-popup-buttons {
                    flex-direction: column;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Show warning popup
    function showWarning() {
        const popup = document.getElementById('logout-warning-popup');
        if (popup) {
            popup.classList.add('show');
            startCountdown();
        }
    }
    
    // Hide warning popup
    function hideWarning() {
        const popup = document.getElementById('logout-warning-popup');
        if (popup) {
            popup.classList.remove('show');
        }
    }
    
    // Countdown timer
    function startCountdown() {
        let timeLeft = WARNING_TIME / 1000; // Convert to seconds
        const countdownElement = document.getElementById('countdown');
        
        const interval = setInterval(() => {
            timeLeft--;
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            countdownElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            if (timeLeft <= 0) {
                clearInterval(interval);
                window.location.href = '/logout';
            }
        }, 1000);
        
        // Store interval ID to clear it if user stays logged in
        popup.countdownInterval = interval;
    }
    
    // Reset timers
    function resetTimers() {
        clearTimeout(warningTimeout);
        clearTimeout(logoutTimeout);
        
        lastActivity = Date.now();
        
        // Set new timers
        warningTimeout = setTimeout(showWarning, POPUP_DISPLAY_TIME);
        logoutTimeout = setTimeout(() => {
            window.location.href = '/logout';
        }, SESSION_TIMEOUT);
    }
    
    // Track user activity
    function trackActivity() {
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
        
        events.forEach(event => {
            document.addEventListener(event, () => {
                const now = Date.now();
                // Only reset if more than 1 minute has passed since last activity
                if (now - lastActivity > 60000) {
                    hideWarning();
                    resetTimers();
                }
            }, { passive: true });
        });
    }
    
    // Initialize
    function init() {
        createLogoutPopup();
        resetTimers();
        trackActivity();
        
        // Button event listeners
        document.getElementById('stay-logged-in').addEventListener('click', () => {
            hideWarning();
            resetTimers();
            
            // Clear countdown interval
            const popup = document.getElementById('logout-warning-popup');
            if (popup.countdownInterval) {
                clearInterval(popup.countdownInterval);
            }
        });
        
        document.getElementById('logout-now').addEventListener('click', () => {
            window.location.href = '/logout';
        });
    }
    
    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
