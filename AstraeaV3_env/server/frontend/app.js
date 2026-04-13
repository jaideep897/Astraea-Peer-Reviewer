/**
 * ASTRAEA V3 | Strategic Research Auditor OS
 * Cinematic High-Logic Controller
 */

const BASE_URL = window.location.origin;

// Core State
let currentSession = null;
let currentPaper = null;
let isProcessing = false;

// Hackathon Merit Engine
const MeritAnalytics = {
    history: [0],
    maxData: 20,
    alignment: 0,
    
    push(reward, total = null) {
        this.history.push(reward);
        if (this.history.length > this.maxData) this.history.shift();
        
        if (total !== null) {
            this.alignment = total * 100;
        } else {
            this.alignment = Math.max(0, Math.min(100, (this.alignment + reward * 100)));
        }
        renderMeritChart();
    }
};

// DOM Linkage
const UI = {
    title: document.getElementById('paperTitle'),
    tabs: document.getElementById('sectionTabs'),
    content: document.getElementById('sectionContent'),
    rewardVal: document.getElementById('rewardValue'),
    rewardCircle: document.getElementById('rewardCircle'),
    feedback: document.getElementById('scientificFeedback'),
    log: document.getElementById('logPanel'),
    step: document.getElementById('stepCounter'),
    delta: document.getElementById('lastActionReward'),
    shell: document.getElementById('appShell'),
    siiVal: document.getElementById('siiValue'),
    siiCircle: document.getElementById('siiIndicator'),
    threads: document.getElementById('neuralThreads'),
    xpVal: document.getElementById('expertLevel'),
    xpBar: document.getElementById('xpBar')
};

// --- Crystalline Acoustic Orchestrator ---
// --- Crystalline Acoustic Orchestrator (FM Synthesis Edition v2) ---
class AcousticEngine {
    constructor() {
        this.ctx = null;
        this.masterGain = null;
    }

    init() {
        if (!this.ctx) {
            this.ctx = new (window.AudioContext || window.webkitAudioContext)();
            this.masterGain = this.ctx.createGain();
            this.masterGain.gain.setValueAtTime(0.6, this.ctx.currentTime);
            this.masterGain.connect(this.ctx.destination);
        }
    }

    play(type) {
        if (!this.ctx) return;
        const now = this.ctx.currentTime;

        if (type === 'tic') {
            // Glassy Harmonic Tic (2 Oscillator FM)
            const carrier = this.ctx.createOscillator();
            const modulator = this.ctx.createOscillator();
            const modGain = this.ctx.createGain();
            const g = this.ctx.createGain();

            carrier.type = 'sine';
            modulator.type = 'sine';
            
            carrier.frequency.setValueAtTime(1200, now);
            modulator.frequency.setValueAtTime(2400, now);
            modGain.gain.setValueAtTime(500, now);

            modulator.connect(modGain);
            modGain.connect(carrier.frequency);
            carrier.connect(g);
            g.connect(this.masterGain);

            g.gain.setValueAtTime(0.4, now);
            g.gain.exponentialRampToValueAtTime(0.001, now + 0.1);
            
            carrier.start();
            modulator.start();
            carrier.stop(now + 0.1);
            modulator.stop(now + 0.1);

        } else if (type === 'scan') {
            // Resonant Neural Bowl (Subtractive)
            const osc = this.ctx.createOscillator();
            const filter = this.ctx.createBiquadFilter();
            const g = this.ctx.createGain();

            osc.type = 'triangle';
            osc.frequency.setValueAtTime(110, now);
            osc.frequency.exponentialRampToValueAtTime(55, now + 1.5);

            filter.type = 'lowpass';
            filter.frequency.setValueAtTime(2000, now);
            filter.frequency.exponentialRampToValueAtTime(100, now + 1.5);
            filter.Q.setValueAtTime(15, now);

            osc.connect(filter);
            filter.connect(g);
            g.connect(this.masterGain);

            g.gain.setValueAtTime(0.3, now);
            g.gain.exponentialRampToValueAtTime(0.001, now + 1.5);

            osc.start();
            osc.stop(now + 1.5);

        } else if (type === 'chime') {
            // Zen Chime (Multi-harmonic Additive)
            const freqs = [432, 864, 1296]; // Pure harmonics
            freqs.forEach((f, i) => {
                const osc = this.ctx.createOscillator();
                const g = this.ctx.createGain();
                osc.frequency.setValueAtTime(f, now);
                osc.connect(g);
                g.connect(this.masterGain);
                g.gain.setValueAtTime(0.2 / (i + 1), now);
                g.gain.exponentialRampToValueAtTime(0.001, now + 2.0);
                osc.start();
                osc.stop(now + 2.0);
            });
        }
    }
}

