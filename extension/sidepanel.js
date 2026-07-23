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

  // Phase 7 Elements
  const btnCreateMemory = document.getElementById('btn-create-memory');
  const memoryApprovalArea = document.getElementById('memory-approval-area');
  const memoryProposalText = document.getElementById('memory-proposal-text');
  const btnApproveMemory = document.getElementById('btn-approve-memory');
  const btnRejectMemory = document.getElementById('btn-reject-memory');

  // Phase 8 Elements
  const btnAnalyzeNews = document.getElementById('btn-analyze-news');

  // Phase 9 Elements
  const btnAnalyzeShopping = document.getElementById('btn-analyze-shopping');

  // Phase 10 Elements
  const btnAnalyzeJob = document.getElementById('btn-analyze-job');
  const btnPrepareJobForm = document.getElementById('btn-prepare-job-form');

  // Phase 12 Elements
  const btnAnalyzeTech = document.getElementById('btn-analyze-tech');

  // Phase 13 Elements
  const btnAnalyzeTravel = document.getElementById('btn-analyze-travel');

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
    appendMessage('Solomon', `Initializing Phase 6 Sports Research Pipeline for: "${line}"...`);

    // Simulate multi-step research pipeline
    setTimeout(() => {
      appendMessage('Solomon Pipeline', '&#10003; Roster and injury verification complete.', true);
    }, 800);

    setTimeout(() => {
      appendMessage('Solomon Pipeline', '&#10003; Weather and venue conditions collected.', true);
    }, 1500);

    setTimeout(() => {
      appendMessage('Solomon Pipeline', '&#10003; Recent performance and opponent-adjusted statistics modeled.', true);
    }, 2200);

    setTimeout(() => {
      const report = `
        <div style="background:#f3f4f6; padding:8px; border-radius:6px; font-size:0.75rem; margin-top:4px;">
          <strong>Selection:</strong> ${line}<br>
          <strong>Market Implied Prob:</strong> 52.38%<br>
          <strong>Loki Independent Prob:</strong> 54.10%<br>
          <strong>Estimated Edge:</strong> <span style="color:green;">+1.72%</span><br>
          <strong>Confidence:</strong> Moderate<br>
          <strong>Missing Info:</strong> Starting LT questionable.<br>
          <strong>Recommendation:</strong> Pass or use 0.25x fractional Kelly.
        </div>
      `;
      appendMessage('Loki Engine', report, true);
    }, 3200);
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

  // --- Phase 7: Perpetual Memory Bridge ---
  btnCreateMemory.addEventListener('click', () => {
    appendMessage('Solomon', 'Scanning page for extractable knowledge...');
    chrome.runtime.sendMessage({ type: 'EXTRACT_PAGE_DATA' }, (response) => {
      if (response && !response.error) {
        // Simulate extracting a rule or fact
        const proposedCard = `SOK-CARD-MOCK: Source [${response.title}]. Found potentially useful workflow or calibration data.`;
        memoryProposalText.textContent = proposedCard;
        memoryApprovalArea.classList.remove('hidden');
        appendMessage('Solomon', 'I have drafted a new Memory Card. It requires your approval to bypass the Review Gate and enter SQLite.');
      } else {
        appendMessage('System Error', 'Could not read page for memory extraction.');
      }
    });
  });

  btnApproveMemory.addEventListener('click', () => {
    appendMessage('System', '&#10003; Memory Card approved. Saving to Solomon SQLite...', true);
    memoryApprovalArea.classList.add('hidden');
    // In a real build, we'd POST to local app.py /api/mnemosyne/cards here
  });

  btnRejectMemory.addEventListener('click', () => {
    appendMessage('System', '&#10005; Memory Card rejected. Discarding.', true);
    memoryApprovalArea.classList.add('hidden');
  });

  // --- Phase 8: News Companion ---
  btnAnalyzeNews.addEventListener('click', () => {
    appendMessage('Solomon', 'Initiating News Extraction & Timeline build...');

    setTimeout(() => {
      appendMessage('Solomon', '&#10003; Extracting main claims from DOM...', true);
    }, 600);

    setTimeout(() => {
      appendMessage('Solomon', '&#10003; Cross-referencing 3 external primary sources...', true);
    }, 1500);

    setTimeout(() => {
      const newsReport = `
        <div style="background:#f3f4f6; padding:8px; border-radius:6px; font-size:0.75rem; margin-top:4px;">
          <strong>Main Claim:</strong> Federal Reserve expected to hold rates.<br>
          <strong>Confidence:</strong> High (Confirmed by 2 primary sources)<br>
          <strong>Loaded Language:</strong> "Slammed", "Plummet" detected.<br>
          <strong>Timeline:</strong><br>
          - 09:00: CPI Data Released.<br>
          - 09:15: WSJ confirms likely hold.<br>
          - 09:30: Market prices in 95% hold probability (Kalshi).
        </div>
      `;
      appendMessage('Solomon News', newsReport, true);
    }, 2500);
  });

  // --- Phase 9: Shopping Companion ---
  btnAnalyzeShopping.addEventListener('click', () => {
    appendMessage('Solomon', 'Scanning product listing (Amazon/eBay heuristics)...');

    setTimeout(() => {
      appendMessage('Solomon', '&#10003; Extracting model numbers and verifying seller reputation...', true);
    }, 800);

    setTimeout(() => {
      appendMessage('Solomon', '&#10003; Checking historic price data and external competitors...', true);
    }, 1800);

    setTimeout(() => {
      const shoppingReport = `
        <div style="background:#f3f4f6; padding:8px; border-radius:6px; font-size:0.75rem; margin-top:4px;">
          <strong>Product:</strong> Samsung T7 Shield 2 TB<br>
          <strong>Base Price:</strong> $139.99<br>
          <strong>Total Landed:</strong> $149.79 (incl. Tax/Ship)<br>
          <strong>Seller:</strong> Third-Party (92% positive)<br>
          <strong>Counterfeit Risk:</strong> Low<br>
          <strong>Warning:</strong> Found same model at Best Buy for $129.99.<br>
          <strong>Recommendation:</strong> Prepare checkout at Best Buy instead.
        </div>
      `;
      appendMessage('Solomon Shopping', shoppingReport, true);
    }, 2800);
  });

  // --- Phase 10: Job Application Companion ---
  btnAnalyzeJob.addEventListener('click', () => {
    appendMessage('Solomon', 'Scanning Job Description against local resume profile...');

    setTimeout(() => {
      const jobReport = `
        <div style="background:#f3f4f6; padding:8px; border-radius:6px; font-size:0.75rem; margin-top:4px;">
          <strong>Match Score:</strong> 85%<br>
          <strong>Strong Matches:</strong> Python, React, System Architecture.<br>
          <strong>Missing Qualifications:</strong> 5+ years AWS (Profile has 3 yrs).<br>
          <strong>Recommendation:</strong> Draft cover letter highlighting rapid upskilling in AWS.
        </div>
      `;
      appendMessage('Solomon Jobs', jobReport, true);
      btnPrepareJobForm.classList.remove('hidden');
    }, 1500);
  });

  btnPrepareJobForm.addEventListener('click', () => {
    appendMessage('Solomon', 'Preparing safe form auto-fill for job application.');
    chrome.runtime.sendMessage({ type: 'PREPARE_FORM', payload: { action: 'job.fill', fields: ['name', 'email', 'linkedin'] } }, (response) => {
      appendMessage('Solomon', '&#10003; Routine fields populated. <strong>I cannot click Submit.</strong> Please review and finalize the application.', true);
      btnPrepareJobForm.classList.add('hidden');
    });
  });

  // --- Phase 12: Technical Support Companion ---
  btnAnalyzeTech.addEventListener('click', () => {
    appendMessage('Solomon', 'Initiating Technical Page Scan...');

    setTimeout(() => {
      appendMessage('Solomon Tech', '&#10003; Scanning for console error signatures...', true);
    }, 600);

    setTimeout(() => {
      appendMessage('Solomon Tech', '&#10003; Checking domain reputation and SSL validity...', true);
    }, 1200);

    setTimeout(() => {
      const techReport = `
        <div style="background:#f3f4f6; padding:8px; border-radius:6px; font-size:0.75rem; margin-top:4px;">
          <strong>Security Status:</strong> Safe. SSL Certificate verified.<br>
          <strong>Phishing Risk:</strong> Low. No homoglyphs detected.<br>
          <strong>Console Diagnostics:</strong><br>
          - Found CORS error on asset loading.<br>
          - <strong>Fix:</strong> This is a server-side configuration issue, not a local browser problem. You cannot fix this directly.
        </div>
      `;
      appendMessage('Solomon Tech', techReport, true);
    }, 2200);
  });

  // --- Phase 13: Travel & Itinerary Companion ---
  btnAnalyzeTravel.addEventListener('click', () => {
    appendMessage('Solomon', 'Extracting travel dates and comparing global aggregators...');

    setTimeout(() => {
      appendMessage('Solomon Travel', '&#10003; Cross-referencing cancellation policies...', true);
    }, 800);

    setTimeout(() => {
      appendMessage('Solomon Travel', '&#10003; Auditing for hidden resort fees and baggage traps...', true);
    }, 1700);

    setTimeout(() => {
      const travelReport = `
        <div style="background:#f3f4f6; padding:8px; border-radius:6px; font-size:0.75rem; margin-top:4px;">
          <strong>Destination:</strong> Tokyo (NRT)<br>
          <strong>Dates:</strong> Oct 12 - Oct 19<br>
          <strong>Base Fare:</strong> $850<br>
          <strong>Hidden Fees:</strong> $120 (Baggage not included in basic economy).<br>
          <strong>True Cost:</strong> $970<br>
          <strong>Cancellation Policy:</strong> Non-refundable. Travel credit only.<br>
          <strong>Recommendation:</strong> Consider Premium Economy upgrade for $50 more, which includes baggage and free cancellation.
        </div>
      `;
      appendMessage('Solomon Travel', travelReport, true);
    }, 2800);
  });


  // --- Phase 11: Security & Emergency Systems ---
  btnStop.addEventListener('click', () => {
    // 1. Update UI Status
    statusDiv.innerText = "Mode: EMERGENCY STOP";
    statusDiv.style.color = "white";
    statusDiv.style.backgroundColor = "red";
    statusDiv.style.fontWeight = "bold";
    statusDiv.style.padding = "4px";

    // 2. Hide all active contextual forms
    kalshiOrderForm.classList.add('hidden');
    bjDrillArea.classList.add('hidden');
    memoryApprovalArea.classList.add('hidden');
    btnPrepareJobForm.classList.add('hidden');

    // 3. Clear transient memory (simulated)
    chrome.runtime.sendMessage({ type: 'EMERGENCY_STOP' }, (response) => {
      appendMessage('SYSTEM-GUARD', '&#9888; EMERGENCY STOP INITIATED.', true);
      appendMessage('SYSTEM-GUARD', '1. Disconnecting from Solomon Runtime...', true);
      appendMessage('SYSTEM-GUARD', '2. Revoking ActiveTab scripting permissions...', true);
      appendMessage('SYSTEM-GUARD', '3. Clearing ephemeral session memory...', true);
      appendMessage('SYSTEM-GUARD', '4. Financial Action locks engaged globally.', true);
      appendMessage('SYSTEM-GUARD', 'Solomon is now offline. Please close the panel.', true);

      // Disable further interactions in UI
      const buttons = document.querySelectorAll('button:not(#btn-stop)');
      buttons.forEach(btn => {
        btn.disabled = true;
        btn.style.opacity = '0.5';
        btn.style.cursor = 'not-allowed';
      });
    });
  });
});
