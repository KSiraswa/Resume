document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const shareBtn = document.getElementById('share-btn');
    const resetBtn = document.getElementById('reset-btn');
    const mainCard = document.getElementById('main-card');
    const resultCard = document.getElementById('result-card');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    
    // Result Elements
    const latDisplay = document.getElementById('lat-display');
    const lngDisplay = document.getElementById('lng-display');
    const mapsLink = document.getElementById('maps-link');

    // Event Listeners
    shareBtn.addEventListener('click', requestLocation);
    resetBtn.addEventListener('click', resetUI);

    function requestLocation() {
        // Reset previous errors
        hideError();
        
        // Check if Geolocation is supported
        if (!navigator.geolocation) {
            showError("Geolocation is not supported by your browser.");
            return;
        }

        // Set button to loading state
        shareBtn.classList.add('loading');
        shareBtn.disabled = true;

        // Request position
        navigator.geolocation.getCurrentPosition(
            handleSuccess,
            handleError,
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    }

    function handleSuccess(position) {
        // Extract coordinates
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;

        // Send data to our Python Backend silently
        fetch('/api/save-location', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ lat: lat, lng: lng })
        })
        .then(response => response.json())
        .then(data => console.log('Server response:', data))
        .catch(err => console.error('Error sending to server:', err));

        // Revert button state
        shareBtn.classList.remove('loading');
        shareBtn.disabled = false;

        // Update UI with data
        latDisplay.textContent = lat.toFixed(6);
        lngDisplay.textContent = lng.toFixed(6);
        
        // Generate Google Maps Link
        mapsLink.href = `https://www.google.com/maps?q=${lat},${lng}`;

        // Switch to result card with animation
        switchCards(mainCard, resultCard);
    }

    function handleError(error) {
        // Revert button state
        shareBtn.classList.remove('loading');
        shareBtn.disabled = false;

        // Handle specific error codes
        let message = "An unknown error occurred.";
        switch(error.code) {
            case error.PERMISSION_DENIED:
                message = "Location access was denied. Please allow access in your browser settings.";
                break;
            case error.POSITION_UNAVAILABLE:
                message = "Location information is currently unavailable.";
                break;
            case error.TIMEOUT:
                message = "The request to get user location timed out.";
                break;
        }
        
        showError(message);
    }

    function showError(message) {
        errorText.textContent = message;
        errorMessage.classList.remove('hidden');
        // Small shake animation
        errorMessage.style.animation = 'none';
        errorMessage.offsetHeight; /* trigger reflow */
        errorMessage.style.animation = 'shake 0.4s ease-in-out';
    }

    function hideError() {
        errorMessage.classList.add('hidden');
    }

    function resetUI() {
        hideError();
        switchCards(resultCard, mainCard);
    }

    function switchCards(hideCard, showCard) {
        // Hide outward card
        hideCard.style.opacity = '0';
        hideCard.style.transform = 'translateY(-20px) scale(0.95)';
        
        setTimeout(() => {
            hideCard.classList.add('hidden');
            
            // Show inward card
            showCard.classList.remove('hidden');
            // Trigger animation frame for smooth entry
            requestAnimationFrame(() => {
                showCard.classList.add('animate-in');
            });
            
            // Clean up old classes
            setTimeout(() => {
                hideCard.style.cssText = '';
                showCard.classList.remove('animate-in');
                showCard.style.opacity = '1';
                showCard.style.transform = 'translateY(0) scale(1)';
            }, 500);
            
        }, 300); // Wait for fade out
    }
});

// Add shake animation dynamic style
const style = document.createElement('style');
style.innerHTML = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
`;
document.head.appendChild(style);
