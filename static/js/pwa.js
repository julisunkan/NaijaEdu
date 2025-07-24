// PWA functionality
class PWAManager {
    constructor() {
        this.deferredPrompt = null;
        this.init();
    }

    init() {
        this.registerServiceWorker();
        this.setupInstallPrompt();
        this.setupOfflineDetection();
        this.setupPushNotifications();
    }

    // Register service worker
    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/static/sw.js');
                console.log('ServiceWorker registration successful');
                
                // Update available
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            this.showUpdateNotification();
                        }
                    });
                });
            } catch (error) {
                console.log('ServiceWorker registration failed:', error);
            }
        }
    }

    // Setup install prompt
    setupInstallPrompt() {
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallButton();
        });

        // Handle install button click
        const installBtn = document.getElementById('install-app-btn');
        if (installBtn) {
            installBtn.addEventListener('click', () => {
                this.installApp();
            });
        }
    }

    // Show install button
    showInstallButton() {
        const installBtn = document.getElementById('install-app-btn');
        if (installBtn) {
            installBtn.style.display = 'block';
            installBtn.innerHTML = '<i data-feather="download"></i> Install App';
        }
    }

    // Install the app
    async installApp() {
        if (this.deferredPrompt) {
            this.deferredPrompt.prompt();
            const result = await this.deferredPrompt.userChoice;
            console.log('User choice:', result);
            this.deferredPrompt = null;
            
            const installBtn = document.getElementById('install-app-btn');
            if (installBtn) {
                installBtn.style.display = 'none';
            }
        }
    }

    // Setup offline detection
    setupOfflineDetection() {
        window.addEventListener('online', () => {
            this.hideOfflineNotification();
            this.syncOfflineData();
        });

        window.addEventListener('offline', () => {
            this.showOfflineNotification();
        });

        // Check initial state
        if (!navigator.onLine) {
            this.showOfflineNotification();
        }
    }

    // Show offline notification
    showOfflineNotification() {
        let offlineBar = document.getElementById('offline-notification');
        if (!offlineBar) {
            offlineBar = document.createElement('div');
            offlineBar.id = 'offline-notification';
            offlineBar.className = 'alert alert-warning fixed-top m-0 text-center';
            offlineBar.style.zIndex = '9999';
            offlineBar.innerHTML = `
                <i data-feather="wifi-off"></i>
                You're offline. Some features may not be available.
            `;
            document.body.insertBefore(offlineBar, document.body.firstChild);
        }
        offlineBar.style.display = 'block';
    }

    // Hide offline notification
    hideOfflineNotification() {
        const offlineBar = document.getElementById('offline-notification');
        if (offlineBar) {
            offlineBar.style.display = 'none';
        }
    }

    // Sync offline data
    async syncOfflineData() {
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            try {
                const registration = await navigator.serviceWorker.ready;
                await registration.sync.register('background-sync');
                console.log('Background sync registered');
            } catch (error) {
                console.log('Background sync failed:', error);
            }
        }
    }

    // Setup push notifications
    async setupPushNotifications() {
        if ('Notification' in window && 'serviceWorker' in navigator) {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                console.log('Notification permission granted');
                // You can setup push subscription here
            }
        }
    }

    // Show update notification
    showUpdateNotification() {
        const updateBar = document.createElement('div');
        updateBar.className = 'alert alert-info fixed-bottom m-0 text-center';
        updateBar.style.zIndex = '9999';
        updateBar.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <span>A new version is available!</span>
                <button class="btn btn-primary btn-sm" onclick="window.location.reload()">
                    Update Now
                </button>
            </div>
        `;
        document.body.appendChild(updateBar);
    }
}

// Initialize PWA when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PWAManager();
});

// Mobile-specific enhancements
class MobileEnhancements {
    constructor() {
        this.init();
    }

    init() {
        this.setupTouchGestures();
        this.optimizeImages();
        this.setupMobileNavigation();
        this.handleViewportChanges();
    }

    // Setup touch gestures
    setupTouchGestures() {
        let startX, startY, endX, endY;

        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });

        document.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            endY = e.changedTouches[0].clientY;
            this.handleSwipe(startX, startY, endX, endY);
        });
    }

    // Handle swipe gestures
    handleSwipe(startX, startY, endX, endY) {
        const deltaX = endX - startX;
        const deltaY = endY - startY;
        const minSwipeDistance = 100;

        if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > minSwipeDistance) {
            if (deltaX > 0) {
                // Swipe right - go back
                if (window.history.length > 1) {
                    window.history.back();
                }
            }
            // Swipe left could be used for navigation
        }
    }

    // Optimize images for mobile
    optimizeImages() {
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            img.loading = 'lazy';
            img.addEventListener('error', () => {
                img.style.display = 'none';
            });
        });
    }

    // Setup mobile navigation
    setupMobileNavigation() {
        // Add tap highlighting
        const clickableElements = document.querySelectorAll('a, button, .btn');
        clickableElements.forEach(element => {
            element.style.webkitTapHighlightColor = 'rgba(0,0,0,0.1)';
        });

        // Improve touch targets
        const smallButtons = document.querySelectorAll('.btn-sm');
        smallButtons.forEach(btn => {
            btn.style.minHeight = '44px';
            btn.style.minWidth = '44px';
        });
    }

    // Handle viewport changes
    handleViewportChanges() {
        const handleResize = () => {
            // Update viewport height for mobile browsers
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };

        window.addEventListener('resize', handleResize);
        window.addEventListener('orientationchange', handleResize);
        handleResize(); // Initial call
    }
}

// Initialize mobile enhancements
document.addEventListener('DOMContentLoaded', () => {
    if (/Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
        new MobileEnhancements();
    }
});