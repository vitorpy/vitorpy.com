(function() {
    // Skip tracking for bots
    const isBot = () => {
        const ua = navigator.userAgent || '';
        const botRegex = /(googlebot|bingbot|slurp|duckduckbot|baiduspider|yandexbot|sogou|exabot|facebot|facebookexternalhit|ia_archiver|vercel-screenshot|lighthouse)/i;
        return botRegex.test(ua);
    };

    if (isBot()) {
        console.log('[tracking] Bot detected, skipping');
        return;
    }

    // Collect fingerprinting data
    const collectData = async () => {
        const data = {
            userAgent: navigator.userAgent,
            language: navigator.language,
            languages: navigator.languages,
            platform: navigator.platform,
            hardwareConcurrency: navigator.hardwareConcurrency,
            deviceMemory: navigator.deviceMemory,
            screenResolution: `${screen.width}x${screen.height}`,
            screenColorDepth: screen.colorDepth,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            referrer: document.referrer,
            url: window.location.href,
            sig: window.location.pathname
        };

        // Get permissions
        data.permissions = {};
        try {
            const cameraResult = await navigator.permissions.query({ name: 'camera' });
            data.permissions.camera = cameraResult.state;
        } catch {}
        try {
            const micResult = await navigator.permissions.query({ name: 'microphone' });
            data.permissions.microphone = micResult.state;
        } catch {}

        // Get battery info
        try {
            const battery = await navigator.getBattery();
            data.battery = {
                level: battery.level,
                charging: battery.charging
            };
        } catch {}

        // Get audio context
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            data.audioSampleRate = audioContext.sampleRate;
            audioContext.close();
        } catch {}

        // Get WebGL renderer
        try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
            if (debugInfo) {
                data.webglRenderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                data.renderer = data.webglRenderer;
            }
        } catch {}

        // Get canvas fingerprint
        try {
            const canvas = document.createElement('canvas');
            canvas.width = 200;
            canvas.height = 50;
            const ctx = canvas.getContext('2d');
            
            ctx.textBaseline = 'top';
            ctx.font = '14px Arial';
            ctx.fillStyle = '#f60';
            ctx.fillRect(125, 1, 62, 20);
            ctx.fillStyle = '#069';
            ctx.fillText('Canvas fingerprint', 2, 15);
            ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
            ctx.fillText('Canvas fingerprint', 4, 17);
            
            data.canvas = canvas.toDataURL();
        } catch {}

        // Get IP address (from public API)
        try {
            const ipResponse = await fetch('https://api.ipify.org?format=json');
            const ipData = await ipResponse.json();
            data.ip = ipData.ip;
        } catch {}

        return data;
    };

    // Send data to API
    const sendData = async (data) => {
        try {
            const response = await fetch('/api/fp-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            console.log('[tracking] Data sent:', response.status);
        } catch (err) {
            console.error('[tracking] Failed to send data:', err);
        }
    };

    // Initialize tracking
    const init = async () => {
        const data = await collectData();
        await sendData(data);
    };

    // Wait for page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();