const Audio = new AcousticEngine();

// --- OS Initialization ---
window.addEventListener('load', () => {
    initCustomSelects();
    attachHaptics();
    
    // Entrance Sequence
    gsap.to(UI.shell, { opacity: 1, duration: 2, ease: "power4.out" });
    gsap.from(".os-panel", { 
        y: 60, 
        opacity: 0, 
        stagger: 0.2, 
        duration: 1.5, 
        ease: "expo.out",
        delay: 0.5
    });
    
    resetEnv();
    updateSII({ step_count: 0 }); 
});

function attachHaptics() {
    document.body.addEventListener('mousedown', () => Audio.init(), { once: true });
    
    document.querySelectorAll('.os-btn, .opt, .trigger, .v3-tab').forEach(el => {
        el.addEventListener('click', () => Audio.play('tic'));
    });
}

// --- Custom Select Controller ---
function initCustomSelects() {
    document.querySelectorAll('.os-select-wrap').forEach(wrap => {
        const trigger = wrap.querySelector('.trigger');
        const options = wrap.querySelector('.options');
        const input = wrap.querySelector('input');

        trigger.addEventListener('click', (e) => {
            options.classList.toggle('show');
            e.stopPropagation();
        });

        wrap.querySelectorAll('.opt').forEach(opt => {
            opt.addEventListener('click', () => {
                trigger.querySelector('.curr').textContent = opt.textContent;
                input.value = opt.dataset.val;
                
                wrap.querySelectorAll('.opt').forEach(o => o.classList.remove('active'));
                opt.classList.add('active');
                options.classList.remove('show');
                
                if (input.id === 'taskSelect') resetEnv();
            });
        });
    });

    document.addEventListener('click', () => {
        document.querySelectorAll('.options').forEach(o => o.classList.remove('show'));
    });
}

// --- Core Logic ---

async function resetEnv() {
    if (isProcessing) return;
    isProcessing = true;
    
    const task = document.getElementById('taskSelect').value;
    addLog(`ENV_START [${task}]`, "system");

    try {
        const resp = await fetch(`${BASE_URL}/reset`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_id: task })
        });
        
        const data = await resp.json();
        currentSession = data.session_id;
        currentPaper = data.observation;
        
        // Reset Merit History for new session
        MeritAnalytics.history = [0];
        MeritAnalytics.alignment = 0;
        renderMeritChart();
        
        renderPaper();
        updateUI(data.observation, 0, "Neural Handshake Success. Node Stable.");
        
        Audio.play('chime');
        Audio.play('startup');
        addLog("ASTRAEA_ONLINE | NODE_SYNC_SUCCESS", "system");
        
        // Clear tactical inputs on reset
        document.getElementById('concernLocation').value = '';
        document.getElementById('concernDesc').value = '';
        document.getElementById('scoreVal').value = '';
        
    } catch (e) {
        addLog("NODE_OFFLINE | RETRYING_SYNC...", "error");
    } finally {
        isProcessing = false;
    }
}

