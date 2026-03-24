"""
Animated HTML Visualization — self-contained browser playback

Generates a single HTML file with embedded simulation data that renders
an animated dashboard with playback controls, event markers, and
real-time metric gauges. Open it in any modern browser.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Optional


def generate_animation(history_df: pd.DataFrame, events_df: pd.DataFrame,
                       output_dir: str = "output",
                       title: str = "DSA Simulation") -> str:
    """Generate a self-contained animated HTML visualization.

    Returns the path to the saved HTML file.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Downsample history for performance (every 2nd tick if > 3000)
    df = history_df.copy()
    if len(df) > 3000:
        df = df.iloc[::2].reset_index(drop=True)

    # Convert data to JSON
    history_json = df.to_json(orient="records", double_precision=4)
    events_json = events_df.to_json(orient="records") if not events_df.empty else "[]"

    html = _build_html(history_json, events_json, title)
    path = str(out / "animation.html")
    Path(path).write_text(html)
    return path


def _build_html(history_json: str, events_json: str, title: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    background: #0a0a0f;
    color: #e0d8c8;
    font-family: 'Segoe UI', system-ui, sans-serif;
    overflow-x: hidden;
}}
#header {{
    text-align: center;
    padding: 18px 0 8px;
    background: linear-gradient(180deg, #1a1520 0%, #0a0a0f 100%);
    border-bottom: 1px solid #2a2535;
}}
#header h1 {{
    font-size: 1.4em;
    font-weight: 300;
    letter-spacing: 3px;
    color: #c8b888;
    text-transform: uppercase;
}}
#header .subtitle {{
    font-size: 0.75em;
    color: #888;
    margin-top: 2px;
}}
#era-banner {{
    text-align: center;
    padding: 6px;
    font-size: 1.1em;
    font-weight: 600;
    letter-spacing: 2px;
    color: #d4a844;
    min-height: 32px;
    text-transform: uppercase;
    text-shadow: 0 0 20px rgba(212, 168, 68, 0.3);
}}
#event-flash {{
    text-align: center;
    padding: 4px;
    font-size: 0.85em;
    color: #ff8844;
    min-height: 24px;
    opacity: 0;
    transition: opacity 0.3s;
}}
#event-flash.visible {{ opacity: 1; }}

/* Controls */
#controls {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 10px 20px;
    background: #111118;
}}
#controls button {{
    background: #222230;
    border: 1px solid #444;
    color: #c8b888;
    padding: 6px 16px;
    cursor: pointer;
    border-radius: 3px;
    font-size: 0.85em;
}}
#controls button:hover {{ background: #333340; }}
#controls button.active {{ background: #443820; border-color: #c8b888; }}
#timeline {{
    flex: 1;
    max-width: 600px;
    height: 6px;
    -webkit-appearance: none;
    appearance: none;
    background: #222;
    border-radius: 3px;
    outline: none;
    cursor: pointer;
}}
#timeline::-webkit-slider-thumb {{
    -webkit-appearance: none;
    width: 14px; height: 14px;
    background: #c8b888;
    border-radius: 50%;
    cursor: pointer;
}}
#tick-display {{
    font-size: 0.85em;
    color: #888;
    min-width: 100px;
    text-align: right;
    font-variant-numeric: tabular-nums;
}}
#speed-display {{
    font-size: 0.75em;
    color: #666;
    min-width: 40px;
}}

/* Dashboard grid */
#dashboard {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto;
    gap: 2px;
    padding: 2px;
    max-width: 1400px;
    margin: 0 auto;
}}
.panel {{
    background: #111118;
    border: 1px solid #1e1e28;
    padding: 10px 14px;
    position: relative;
}}
.panel-title {{
    font-size: 0.7em;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #666;
    margin-bottom: 8px;
}}
canvas {{
    width: 100%;
    height: 200px;
    display: block;
}}

/* Gauges row */
#gauges {{
    display: flex;
    justify-content: center;
    gap: 30px;
    padding: 12px 20px;
    background: #0d0d14;
    flex-wrap: wrap;
}}
.gauge {{
    text-align: center;
    min-width: 80px;
}}
.gauge-value {{
    font-size: 1.6em;
    font-weight: 200;
    font-variant-numeric: tabular-nums;
}}
.gauge-label {{
    font-size: 0.6em;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #666;
    margin-top: 2px;
}}

