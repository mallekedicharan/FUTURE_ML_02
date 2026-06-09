const SAMPLE_TICKETS = [
    // Technical Issue - Critical
    "URGENT: My device is emitting smoke and making unusual sounds. I've immediately unplugged it. This could be a serious safety hazard that needs immediate attention!",
    "My laptop exploded while charging overnight. There is damage to my furniture. This is a serious safety issue. I have photos of the damage.",
    "Multiple devices in our office have simultaneously failed after a firmware update. This has brought our entire operations to a halt. 50 employees unable to work!",
    // Technical Issue - High
    "My laptop has completely stopped working. It was fine yesterday but now it won't turn on at all. I've tried charging it for hours. This is my primary work device and I need it urgently.",
    "After the latest system update, my tablet is completely bricked. It's stuck in a boot loop. I've lost access to all my work documents and have a critical deadline in two days.",
    "The screen on my monitor cracked spontaneously without any impact. There are visible lines across the display and touch functionality is completely gone.",
    // Technical Issue - Medium
    "The battery on my tablet is draining much faster than usual. It used to last all day but now barely makes it to noon. Could there be a software issue?",
    "My smartwatch has been running very slowly since the last update. Apps take forever to open and there's noticeable lag when typing.",
    "The audio on my wireless headphones is distorted when playing music or during calls. The speakers make a crackling sound at any volume level.",
    // Technical Issue - Low
    "I noticed a minor cosmetic scratch on my smartphone when I unboxed it. The device works fine otherwise but I wanted to report this for my records.",
    "The notification light on my phone blinks a different color than what's described in the manual. Everything else works perfectly, just curious if this is normal.",
    // Billing Inquiry - Critical
    "I'm seeing over $10,000 in unauthorized charges on my account for purchases I never made. My account has clearly been hacked. I need all charges frozen immediately!",
    // Billing Inquiry - High
    "I've been charged three times for the same purchase. My credit card shows three separate transactions. I need an immediate refund for the duplicate charges.",
    "I cancelled my subscription two months ago but I'm still being charged monthly. I have the cancellation confirmation email as proof. Refund all charges since cancellation.",
    // Billing Inquiry - Medium
    "I have a question about a small discrepancy on my latest invoice. The tax amount seems slightly higher than what I calculated. Could you please review?",
    "I'd like to update my payment method for my subscription but the website keeps showing an error. I've tried multiple cards and browsers.",
    // Billing Inquiry - Low
    "Could you tell me when my next billing cycle starts? I'm planning my budget for next month and want to know the exact date.",
    "Could you send me a duplicate copy of my receipt from last month? I need it for my expense report but seem to have misplaced the original email.",
    // Product Inquiry - High
    "My warranty expires tomorrow and I need to know if the issue I'm experiencing is covered before it's too late. Can someone please review my case urgently?",
    // Product Inquiry - Medium
    "I'm considering purchasing a new smartwatch and would like to know more about its specifications compared to the previous model.",
    "Could you tell me about the warranty coverage for the wireless headphones? I want to know what's covered before making my purchase decision.",
    // Product Inquiry - Low
    "Just curious about when the next generation of the laptop might be announced. I'm not in a hurry but want to make an informed decision.",
    "Is the router packaging made from recycled materials? I'm environmentally conscious and would like to know about your sustainability practices.",
    // Account Access - Critical
    "EMERGENCY: Our corporate admin account has been breached. The attacker has changed all admin credentials and is actively deleting employee accounts. Freeze our account NOW!",
    // Account Access - High
    "I can't login to my account. I've tried password reset but the verification emails aren't arriving. I have a deadline in 4 hours and need access urgently.",
    "Someone has changed my account password and recovery email. I can no longer access any of my services. I believe my account has been compromised.",
    // Account Access - Medium
    "I changed my phone number recently and now I can't receive verification codes. I'd like to update my phone number but the settings require the old number.",
    // Account Access - Low
    "I'd like to change my display name on my account. It currently shows my full name but I prefer just my first name. Where can I find this setting?",
    "How do I download all my data from my account? I'd like to keep a personal backup of my account information for my records.",
    // General Query - Medium
    "I need help tracking my shipment. The tracking number provided doesn't seem to work on the shipping carrier's website. My order was placed five days ago.",
    "I'm interested in your corporate discount program for bulk purchases. Our company is planning to outfit our new office and would like volume pricing.",
    // General Query - Low
    "Just writing to say how happy I am with my recent purchase. It has exceeded my expectations and I wanted to share my positive experience!",
    "I noticed a typo on your product page. The word 'specifications' is misspelled as 'specificatons'. Just thought I'd let you know.",
    "Do you have any upcoming product launch events? I'm a tech enthusiast and would love to attend."
];