async function handleAction(type) {
    if (!currentSession || isProcessing) return;
    isProcessing = true;

    const action = { action_type: type };
    if (type === 'flag_concern') {
        action.concern_type = document.getElementById('concernType').value;
        action.concern_location = document.getElementById('concernLocation').value;
        action.concern_description = document.getElementById('concernDesc').value;
    } else if (type === 'assign_score') {
        action.dimension = document.getElementById('scoreDimension').value;
        action.score = parseFloat(document.getElementById('scoreVal').value);
    } else if (type === 'submit_decision') {
        const decisionVal = document.getElementById('decisionVal').value;
        action.decision = decisionVal;
    }

    setButtonState(type, 'loading');

    try {
        // --- HARDENED VALIDATION (INSIDE TRY) ---
        if (type === 'assign_score') {
            const score = document.getElementById('scoreVal').value;
            if (score === "") {
                UI.feedback.innerHTML = `<span class="feedback-error">>>> CRITICAL: SCORE_METRIC_REQUIRED <<<</span>`;
                addLog("VALIDATION_ERROR: SCORE_METRIC_REQUIRED", "error");
                isProcessing = false;
                setButtonState(type, 'default');
                return;
            }
        }
        // ---------------------------

        const resp = await fetch(`${BASE_URL}/step`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSession, action })
        });

        if (!resp.ok) {
            const errData = await resp.json().catch(() => ({}));
            throw new Error(errData.detail || `HTTP_${resp.status}`);
        }

        const data = await resp.json();
        const reward = data.reward.total;
        const total = data.observation.total_reward;
        
        MeritAnalytics.push(reward, total);
        updateUI(data.observation, reward, data.reward.feedback);
        
        if (reward > 0) {
            setButtonState(type, 'success');
            triggerPulse('success');
            Audio.play('chime');
        } else if (reward < 0) {
            setButtonState(type, 'error');
            triggerGlitch();
        } else {
            setButtonState(type, 'default');
        }

        const logType = reward > 0 ? "success" : (reward < 0 ? "error" : "system");
        addLog(`${type.toUpperCase()} | MERIT: ${reward.toFixed(2)}`, logType);
        
        if (type === 'submit_decision') {
            addLog("PROTOCOL_TERMINATED: Audit Cycle Complete.", "success");
        }

        if (data.done) {
            document.getElementById('graderBtn').style.display = 'block';
            addLog("SYNC_COMPLETE: Awaiting Final Grade.", "system");
        }
    } catch (e) {
        console.error("Neural Error:", e);
        
        let errorMsg = "REASON: NEURAL_LATENCY / CONCURRENCY_LOCK | SOLUTION: PRESS 'RESET ENV' TO RE-STABILIZE";
        if (e.message.includes("VALIDATION_ERROR")) {
            errorMsg = e.message;
        } else if (e.message.includes("404") || e.message.includes("not found")) {
            errorMsg = "REASON: SESSION_EXPIRED | SOLUTION: RE-INITIALIZING TASK...";
            setTimeout(() => resetEnv(), 1500); 
        } else if (e.message.includes("500") || e.message.includes("Internal")) {
            errorMsg = "REASON: SYNAPTIC_FAULT | SOLUTION: PRESS 'RESET ENV'";
        } else if (window.navigator.onLine === false) {
            errorMsg = "REASON: OFFLINE_MODE | SOLUTION: CHECK_NETWORK_STABILITY";
        }
        
        addLog(errorMsg, "error");
        UI.feedback.innerHTML = `<span class="feedback-error">${errorMsg}</span>`;
        setButtonState(type, 'default');
    } finally {
        isProcessing = false;
    }
}