/* Event log */
#event-log {{
    max-width: 1400px;
    margin: 0 auto;
    padding: 8px 14px;
    background: #0d0d14;
    border-top: 1px solid #1e1e28;
    max-height: 120px;
    overflow-y: auto;
    font-size: 0.75em;
    font-family: monospace;
}}
.log-entry {{
    padding: 1px 0;
    color: #888;
}}
.log-entry .tick {{ color: #555; }}
.log-entry .etype {{ color: #c8b888; }}
</style>
</head>
<body>

<div id="header">
    <h1>{title}</h1>
    <div class="subtitle">Entropy-Driven Dynamics &mdash; Emergent Biblical Arc</div>
</div>
<div id="era-banner">Eden</div>
<div id="event-flash"></div>

<div id="controls">
    <button id="btn-play" class="active">&#9654; Play</button>
    <button id="btn-pause">&#10074;&#10074; Pause</button>
    <button id="btn-reset">&#8634; Reset</button>
    <input type="range" id="timeline" min="0" max="100" value="0">
    <div id="tick-display">Tick 0</div>
    <button id="btn-slower">-</button>
    <div id="speed-display">1x</div>
    <button id="btn-faster">+</button>
</div>

<div id="gauges">
    <div class="gauge">
        <div class="gauge-value" id="g-corruption" style="color:#9966cc">0.00</div>
        <div class="gauge-label">Corruption</div>
    </div>
    <div class="gauge">
        <div class="gauge-value" id="g-nearness" style="color:#d4a844">0.00</div>
        <div class="gauge-label">Divine Nearness</div>
    </div>
    <div class="gauge">
        <div class="gauge-value" id="g-covenant" style="color:#4488cc">0.00</div>
        <div class="gauge-label">Covenant</div>
    </div>
    <div class="gauge">
        <div class="gauge-value" id="g-presence" style="color:#d4a844">0.00</div>
        <div class="gauge-label">Presence</div>
    </div>
    <div class="gauge">
        <div class="gauge-value" id="g-remnant" style="color:#88aa44">0.00</div>
        <div class="gauge-label">Remnant</div>
    </div>
    <div class="gauge">
        <div class="gauge-value" id="g-alive" style="color:#aaa">0</div>
        <div class="gauge-label">Population</div>
    </div>
    <div class="gauge">
        <div class="gauge-value" id="g-temple" style="color:#d4a844">0.00</div>
        <div class="gauge-label">Temple</div>
    </div>
</div>

<div id="dashboard">
    <div class="panel">
        <div class="panel-title">SCC &mdash; Three-Realm Cosmology</div>
        <canvas id="c-scc"></canvas>
    </div>
    <div class="panel">
        <div class="panel-title">CDT &mdash; Covenant Distance</div>
        <canvas id="c-cdt"></canvas>
    </div>
    <div class="panel">
        <div class="panel-title">DSA &mdash; Divine Engagement</div>
        <canvas id="c-dsa"></canvas>
    </div>
    <div class="panel">
        <div class="panel-title">Population &mdash; Agents</div>
        <canvas id="c-pop"></canvas>
    </div>
</div>

<div id="event-log"></div>

<script>
// === DATA ===
const history = {history_json};
const events = {events_json};

// Pre-index events by tick
const eventsByTick = {{}};
events.forEach(e => {{
    const t = e.tick;
    if (!eventsByTick[t]) eventsByTick[t] = [];
    eventsByTick[t].push(e);
}});

// === STATE ===
let currentIndex = 0;
let playing = true;
let speed = 1;
const speeds = [0.25, 0.5, 1, 2, 4, 8, 16];
let speedIdx = 2;
let lastFrameTime = 0;
const baseInterval = 50; // ms per tick at 1x

// === ELEMENTS ===
const timeline = document.getElementById('timeline');
const tickDisplay = document.getElementById('tick-display');
const eraBanner = document.getElementById('era-banner');
const eventFlash = document.getElementById('event-flash');
const eventLog = document.getElementById('event-log');
const speedDisplay = document.getElementById('speed-display');

timeline.max = history.length - 1;

// === CANVAS SETUP ===
function setupCanvas(id) {{
    const canvas = document.getElementById(id);
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    return {{ canvas, ctx, w: rect.width, h: rect.height }};
}}

let panels;
function initPanels() {{
    panels = {{
        scc: setupCanvas('c-scc'),
        cdt: setupCanvas('c-cdt'),
        dsa: setupCanvas('c-dsa'),
        pop: setupCanvas('c-pop'),
    }};
}}

// === DRAWING ===
function drawChart(panel, series, endIdx) {{
    const {{ ctx, w, h }} = panel;
    ctx.clearRect(0, 0, w, h);

    const total = history.length;
    const padding = {{ left: 1, right: 1, top: 4, bottom: 4 }};
    const plotW = w - padding.left - padding.right;
    const plotH = h - padding.top - padding.bottom;

    // Grid lines
    ctx.strokeStyle = '#1a1a24';
    ctx.lineWidth = 0.5;
    for (let i = 0; i <= 4; i++) {{
        const y = padding.top + (plotH * i / 4);
        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(w - padding.right, y);
        ctx.stroke();
    }}

    // Draw playhead
    const playheadX = padding.left + (endIdx / Math.max(1, total - 1)) * plotW;
    ctx.strokeStyle = '#ffffff18';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(playheadX, padding.top);
    ctx.lineTo(playheadX, h - padding.bottom);
    ctx.stroke();

    // Mark events on this chart
    const eventTicks = Object.keys(eventsByTick).map(Number).filter(t => {{
        const idx = history.findIndex(h => h.tick >= t);
        return idx >= 0 && idx <= endIdx;
    }});
    ctx.strokeStyle = '#ffffff0a';
    ctx.lineWidth = 0.5;
    eventTicks.forEach(t => {{
        const idx = history.findIndex(h => h.tick >= t);
        const x = padding.left + (idx / Math.max(1, total - 1)) * plotW;
        ctx.beginPath();
        ctx.moveTo(x, padding.top);
        ctx.lineTo(x, h - padding.bottom);
        ctx.stroke();
    }});

    // Draw each series
    series.forEach(s => {{
        ctx.strokeStyle = s.color;
        ctx.lineWidth = s.width || 1.5;
        ctx.globalAlpha = s.alpha || 0.9;
        ctx.beginPath();

        // Draw full history faintly, then bright up to endIdx
        const step = Math.max(1, Math.floor(total / plotW));
        for (let i = 0; i < total; i += step) {{
            const x = padding.left + (i / Math.max(1, total - 1)) * plotW;
            const val = history[i][s.key];
            const y = padding.top + plotH * (1 - Math.min(1, Math.max(0, val || 0)));
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }}

        // Dim future part
        ctx.save();
        const grad = ctx.createLinearGradient(playheadX - 2, 0, playheadX + 20, 0);
        grad.addColorStop(0, s.color);
        grad.addColorStop(1, s.color + '15');

        ctx.stroke();
        ctx.restore();

        // Overdraw bright portion up to current
        ctx.globalAlpha = 1;
        ctx.beginPath();
        for (let i = 0; i <= endIdx; i += step) {{
            const x = padding.left + (i / Math.max(1, total - 1)) * plotW;
            const val = history[i][s.key];
            const y = padding.top + plotH * (1 - Math.min(1, Math.max(0, val || 0)));
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }}
        ctx.stroke();

        // Current value dot
        if (endIdx >= 0) {{
            const val = history[endIdx][s.key] || 0;
            const dotX = padding.left + (endIdx / Math.max(1, total - 1)) * plotW;
            const dotY = padding.top + plotH * (1 - Math.min(1, Math.max(0, val)));
            ctx.fillStyle = s.color;
            ctx.beginPath();
            ctx.arc(dotX, dotY, 3, 0, Math.PI * 2);
            ctx.fill();
        }}

        // Label
        if (s.label) {{
            const val = history[Math.min(endIdx, history.length - 1)][s.key] || 0;
            ctx.fillStyle = s.color;
            ctx.font = '10px system-ui';
            ctx.globalAlpha = 0.7;
            const dotY = padding.top + plotH * (1 - Math.min(1, Math.max(0, val)));
            ctx.fillText(s.label, playheadX + 6, dotY + 3);
            ctx.globalAlpha = 1;
        }}
    }});

    ctx.globalAlpha = 1;
}}

function renderFrame(idx) {{
    if (!panels) return;
    const row = history[idx];
    if (!row) return;

    // SCC
    drawChart(panels.scc, [
        {{ key: 'env_heavenly_influence', color: '#d4a844', label: 'Heavenly' }},
        {{ key: 'env_underworld_pressure', color: '#aa3333', label: 'Underworld' }},
        {{ key: 'env_natural_vitality', color: '#44aa44', label: 'Vitality' }},
        {{ key: 'env_corruption_level', color: '#9966cc', label: 'Corruption', width: 2 }},
    ], idx);

    // CDT
    drawChart(panels.cdt, [
        {{ key: 'cdt_active_distance', color: '#cc4444', label: 'Distance' }},
        {{ key: 'cdt_divine_nearness', color: '#d4a844', label: 'Nearness' }},
        {{ key: 'cdt_covenant_strength', color: '#4488cc', label: 'Covenant' }},
        {{ key: 'cdt_spiritual_vitality', color: '#44aa44', label: 'Vitality' }},
    ], idx);

    // DSA
    drawChart(panels.dsa, [
        {{ key: 'dsa_presence_level', color: '#d4a844', label: 'Presence', width: 2 }},
        {{ key: 'dsa_delight', color: '#88cc44', label: 'Delight' }},
        {{ key: 'dsa_grief', color: '#4466aa', label: 'Grief' }},
        {{ key: 'dsa_patience', color: '#cc8844', label: 'Patience' }},
        {{ key: 'dsa_compassion', color: '#cc4444', label: 'Compassion' }},
    ], idx);

    // Population
    drawChart(panels.pop, [
        {{ key: 'pop_population_faithfulness', color: '#4488cc', label: 'Faithful' }},
        {{ key: 'pop_population_rebellion', color: '#cc4444', label: 'Rebellion' }},
        {{ key: 'pop_remnant_fraction', color: '#d4a844', label: 'Remnant' }},
        {{ key: 'pop_avg_delusion', color: '#9966cc', label: 'Delusion' }},
    ], idx);

    // Gauges
    document.getElementById('g-corruption').textContent = (row.env_corruption_level || 0).toFixed(2);
    document.getElementById('g-nearness').textContent = (row.cdt_divine_nearness || 0).toFixed(2);
    document.getElementById('g-covenant').textContent = (row.cdt_covenant_strength || row.cdt_covenant_health || 0).toFixed(2);
    document.getElementById('g-presence').textContent = (row.dsa_presence_level || 0).toFixed(2);
    document.getElementById('g-remnant').textContent = (row.pop_remnant_fraction || 0).toFixed(2);
    document.getElementById('g-alive').textContent = row.pop_alive_count || 0;
    document.getElementById('g-temple').textContent = (row.temple_presence || 0).toFixed(2);

    // Tick display
    tickDisplay.textContent = `Tick ${{row.tick}}`;
    timeline.value = idx;

    // Era detection
    updateEra(row);

    // Events at this tick
    const tickEvents = eventsByTick[row.tick];
    if (tickEvents && tickEvents.length > 0) {{
        const latest = tickEvents[tickEvents.length - 1];
        eventFlash.textContent = latest.description || latest.type;
        eventFlash.classList.add('visible');
        setTimeout(() => eventFlash.classList.remove('visible'), 2000);

        tickEvents.forEach(e => {{
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.innerHTML = `<span class="tick">[Tick ${{e.tick}}]</span> <span class="etype">${{e.type}}</span> ${{e.description || ''}}`;
            eventLog.prepend(entry);
        }});
    }}
}}

function updateEra(row) {{
    let era = '';
    const tick = row.tick;
    const corruption = row.env_corruption_level || 0;
    const consummated = row.consummated;
    const graceActive = row.grace_period_active;
    const sojourn = row.sojourn_active;
    const templePresence = row.temple_presence || 0;
    const apostasy = row.apostasy_level || 0;

    if (consummated) {{
        era = 'New Creation';
        eraBanner.style.color = '#fff';
        eraBanner.style.textShadow = '0 0 30px rgba(255,255,255,0.5)';
    }} else if (apostasy > 0.3) {{
        era = 'Final Apostasy';
        eraBanner.style.color = '#cc3333';
        eraBanner.style.textShadow = '0 0 20px rgba(200,50,50,0.3)';
    }} else if (graceActive) {{
        era = 'Church Age — Grace Period';
        eraBanner.style.color = '#88aa44';
        eraBanner.style.textShadow = '0 0 20px rgba(136,170,68,0.3)';
    }} else if (templePresence > 0.3) {{
        era = 'Temple Period';
        eraBanner.style.color = '#d4a844';
        eraBanner.style.textShadow = '0 0 20px rgba(212,168,68,0.3)';
    }} else if (sojourn) {{
        era = 'Sojourn';
        eraBanner.style.color = '#aa8844';
        eraBanner.style.textShadow = '0 0 20px rgba(170,136,68,0.2)';
    }} else if (corruption < 0.05 && tick < 50) {{
        era = 'Eden';
        eraBanner.style.color = '#44cc44';
        eraBanner.style.textShadow = '0 0 20px rgba(68,204,68,0.3)';
    }} else if (corruption > 0.8 && tick < 400) {{
        era = 'Pre-Flood Wickedness';
        eraBanner.style.color = '#aa3333';
        eraBanner.style.textShadow = '0 0 20px rgba(170,50,50,0.3)';
    }} else {{
        era = 'Unfolding History';
        eraBanner.style.color = '#888';
        eraBanner.style.textShadow = 'none';
    }}
    eraBanner.textContent = era;
}}

// === CONTROLS ===
document.getElementById('btn-play').onclick = () => {{
    playing = true;
    document.getElementById('btn-play').classList.add('active');
    document.getElementById('btn-pause').classList.remove('active');
}};
document.getElementById('btn-pause').onclick = () => {{
    playing = false;
    document.getElementById('btn-pause').classList.add('active');
    document.getElementById('btn-play').classList.remove('active');
}};
document.getElementById('btn-reset').onclick = () => {{
    currentIndex = 0;
    eventLog.innerHTML = '';
    renderFrame(0);
}};
timeline.oninput = () => {{
    currentIndex = parseInt(timeline.value);
    renderFrame(currentIndex);
}};
document.getElementById('btn-faster').onclick = () => {{
    speedIdx = Math.min(speedIdx + 1, speeds.length - 1);
    speed = speeds[speedIdx];
    speedDisplay.textContent = speed + 'x';
}};
document.getElementById('btn-slower').onclick = () => {{
    speedIdx = Math.max(speedIdx - 1, 0);
    speed = speeds[speedIdx];
    speedDisplay.textContent = speed + 'x';
}};

// Keyboard
document.addEventListener('keydown', e => {{
    if (e.code === 'Space') {{ e.preventDefault(); playing = !playing;
        document.getElementById('btn-play').classList.toggle('active', playing);
        document.getElementById('btn-pause').classList.toggle('active', !playing);
    }}
    if (e.code === 'ArrowRight') {{ currentIndex = Math.min(currentIndex + 10, history.length - 1); renderFrame(currentIndex); }}
    if (e.code === 'ArrowLeft') {{ currentIndex = Math.max(currentIndex - 10, 0); renderFrame(currentIndex); }}
}});

// === ANIMATION LOOP ===
function animate(timestamp) {{
    if (!lastFrameTime) lastFrameTime = timestamp;
    const elapsed = timestamp - lastFrameTime;
    const interval = baseInterval / speed;

    if (playing && elapsed >= interval) {{
        lastFrameTime = timestamp;
        if (currentIndex < history.length - 1) {{
            currentIndex++;
            renderFrame(currentIndex);
        }} else {{
            playing = false;
            document.getElementById('btn-pause').classList.add('active');
            document.getElementById('btn-play').classList.remove('active');
        }}
    }}
    requestAnimationFrame(animate);
}}

// === INIT ===
window.addEventListener('load', () => {{
    initPanels();
    renderFrame(0);
    requestAnimationFrame(animate);
}});
window.addEventListener('resize', () => {{
    initPanels();
    renderFrame(currentIndex);
}});
</script>
</body>
</html>"""
