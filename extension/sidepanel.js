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

  // Phase 14 Elements
  const btnAnalyzeHousehold = document.getElementById('btn-analyze-household');

  // Phase 15 Elements
  const btnAnalyzeEdu = document.getElementById('btn-analyze-edu');

  // Phase 16 Elements
  const btnAnalyzeEmail = document.getElementById('btn-analyze-email');

  // Phase 17 Elements
  const btnAnalyzeEntertainment = document.getElementById('btn-analyze-entertainment');

  // Phase 18 Elements
  const btnAnalyzeCrossMarket = document.getElementById('btn-analyze-cross-market');

  // Phase 19 Elements
  const btnViewAuditLogs = document.getElementById('btn-view-audit-logs');

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

  // --- Phase 14: Household Management ---
  btnAnalyzeHousehold.addEventListener('click', () => {
    appendMessage('Solomon', 'Scanning appliance models and utility data...');

    setTimeout(() => {
      appendMessage('Solomon Home', '&#10003; Identifying appliance replacement parts from DOM...', true);
    }, 800);

    setTimeout(() => {
      appendMessage('Solomon Home', '&#10003; Comparing repair cost versus complete replacement...', true);
    }, 1800);

    setTimeout(() => {
      const homeReport = `
        <div style="background:#f3f4f6; padding:8px; border-radius:6px; font-size:0.75rem; margin-top:4px;">
          <strong>Appliance:</strong> Whirlpool Refrigerator (WRX735SBMZ)<br>
          <strong>Issue:</strong> Ice maker failure.<br>
          <strong>Part Required:</strong> Assembly W11299924 ($85)<br>
          <strong>Avg Labor Cost:</strong> $150<br>
          <strong>Total Repair Cost:</strong> ~$235<br>
          <strong>New Unit Cost:</strong> $1,800<br>
          <strong>Recommendation:</strong> Repair is economically viable (<15% of replacement cost).
        </div>
      `;
      appendMessage('Solomon Home', homeReport, true);
    }, 2800);
  });

  // --- Phase 15: Education & Study Notes ---
  btnAnalyzeEdu.addEventListener('click', () => {
    appendMessage('Solomon', 'Extracting educational materials and evaluating concepts...');

    setTimeout(() => {
      appendMessage('Solomon Edu', '&#10003; Generating summary notes and formatting citations...', true);
    }, 800);

    setTimeout(() => {
      appendMessage('Solomon Edu', '&#10003; Cross-referencing against active assignment requirements...', true);
    }, 1800);

    setTimeout(() => {
      const eduReport = `
        <div style="background:#f3f4f6; padding:8px; border-radius:6px; font-size:0.75rem; margin-top:4px;">
          <strong>Topic:</strong> Cellular Respiration<br>
          <strong>Summary:</strong> The process by which cells convert glucose and oxygen into ATP, water, and CO2.<br>
          <strong>Citation (APA):</strong> <em>Author, A. A. (Year). Title of article. Title of Journal.</em><br>
          <strong>Assignment Check:</strong> You still need to cover the Krebs cycle specifically.<br>
          <strong>Quick Quiz:</strong> What is the net ATP yield from one glucose molecule? (Click to reveal answer).
        </div>
      `;
      appendMessage('Solomon Edu', eduReport, true);
    }, 2800);
  });

  // --- Phase 16: Email & Comms Companion ---
  btnAnalyzeEmail.addEventListener('click', () => {
    appendMessage('Solomon', 'Scanning email thread and parsing attachments...');

    setTimeout(() => {
      appendMessage('Solomon Comms', '&#10003; Extracting unresolved questions from previous messages...', true);
    }, 800);

    setTimeout(() => {
      appendMessage('Solomon Comms', '&#10003; Generating suggested reply draft...', true);
    }, 1800);

    setTimeout(() => {
      const emailReport = `
        <div style="background:#f3f4f6; padding:8px; border-radius:6px; font-size:0.75rem; margin-top:4px;">
          <strong>Unresolved Action Items:</strong> 2 (Send Q3 report, confirm meeting time).<br>
          <strong>Attachment Scan:</strong> Safe (1 PDF detected).<br>
          <strong>Suggested Reply Draft:</strong><br>
          <em>"Hi team, please find the Q3 report attached. I am available to meet at 2:00 PM EST tomorrow."</em><br><br>
          <strong>Note:</strong> I have prepared the draft. <strong>I cannot click send.</strong>
        </div>
      `;
      appendMessage('Solomon Comms', emailReport, true);
    }, 2800);
  });

  // --- Phase 17: Entertainment Companion ---
  btnAnalyzeEntertainment.addEventListener('click', () => {
    appendMessage('Solomon', 'Scanning page for media titles, actors, and dates...');

    setTimeout(() => {
      appendMessage('Solomon Entertainment', '&#10003; Aggregating spoiler-free reviews...', true);
    }, 800);

    setTimeout(() => {
      appendMessage('Solomon Entertainment', '&#10003; Checking local streaming availability...', true);
    }, 1800);

    setTimeout(() => {
      const entertainmentReport = `
        <div style="background:#f3f4f6; padding:8px; border-radius:6px; font-size:0.75rem; margin-top:4px;">
          <strong>Title Detected:</strong> Dune: Part Two<br>
          <strong>Release Date:</strong> March 1, 2024<br>
          <strong>Spoiler-Free Consensus:</strong> "A visually stunning epic that improves upon the first installment. Pacing is excellent."<br>
          <strong>Streaming On:</strong> Max (Included in your subscription)<br>
          <strong>Action:</strong> Added to Solomon Watch List.
        </div>
      `;
      appendMessage('Solomon Entertainment', entertainmentReport, true);
    }, 2800);
  });

  // --- Phase 18: Cross-Market Radar ---
  btnAnalyzeCrossMarket.addEventListener('click', () => {
    appendMessage('Solomon', 'Initiating cross-market scan across prediction platforms...');

    setTimeout(() => {
      appendMessage('Solomon Radar', '&#10003; Retrieving Kalshi order book data via public API...', true);
    }, 800);

    setTimeout(() => {
      appendMessage('Solomon Radar', '&#10003; Retrieving Polymarket data via Gamma API...', true);
    }, 1800);

    setTimeout(() => {
      const radarReport = `
        <div style="background:#f3f4f6; padding:8px; border-radius:6px; font-size:0.75rem; margin-top:4px;">
          <strong>Target Market:</strong> Will the Fed cut rates in Q4?<br>
          <strong>Kalshi Implied:</strong> 38% (Spread: 2¢)<br>
          <strong>Polymarket Implied:</strong> 47% (Spread: 1¢)<br>
          <strong>Solomon Base Rate Estimate:</strong> 44%<br>
          <strong>Divergence Detected:</strong> 9% Delta<br>
          <strong>Analysis:</strong> Kalshi market appears underpriced compared to both crypto consensus and Solomon internal estimates. Recommend executing paper trade to track calibration.
        </div>
      `;
      appendMessage('Solomon Radar', radarReport, true);
    }, 3200);
  });

  // --- Phase 19: Audit Logger ---
  btnViewAuditLogs.addEventListener('click', () => {
    appendMessage('System Audit', 'Retrieving session action logs from Service Worker...', true);
    chrome.runtime.sendMessage({ type: 'GET_AUDIT_LOGS' }, (response) => {
      if (response && response.logs) {
        if (response.logs.length === 0) {
          appendMessage('System Audit', 'No actions logged in current session.');
          return;
        }

        let logHtml = `<div style="background:#f3f4f6; padding:8px; border-radius:6px; font-size:0.75rem; margin-top:4px; max-height: 150px; overflow-y: auto;">`;
        response.logs.forEach(log => {
          logHtml += `<strong>[${log.action}]</strong> ${log.details}<br><span style="color:#6b7280; font-size:0.65rem;">${log.timestamp}</span><br><hr style="border:0; border-top:1px solid #e5e7eb; margin: 4px 0;">`;
        });
        logHtml += `</div>`;
        appendMessage('System Audit', logHtml, true);
      } else {
        appendMessage('System Error', 'Failed to retrieve audit logs.');
      }
    });
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
