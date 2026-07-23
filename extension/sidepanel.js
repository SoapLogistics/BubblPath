// sidepanel.js

document.addEventListener('DOMContentLoaded', () => {
  const btnReadPage = document.getElementById('btn-read-page');
  const btnKalshiTest = document.getElementById('btn-kalshi-test');
  const btnPrepareKalshi = document.getElementById('btn-prepare-kalshi');
  const btnAnalyzeSports = document.getElementById('btn-analyze-sports');
  const btnStop = document.getElementById('btn-stop');
  const chatBox = document.getElementById('chat');
  const statusDiv = document.getElementById('status');
  const kalshiOrderForm = document.getElementById('kalshi-order-form');

  // Phase 4 Elements
  const btnScrollDown = document.getElementById('btn-scroll-down');
  const btnHighlightText = document.getElementById('btn-highlight-text');

  // Phase 5 Elements
  const btnStartBjDrill = document.getElementById('btn-start-bj-drill');
  const bjDrillArea = document.getElementById('bj-drill-area');
  const bjCardDisplay = document.getElementById('bj-card-display');
  const bjUserCount = document.getElementById('bj-user-count');
  const btnSubmitBjCount = document.getElementById('btn-submit-bj-count');

  function appendMessage(sender, text, isHtml = false) {
    const p = document.createElement('p');
    const strong = document.createElement('strong');
    strong.textContent = `${sender}: `;
    p.appendChild(strong);

    if (isHtml) {
      // Use carefully when rendering controlled HTML (e.g., formatting payloads or bolding internal messages)
      const span = document.createElement('span');
      span.innerHTML = text;
      p.appendChild(span);
    } else {
      // Default to safe textContent for untrusted external data
      p.appendChild(document.createTextNode(text));
    }

    chatBox.appendChild(p);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  // --- Phase 1: Observer ---
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
        appendMessage('Solomon', `I see you are on: ${response.title}`);
        if (response.hasSensitiveFields) {
          appendMessage('System Warning', 'Sensitive fields detected on this page. Financial actions are hard-stopped.');
        }
        appendMessage('Solomon', `Preview text loaded (${response.contentPreview.length} chars). Ready for analysis.`);
      }
    });
  });

  // --- Phase 2: Researcher ---
  btnKalshiTest.addEventListener('click', () => {
    appendMessage('Solomon', 'Querying Kalshi Public APIs for related markets...');
    // Simulated API call delay
    setTimeout(() => {
      appendMessage('Solomon', 'Market implied probability is 42%. My internal estimate based on news sentiment is 60%. Edge is +18%.');
      appendMessage('Solomon', 'Recommendation: Construct LIMIT YES order.');
      kalshiOrderForm.classList.remove('hidden');
    }, 1200);
  });

  btnAnalyzeSports.addEventListener('click', () => {
    const line = document.getElementById('sports-line').value;
    if (!line) {
      appendMessage('Solomon', 'Please enter a sports line to analyze.');
      return;
    }
    appendMessage('Solomon', `Routing "${line}" to local Loki Engine...`);
    setTimeout(() => {
      appendMessage('Loki Engine', `Analyzed ${line}. Break-even: 52.38%. Shin True Prob: 54.1%. Edge: +1.72%. Rec: Pass or use 0.25x fractional Kelly.`);
    }, 1000);
  });

  // --- Phase 4: Controlled Browser Actions ---
  btnScrollDown.addEventListener('click', () => {
    appendMessage('Solomon', 'Executing scroll down action.');
    chrome.runtime.sendMessage({ type: 'EXECUTE_ACTION', action: 'page.scroll', direction: 'down' });
  });

  btnHighlightText.addEventListener('click', () => {
    appendMessage('Solomon', 'Highlighting currently selected text on page.');
    chrome.runtime.sendMessage({ type: 'EXECUTE_ACTION', action: 'page.highlight' });
  });

  // --- Phase 3: Preparer ---
  btnPrepareKalshi.addEventListener('click', () => {
    const ticker = document.getElementById('kalshi-ticker').value;
    const type = document.getElementById('kalshi-type').value;
    const price = document.getElementById('kalshi-price').value;
    const quantity = document.getElementById('kalshi-quantity').value;

    const payload = {
      action: "order.prepare",
      ticker: ticker,
      type: type,
      yes_price: parseInt(price),
      count: parseInt(quantity)
    };

    appendMessage('Solomon', 'Preparing trade payload. <strong>I cannot submit this.</strong>', true);
    appendMessage('Solomon Payload', `<pre style="background:#f3f4f6;padding:4px;border-radius:4px;font-size:0.75rem;white-space:pre-wrap;">${JSON.stringify(payload, null, 2)}</pre>`, true);
    appendMessage('System', 'You must manually copy this payload or click the final submission button on the Kalshi UI.');
  });

  // --- Phase 5: Blackjack Training Lab ---
  let currentBjCount = 0;
  const bjCards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];
  let currentCard = '';

  btnStartBjDrill.addEventListener('click', () => {
    appendMessage('Solomon Lab', 'Starting Hi-Lo running count drill. (Offline Simulation)');
    bjDrillArea.classList.remove('hidden');
    currentBjCount = 0;
    drawNextBjCard();
  });

  function drawNextBjCard() {
    currentCard = bjCards[Math.floor(Math.random() * bjCards.length)];
    bjCardDisplay.textContent = currentCard;
    bjUserCount.value = '';

    // Update internal true count
    if (['2', '3', '4', '5', '6'].includes(currentCard)) {
      currentBjCount += 1;
    } else if (['10', 'J', 'Q', 'K', 'A'].includes(currentCard)) {
      currentBjCount -= 1;
    }
  }

  btnSubmitBjCount.addEventListener('click', () => {
    const userVal = parseInt(bjUserCount.value);
    if (isNaN(userVal)) {
      appendMessage('Solomon Lab', 'Please enter a valid number.');
      return;
    }

    if (userVal === currentBjCount) {
      appendMessage('Solomon Lab', 'Correct!');
      drawNextBjCard();
    } else {
      appendMessage('Solomon Lab', `Incorrect. The running count was ${currentBjCount}. Try again.`);
    }
  });

  // --- Emergency ---
  btnStop.addEventListener('click', () => {
    statusDiv.innerText = "Mode: STOPPED";
    statusDiv.style.color = "red";
    statusDiv.style.fontWeight = "bold";
    appendMessage('SYSTEM', 'All Solomon activities halted. Connection to local runtime severed.');
    kalshiOrderForm.classList.add('hidden');
  });
});
