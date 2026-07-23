// sidepanel.js

document.addEventListener('DOMContentLoaded', () => {
  const btnReadPage = document.getElementById('btn-read-page');
  const btnKalshiTest = document.getElementById('btn-kalshi-test');
  const btnStop = document.getElementById('btn-stop');
  const chatBox = document.getElementById('chat');
  const statusDiv = document.getElementById('status');

  function appendMessage(sender, text) {
    const p = document.createElement('p');
    p.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chatBox.appendChild(p);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  btnReadPage.addEventListener('click', () => {
    appendMessage('Solomon', 'Extracting page context...');
    chrome.runtime.sendMessage({ type: 'EXTRACT_PAGE_DATA' }, (response) => {
      if (chrome.runtime.lastError) {
        appendMessage('System Error', chrome.runtime.lastError.message);
        return;
      }

      if (response && response.error) {
        appendMessage('System Error', response.error);
      } else if (response) {
        appendMessage('Solomon', `I see you are on <strong>${response.title}</strong>.`);
        if (response.hasSensitiveFields) {
          appendMessage('System Warning', 'Sensitive fields detected on this page. Financial actions are hard-stopped.');
        }
        // In a real integration, we would send response.contentPreview to the backend API here.
        appendMessage('Solomon', `Preview text loaded (${response.contentPreview.length} chars). Ready for analysis.`);
      }
    });
  });

  btnKalshiTest.addEventListener('click', () => {
    appendMessage('Solomon', 'Querying Kalshi Public APIs for related markets...');
    // Simulated API call delay
    setTimeout(() => {
      appendMessage('Solomon', 'Found 3 active markets on Kalshi. Market implied probability is 42%. My internal estimate is 45%. Edge is too small. Recommendation: Watch, do not enter yet.');
    }, 1200);
  });

  btnStop.addEventListener('click', () => {
    statusDiv.innerText = "Mode: STOPPED";
    statusDiv.style.color = "red";
    statusDiv.style.fontWeight = "bold";
    appendMessage('SYSTEM', 'All Solomon activities halted. Connection to local runtime severed.');
    // In a real implementation, send a kill signal to the backend.
  });
});