/* ===== TOAST NOTIFICATION SYSTEM ===== */
function createToastContainer() {
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        document.body.appendChild(container);
    }
    return container;
}

function showToast(message, type = "info", duration = 4000) {
    const container = createToastContainer();

    const icons = {
        success: "✅",
        error: "❌",
        warning: "⚠️",
        info: "ℹ️"
    };

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-body">
            <span class="toast-icon">${icons[type] || icons.info}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="dismissToast(this.parentElement.parentElement)">&times;</button>
        </div>
        <div class="toast-progress"><div class="toast-progress-bar toast-progress-${type}"></div></div>
    `;

    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.add("toast-visible");
    });

    const progressBar = toast.querySelector(".toast-progress-bar");
    progressBar.style.transition = `width ${duration}ms linear`;
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            progressBar.style.width = "0%";
        });
    });

    const timer = setTimeout(() => dismissToast(toast), duration);
    toast._timer = timer;

    toast.addEventListener("mouseenter", () => {
        clearTimeout(toast._timer);
        progressBar.style.transitionDuration = "0s";
        progressBar.style.width = progressBar.getBoundingClientRect().width / toast.getBoundingClientRect().width * 100 + "%";
    });

    toast.addEventListener("mouseleave", () => {
        const remaining = parseFloat(progressBar.style.width) / 100 * duration;
        progressBar.style.transition = `width ${remaining}ms linear`;
        requestAnimationFrame(() => { progressBar.style.width = "0%"; });
        toast._timer = setTimeout(() => dismissToast(toast), remaining);
    });
}

function dismissToast(toast) {
    if (!toast || toast._dismissed) return;
    toast._dismissed = true;
    clearTimeout(toast._timer);
    toast.classList.add("toast-exit");
    toast.classList.remove("toast-visible");
    toast.addEventListener("animationend", () => toast.remove());
}

/* ===== INIT ===== */
document.addEventListener("DOMContentLoaded", function () {
    loadMetrics();
});

async function loadMetrics() {
    try {
        const res = await fetch("/api/metrics");
        const data = await res.json();
        populateMetrics(data);
    } catch (e) {
        console.error("Failed to load metrics:", e);
    }
}

function populateMetrics(data) {
    const cat = data.category;
    const pri = data.priority;

    document.getElementById("stat-accuracy").textContent = (cat.accuracy * 100).toFixed(1) + "%";
    document.getElementById("stat-priority-accuracy").textContent = (pri.accuracy * 100).toFixed(1) + "%";

    setMetric("cat-accuracy", cat.accuracy);
    setMetric("cat-precision", cat.precision);
    setMetric("cat-recall", cat.recall);
    setMetric("cat-f1", cat.f1_score);

    setMetric("pri-accuracy", pri.accuracy);
    setMetric("pri-precision", pri.precision);
    setMetric("pri-recall", pri.recall);
    setMetric("pri-f1", pri.f1_score);

    buildConfusionMatrix("cat-confusion-matrix", cat.confusion_matrix, cat.labels);
    buildConfusionMatrix("pri-confusion-matrix", pri.confusion_matrix, pri.labels);

    buildReportTable("cat-report-table", cat.classification_report, cat.labels);
    buildReportTable("pri-report-table", pri.classification_report, pri.labels);
}

function setMetric(prefix, value) {
    const pct = (value * 100).toFixed(1);
    document.getElementById(prefix).textContent = pct + "%";
    const bar = document.getElementById(prefix + "-bar");
    if (bar) setTimeout(() => { bar.style.width = pct + "%"; }, 200);
}

function buildConfusionMatrix(tableId, matrix, labels) {
    const table = document.getElementById(tableId);
    const thead = table.querySelector("thead tr");
    const tbody = table.querySelector("tbody");

    thead.innerHTML = '<th class="cm-corner">Actual \\ Predicted</th>';
    labels.forEach(l => {
        const th = document.createElement("th");
        th.textContent = l;
        thead.appendChild(th);
    });

    tbody.innerHTML = "";
    matrix.forEach((row, i) => {
        const tr = document.createElement("tr");
        const labelTd = document.createElement("td");
        labelTd.textContent = labels[i];
        labelTd.className = "cm-label";
        tr.appendChild(labelTd);

        row.forEach((val, j) => {
            const td = document.createElement("td");
            td.textContent = val;
            if (i === j) td.className = "cm-diagonal";
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

function buildReportTable(tableId, report, labels) {
    const tbody = document.querySelector("#" + tableId + " tbody");
    tbody.innerHTML = "";

    labels.forEach(label => {
        const r = report[label];
        if (!r) return;
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td style="font-weight:600;color:var(--text-primary)">${label}</td>
            <td>${(r.precision * 100).toFixed(1)}%</td>
            <td>${(r.recall * 100).toFixed(1)}%</td>
            <td>${(r["f1-score"] * 100).toFixed(1)}%</td>
            <td>${r.support}</td>
        `;
        tbody.appendChild(tr);
    });

    if (report["weighted avg"]) {
        const wa = report["weighted avg"];
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td style="font-weight:700;color:var(--orange)">Weighted Avg</td>
            <td style="font-weight:600">${(wa.precision * 100).toFixed(1)}%</td>
            <td style="font-weight:600">${(wa.recall * 100).toFixed(1)}%</td>
            <td style="font-weight:600">${(wa["f1-score"] * 100).toFixed(1)}%</td>
            <td style="font-weight:600">${wa.support}</td>
        `;
        tbody.appendChild(tr);
    }
}

async function classifyTicket() {
    const input = document.getElementById("ticket-input").value.trim();
    if (!input) { showToast("Please enter a ticket description.", "warning"); return; }

    const btn = document.getElementById("classify-btn");
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Classifying...';

    try {
        const res = await fetch("/api/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: input })
        });
        const data = await res.json();

        if (data.error) { showToast(data.error, "error"); return; }

        document.getElementById("result-placeholder").style.display = "none";
        document.getElementById("result-content").style.display = "block";
        document.getElementById("result-content").style.animation = "none";
        void document.getElementById("result-content").offsetHeight;
        document.getElementById("result-content").style.animation = "fadeIn 0.4s ease";

        document.getElementById("result-category-value").textContent = data.category;
        document.getElementById("result-category-desc").textContent = data.category_description;

        const priBadge = document.getElementById("result-priority-value");
        priBadge.textContent = data.priority;
        priBadge.className = "priority-badge priority-" + data.priority;

        document.getElementById("result-priority-desc").textContent = data.priority_description;
        document.getElementById("result-processed-text").textContent = data.processed_text;
    } catch (e) {
        showToast("Error classifying ticket. Is the server running?", "error");
        console.error(e);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-icon">🔍</span> Classify Ticket';
    }
}

function loadSampleTicket() {
    const idx = Math.floor(Math.random() * SAMPLE_TICKETS.length);
    document.getElementById("ticket-input").value = SAMPLE_TICKETS[idx];
}

function clearInput() {
    document.getElementById("ticket-input").value = "";
    document.getElementById("result-placeholder").style.display = "block";
    document.getElementById("result-content").style.display = "none";
}

async function loadSamplePredictions() {
    const tbody = document.getElementById("samples-tbody");
    tbody.innerHTML = '<tr><td colspan="6" class="empty-row"><span class="spinner"></span> Loading samples...</td></tr>';

    try {
        const res = await fetch("/api/sample-tickets");
        const samples = await res.json();

        const predictions = await Promise.all(samples.map(async (s) => {
            const predRes = await fetch("/api/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: (s["Ticket Subject"] || "") + " " + (s["Ticket Description"] || "") })
            });
            return { sample: s, prediction: await predRes.json() };
        }));

        tbody.innerHTML = "";
        predictions.forEach(({ sample, prediction }) => {
            const catMatch = sample["Ticket Type"] === prediction.category;
            const priMatch = sample["Ticket Priority"] === prediction.priority;
            const bothMatch = catMatch && priMatch;

            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td title="${sample['Ticket Description'] || ''}">${(sample["Ticket Description"] || "").substring(0, 80)}...</td>
                <td>${sample["Ticket Type"]}</td>
                <td style="font-weight:600">${prediction.category}</td>
                <td><span class="priority-badge priority-${sample['Ticket Priority']}">${sample["Ticket Priority"]}</span></td>
                <td><span class="priority-badge priority-${prediction.priority}">${prediction.priority}</span></td>
                <td class="${bothMatch ? 'match-yes' : 'match-no'}">${bothMatch ? '✓ Match' : '✗ Mismatch'}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-row">Error loading samples. Is the server running?</td></tr>';
        console.error(e);
    }
}