async function requestHint() {
    if (!currentSession || isProcessing) return;
    isProcessing = true;
    
    Audio.play('scan');
    const orb = document.getElementById('hintBtn');
    orb.classList.add('scan-active');
    addLog("NEURAL_SCAN_IN_PROGRESS...", "system");

    console.log("Deep Scan: Initiating for session", currentSession);

    try {
        const url = `${BASE_URL}/hint?session_id=${currentSession}`;
        console.log("Deep Scan: Fetching from", url);
        const resp = await fetch(url);
        if (!resp.ok) throw new Error(`HTTP Error: ${resp.status}`);
        
        const data = await resp.json();
        console.log("Deep Scan: Received data", data);
        if (data.detail) throw new Error(data.detail);
        if (!data.hint) throw new Error("Invalid hint packet received.");

        // --- Spectral Auditor Enhancement ---
        if (data.location && currentPaper) {
            console.log("Deep Scan: Mapping discrepancy to", data.location);
            const sections = Object.keys(currentPaper.sections);
            const other = sections.filter(s => s !== data.location.toLowerCase())[Math.floor(Math.random() * (sections.length - 1))];
            
            if (other) {
                console.log("Deep Scan: Drawing thread to", other);
                drawNeuralThread(data.location.toLowerCase(), other);
            }
            highlightLogicGap(data.description);
        }

        // Intensified Neural Pulse Sequence
        gsap.to(orb, { 
            scale: 1.3, 
            duration: 0.2, 
            repeat: 5, 
            yoyo: true, 
            ease: "sine.inOut",
            onComplete: () => gsap.to(orb, { scale: 1, duration: 0.5 }) 
        });
        
        UI.feedback.innerHTML = `<div class="hint-pulse">NEURAL_DECRYPTION_SUCCESS</div>`;
        addLog(`SCAN_RESULT: DISCREPANCY in ${data.location ? data.location.toUpperCase() : 'UNKNOWN'}`, "success");
        
        // --- Trigger Cinematic Report Modal ---
        modal.show(data);
    } catch (e) {
        console.error("Deep Scan Critical Error:", e);
        let errorMsg = `SCAN_HARDWARE_FAULT: ${e.message}`;
        if (e.message.includes("404")) errorMsg = "SCAN_FAULT | SESSION_TIMEOUT";
        
        addLog(errorMsg, "error");
        UI.feedback.innerHTML = `<span class="feedback-error">${errorMsg}</span>`;
    } finally {
        isProcessing = false;
        setTimeout(() => orb.classList.remove('scan-active'), 1500);
    }
}

async function requestGrade() {
    if (!currentSession || isProcessing) return;
    isProcessing = true;
    
    try {
        const resp = await fetch(`${BASE_URL}/grader`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSession })
        });
        const data = await resp.json();
        
        Audio.play('chime');
        addLog(`GRADE_PROTO: ACCURACY ${(data.score * 100).toFixed(1)}%`, "success");
        
        // Show rich scientific report
        UI.feedback.innerHTML = `
            <div class="grade-report">
                <div class="report-header">FINAL_AUDIT_REPORT</div>
                <div class="report-body">${data.feedback}</div>
                <div class="report-id">REPT_ID: ${Math.random().toString(36).substr(2, 9).toUpperCase()}</div>
            </div>
        `;
    } catch (e) {
        addLog("GRADER_NODE_OFFLINE", "error");
    } finally {
        isProcessing = false;
    }
}

// --- Renderers ---

function updateUI(obs, lastReward, feedback) {
    const total = obs.total_reward || 0;
    
    // Stats
    UI.rewardVal.textContent = total.toFixed(2); // Updated to 2 digits
    UI.rewardCircle.setAttribute('stroke-dasharray', `${Math.min(100, total * 100)}, 100`);
    
    UI.delta.textContent = lastReward.toFixed(2); // Updated to 2 digits
    UI.delta.style.color = "var(--c-success)";
    gsap.from(UI.delta, { scale: 2, opacity: 0, duration: 0.8 });
    
    UI.step.textContent = `${obs.step_count}/${obs.max_steps}`;
    document.getElementById('alignmentVal').textContent = `ALIGNMENT: ${MeritAnalytics.alignment.toFixed(0)}%`;
    
    updateAura(total);
    updateSII(obs, lastReward);
    updateXP(obs);
    
    if (feedback) {
        UI.feedback.classList.remove('feedback-error', 'feedback-hallucination');
        
        if (feedback.includes("Hallucination Alert")) {
            UI.feedback.innerHTML = `<div class="feedback-hallucination">${feedback}</div>`;
            Audio.play('tic');
        } else {
            UI.feedback.textContent = feedback;
        }
        
        gsap.from(UI.feedback, { opacity: 0, x: -30, duration: 0.6 });
    }
}

