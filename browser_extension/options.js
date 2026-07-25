document.addEventListener('DOMContentLoaded', () => {
    chrome.storage.local.get(['backendUrl', 'authKey'], (result) => {
        if (result.backendUrl) document.getElementById('backend-url').value = result.backendUrl;
        if (result.authKey) document.getElementById('auth-key').value = result.authKey;
    });
});

document.getElementById('save-btn').addEventListener('click', () => {
    const backendUrl = document.getElementById('backend-url').value;
    const authKey = document.getElementById('auth-key').value;

    chrome.storage.local.set({ backendUrl, authKey }, () => {
        const status = document.getElementById('status');
        status.textContent = 'Options saved.';
        status.style.color = 'green';
        setTimeout(() => status.textContent = '', 2000);
    });
});

document.getElementById('test-btn').addEventListener('click', async () => {
    const backendUrl = document.getElementById('backend-url').value;
    const authKey = document.getElementById('auth-key').value;
    const status = document.getElementById('status');

    status.textContent = 'Testing connection...';
    status.style.color = '#333';

    try {
        const response = await fetch(`${backendUrl}/health`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${authKey}`
            }
        });

        if (response.ok) {
            status.textContent = 'Connection Successful! Solomon is online.';
            status.style.color = 'green';
        } else {
            status.textContent = `Connection Failed: HTTP ${response.status} (Check Auth Key)`;
            status.style.color = 'red';
        }
    } catch (err) {
        status.textContent = `Connection Failed: ${err.message} (Is the server running?)`;
        status.style.color = 'red';
    }
});
