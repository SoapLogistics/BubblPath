const CONFIG = {
    backendUrl: "http://localhost:8000" // Configure via environment or storage
};

function getStatus() {
    fetch(`${CONFIG.backendUrl}/api/joe/status`)
        .then(res => res.json())
        .then(data => console.log(data))
        .catch(err => console.error(err));
}