function updateSII(obs, lastReward = 0) {
    // SCIENTIFIC_INTEGRITY now rewards quality audits.
    // Logic: Base 100. Slight decay per step, but significant boost for positive rewards.
    const stepPenalty = obs.step_count * 1.5;
    const meritBonus = (obs.total_reward || 0) * 40;
    
    let currentSII = Math.max(15, Math.min(100, 100 - stepPenalty + meritBonus));
    
    // Smooth transition for the value
    UI.siiVal.textContent = currentSII.toFixed(0);
    UI.siiCircle.setAttribute('stroke-dasharray', `${currentSII}, 100`);
    
    const container = document.querySelector('.sii-gauge-container');
    if (currentSII < 60) {
        container.classList.add('sii-unstable');
        if (lastReward <= 0) triggerGlitch(); // Visual warning for low integrity
    } else {
        container.classList.remove('sii-unstable');
    }
}

function updateXP(obs) {
    const level = obs.expert_level || 1;
    const currentXp = obs.neural_xp || 0;
    
    // Level progress calculation: (XP - CurrentLevelStart) / (NextLevelStart - CurrentLevelStart)
    // Formula from environment.py: new_level = 1 + floor(sqrt(XP/5))
    // Therefore XP for level L: 5 * (L-1)^2
    const currentLevelXp = 5 * Math.pow(level - 1, 2);
    const nextLevelXp = 5 * Math.pow(level, 2);
    const progress = ((currentXp - currentLevelXp) / (nextLevelXp - currentLevelXp)) * 100;

    const oldLevel = parseInt(UI.xpVal.textContent);
    UI.xpVal.textContent = level;
    
    // Smooth XP Bar Transition
    gsap.to(UI.xpBar, { 
        width: `${Math.min(100, Math.max(5, progress))}%`, 
        duration: 0.8, 
        ease: "power2.out" 
    });
    
    if (level > oldLevel && !isNaN(oldLevel)) {
        addLog(`NEURAL MILESTONE: Reached EXPERT_LEVEL_${level}`, "success");
        UI.xpVal.classList.add('level-up-pulse');
        Audio.play('chime'); // Use chime for level up
        setTimeout(() => UI.xpVal.classList.remove('level-up-pulse'), 1000);
    }
}

function drawNeuralThread(fromKey, toKey) {
    const tabs = Array.from(document.querySelectorAll('.v3-tab'));
    const t1 = tabs.find(t => t.textContent.toLowerCase() === fromKey);
    const t2 = tabs.find(t => t.textContent.toLowerCase() === toKey);
    
    if (!t1 || !t2) return;

    const r1 = t1.getBoundingClientRect();
    const r2 = t2.getBoundingClientRect();

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("class", "neural-thread");
    path.setAttribute("pathLength", "1");
    
    const startX = r1.left + r1.width / 2;
    const startY = r1.top + r1.height / 2;
    const endX = r2.left + r2.width / 2;
    const endY = r2.top + r2.height / 2;

    const cp1y = startY - 100;
    const cp2y = endY - 100;

    path.setAttribute("d", `M ${startX} ${startY} C ${startX} ${cp1y}, ${endX} ${cp2y}, ${endX} ${endY}`);
    UI.threads.appendChild(path);

    // Native Stroke Animation (Replaces drawSVG)
    gsap.fromTo(path, 
        { strokeDasharray: 1, strokeDashoffset: 1, opacity: 0 }, 
        { strokeDashoffset: 0, opacity: 0.6, duration: 1.2, ease: "power2.out" }
    );
    
    setTimeout(() => {
        gsap.to(path, { opacity: 0, duration: 1, onComplete: () => path.remove() });
    }, 4000);
}

