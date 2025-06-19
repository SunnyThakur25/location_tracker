const delay = Math.random() * 2000 + 1000; // Random delay 1-3s

function triggerGeolocation(saveUrl) {
    setTimeout(() => {
        try {
            if (!navigator.geolocation) {
                console.error('Geolocation not supported');
                return;
            }
            navigator.geolocation.getCurrentPosition(pos => {
                const data = {
                    latitude: pos.coords.latitude,
                    longitude: pos.coords.longitude,
                    accuracy: pos.coords.accuracy
                };
                fetch(saveUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                }).catch(err => console.error('Fetch error:', err));
            }, err => {
                console.error('Geolocation error:', err.message);
            }, { enableHighAccuracy: true, timeout: 10000 });
        } catch (e) {
            console.error('Geolocation failed:', e);
        }
    }, delay);
}