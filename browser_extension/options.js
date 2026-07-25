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
        document.getElementById('status').textContent = 'Options saved.';
        setTimeout(() => document.getElementById('status').textContent = '', 2000);
    });
});