function highlightLogicGap(desc) {
    const content = UI.content.textContent;
    // Simple mock: highlight a random sentence that 'sounds' technical
    const sentences = content.split('.');
    const randomIdx = Math.floor(Math.random() * (sentences.length - 1));
    const target = sentences[randomIdx];
    
    UI.content.innerHTML = content.replace(target, `<span class="logic-gap-glow">${target}</span>`);
    setTimeout(() => {
        UI.content.innerHTML = content;
    }, 5000);
}

function renderMeritChart() {
    const path = document.getElementById('chartPath');
    const area = document.getElementById('chartArea');
    if (!path) return;

    const data = MeritAnalytics.history;
    const width = 300;
    const height = 100;
    const step = width / (MeritAnalytics.maxData - 1);
    
    let points = "";
    let areaPoints = `0,${height} `;
    
    data.forEach((val, i) => {
        const x = i * step;
        const y = height - (Math.min(1, Math.max(0, val * 5 + 0.5)) * height);
        points += `${x},${y} `;
        areaPoints += `${x},${y} `;
    });
    
    areaPoints += `${(data.length - 1) * step},${height}`;
    
    path.setAttribute('d', `M ${points}`);
    area.setAttribute('d', `M ${areaPoints} Z`);
    
    // Native Stroke Animation (Replaces drawSVG)
    path.setAttribute('pathLength', '1');
    gsap.fromTo(path, { strokeDasharray: 1, strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 0.8, ease: "power1.inOut" });
}

function updateAura(total) {
    const body = document.body;
    body.classList.remove('os-aura-success', 'os-aura-error');
    
    if (total > 0.8) body.classList.add('os-aura-success');
    else if (total < 0.2 && total > 0.05) body.classList.add('os-aura-error');
}

function triggerPulse(type) {
    const aura = type === 'success' ? 'var(--c-success)' : 'var(--c-accent)';
    gsap.to('.p1', { boxShadow: `0 0 100px ${aura}`, duration: 0.3, yoyo: true, repeat: 1 });
}

function triggerGlitch() {
    document.body.classList.add('glitch-active');
    Audio.play('tic'); // Rapid tics for glitch
    setTimeout(() => document.body.classList.remove('glitch-active'), 500);
}

function setButtonState(type, state) {
    let btnId = '';
    if (type === 'flag_concern') btnId = 'flagBtn';
    else if (type === 'assign_score') btnId = 'scoreBtn';
    else if (type === 'submit_decision') btnId = 'submitBtn';
    
    const btn = document.getElementById(btnId);
    if (!btn) return;

    if (state === 'loading') {
        btn.dataset.originalText = btn.textContent;
        btn.textContent = 'EXECUTING...';
        btn.classList.add('loading-pulse');
        btn.disabled = true;
        btn.style.opacity = '0.5';
    } else if (state === 'success') {
        btn.textContent = 'SUCCESS';
        btn.classList.remove('loading-pulse');
        btn.classList.add('btn-success-glow');
        btn.disabled = false;
        btn.style.opacity = '1';
        setTimeout(() => {
            btn.textContent = btn.dataset.originalText;
            btn.classList.remove('btn-success-glow');
        }, 2000);
    } else {
        btn.textContent = btn.dataset.originalText;
        btn.classList.remove('loading-pulse');
        btn.disabled = false;
        btn.style.opacity = '1';
    }
}

function renderSection(key) {
    UI.content.textContent = currentPaper.sections[key];
    gsap.from(UI.content, { opacity: 0, scale: 0.98, duration: 0.5 });
}

function updateTabs(key) {
    document.querySelectorAll('.v3-tab').forEach(t => {
        if (t.textContent === key.toUpperCase()) t.classList.add('active');
        else t.classList.remove('active');
    });
}

function renderPaper() {
    if (!currentPaper) return;
    UI.title.textContent = currentPaper.paper_title || "SCIENTIFIC_AUDIT_NODE";
    UI.tabs.innerHTML = '';
    
    Object.keys(currentPaper.sections).forEach((key, i) => {
        const t = document.createElement('div');
        t.className = `v3-tab ${i === 0 ? 'active' : ''}`;
        t.textContent = key.toUpperCase();
        t.onclick = () => {
            Audio.play('tic');
            renderSection(key);
            updateTabs(key);
        };
        UI.tabs.appendChild(t);
    });
    
    renderSection(Object.keys(currentPaper.sections)[0]);
}

function addLog(msg, type = "") {
    const time = new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const div = document.createElement('div');
    
    let badge = "SYS";
    if (type === "success") badge = "DONE";
    if (type === "error") badge = "FAIL";
    if (type === "system") badge = "BOOT";
    
    div.className = `log-entry ${type}`;
    div.innerHTML = `
        <span class="log-time">[${time}]</span>
        <span class="log-badge">${badge}</span>
        <span class="log-msg">${msg}</span>
    `;
    
    UI.log.appendChild(div);
    UI.log.scrollTop = UI.log.scrollHeight;
    gsap.from(div, { opacity: 0, x: -15, duration: 0.4, ease: "power2.out" });
}

// Wire-up buttons
document.getElementById('resetBtn').addEventListener('click', resetEnv);
document.getElementById('flagBtn').addEventListener('click', () => handleAction('flag_concern'));
document.getElementById('scoreBtn').addEventListener('click', () => handleAction('assign_score'));
document.getElementById('submitBtn').addEventListener('click', () => handleAction('submit_decision'));
document.getElementById('graderBtn').addEventListener('click', requestGrade);
document.getElementById('hintBtn').addEventListener('click', requestHint);

// --- Modal Handling ---
const modal = {
    report: document.getElementById('scanReportModal'),
    closeBtn: document.getElementById('closeReportBtn'),
    shell: document.querySelector('.os-grid'),
    
    show(data) {
        const now = new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const severity = Math.floor((data.severity || 0.5) * 100);
        const confidence = (90 + Math.random() * 8).toFixed(1);
        
        document.getElementById('reportType').textContent = (data.type || "UNKNOWN_ANOMALY").toUpperCase();
        document.getElementById('reportLocation').textContent = (data.location || "UNTRACKED").toUpperCase();
        document.getElementById('reportDescription').textContent = data.description || "Experimental anomaly detected in neural stream.";
        document.getElementById('reportProtocolId').textContent = `PID_${Math.floor(Math.random()*9000)+1000}_ALPHA`;
        document.getElementById('reportTime').textContent = now;
        
        // Severity UI
        const sevBar = document.getElementById('reportSeverityBar');
        const sevVal = document.getElementById('reportSeverityVal');
        sevBar.style.width = `${severity}%`;
        sevVal.textContent = `${severity}%`;
        
        // Dynamic Recommendation
        const actionEl = document.getElementById('reportAction');
        const type = data.type || '';
        if (type.includes('leakage') || type.includes('reproducibility')) {
            actionEl.textContent = "CRITICAL: FLAG_CONCERN + REJECT_PROTOCOL";
            actionEl.style.color = "#ef4444";
            actionEl.style.borderColor = "#ef4444";
        } else {
            actionEl.textContent = "ADVISORY: FLAG_CONCERN + MAJOR_REVISION";
            actionEl.style.color = "#4ade80";
            actionEl.style.borderColor = "#4ade80";
        }
        
        document.getElementById('reportConfidence').textContent = `${confidence}%`;
        
        this.shell.classList.add('os-blurred');
        this.report.classList.add('show');
    },
    
    hide() {
        this.report.classList.remove('show');
        this.shell.classList.remove('os-blurred');
    }
};

if (modal.closeBtn) {
    modal.closeBtn.onclick = () => modal.hide();
}
