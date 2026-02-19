import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(page_title="Effort vs Impact Matrix", layout="wide")

st.title("📊 Effort vs Impact Matrix")
st.caption("Add initiatives below, then drag them onto the grid to prioritize.")

# Session state for initiatives
if "initiatives" not in st.session_state:
    st.session_state.initiatives = []

# Input row
col1, col2 = st.columns([4, 1])
with col1:
    new_initiative = st.text_input(
        "Add an initiative, project, or task:",
        placeholder="e.g. Launch new onboarding flow",
        label_visibility="collapsed",
        key="new_initiative_input"
    )
with col2:
    add_clicked = st.button("➕ Add", use_container_width=True)

if add_clicked and new_initiative.strip():
    st.session_state.initiatives.append({
        "id": f"item_{len(st.session_state.initiatives)}_{new_initiative[:10].replace(' ', '_')}",
        "label": new_initiative.strip(),
        # Default position: center of grid (x=50, y=50 as %)
        "x": 50,
        "y": 50,
        "placed": False
    })
    st.rerun()

# Pass initiatives to JS
initiatives_json = json.dumps(st.session_state.initiatives)

html_code = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: 'DM Sans', sans-serif;
    background: #f8f7f4;
    padding: 16px;
    min-height: 100vh;
  }}

  .layout {{
    display: flex;
    gap: 20px;
    align-items: flex-start;
  }}

  /* GRID SECTION */
  .grid-section {{
    flex: 1;
    min-width: 0;
  }}

  .axis-label-top {{
    text-align: center;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #1a1a2e;
    margin-bottom: 4px;
  }}

  .grid-row {{
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  .axis-label-side {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #1a1a2e;
    writing-mode: vertical-rl;
    transform: rotate(180deg);
    white-space: nowrap;
    width: 20px;
  }}

  .axis-label-side.right {{
    transform: rotate(0deg);
  }}

  #matrix {{
    position: relative;
    width: 100%;
    aspect-ratio: 1;
    border: 2px solid #1a1a2e;
    cursor: crosshair;
    overflow: hidden;
  }}

  .quadrant {{
    position: absolute;
    width: 50%;
    height: 50%;
    display: flex;
    align-items: flex-end;
    justify-content: flex-start;
    padding: 10px 12px;
  }}

  .quadrant-label {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    opacity: 0.85;
    line-height: 1.3;
  }}

  /* Quadrants: top-left = high impact low effort = Quick Wins */
  .q-quick    {{ top: 0; left: 0;    background: #c8e6c9; }}
  .q-major    {{ top: 0; right: 0;   background: #bbdefb; }}
  .q-fillin   {{ bottom: 0; left: 0; background: #e3f2fd; }}
  .q-money    {{ bottom: 0; right: 0; background: #ffe0b2; }}

  .q-quick .quadrant-label   {{ color: #1b5e20; }}
  .q-major .quadrant-label   {{ color: #0d47a1; }}
  .q-fillin .quadrant-label  {{ color: #1565c0; }}
  .q-money .quadrant-label   {{ color: #e65100; }}

  /* Dividers */
  .divider-h {{
    position: absolute;
    top: 50%;
    left: 0;
    width: 100%;
    height: 2px;
    background: #1a1a2e;
    z-index: 2;
  }}
  .divider-v {{
    position: absolute;
    left: 50%;
    top: 0;
    width: 2px;
    height: 100%;
    background: #1a1a2e;
    z-index: 2;
  }}

  /* DOT */
  .dot {{
    position: absolute;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #1a1a2e;
    border: 2px solid white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    cursor: grab;
    z-index: 10;
    transform: translate(-50%, -50%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    color: white;
    transition: box-shadow 0.15s, transform 0.1s;
    user-select: none;
  }}

  .dot:hover {{
    box-shadow: 0 4px 16px rgba(0,0,0,0.35);
    transform: translate(-50%, -50%) scale(1.1);
  }}

  .dot.dragging {{
    cursor: grabbing;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    transform: translate(-50%, -50%) scale(1.15);
    z-index: 100;
  }}

  .dot-tooltip {{
    position: absolute;
    bottom: calc(100% + 8px);
    left: 50%;
    transform: translateX(-50%);
    background: #1a1a2e;
    color: white;
    font-size: 11px;
    font-weight: 500;
    padding: 4px 8px;
    border-radius: 4px;
    white-space: nowrap;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.15s;
    z-index: 200;
    font-family: 'DM Sans', sans-serif;
  }}

  .dot:hover .dot-tooltip {{ opacity: 1; }}

  /* LEGEND / SIDEBAR */
  .sidebar {{
    width: 220px;
    flex-shrink: 0;
  }}

  .sidebar-title {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #666;
    margin-bottom: 10px;
  }}

  .legend-item {{
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 8px 10px;
    border-radius: 8px;
    background: white;
    margin-bottom: 6px;
    border: 1.5px solid #e8e8e8;
    transition: border-color 0.15s;
  }}

  .legend-item:hover {{ border-color: #1a1a2e; }}

  .legend-dot {{
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #1a1a2e;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: white;
    font-weight: 500;
    margin-top: 1px;
  }}

  .legend-text {{
    flex: 1;
    min-width: 0;
  }}

  .legend-label {{
    font-size: 12px;
    font-weight: 600;
    color: #1a1a2e;
    word-break: break-word;
    line-height: 1.3;
  }}

  .legend-quadrant {{
    font-size: 10px;
    color: #888;
    margin-top: 2px;
    font-weight: 500;
  }}

  .dot-colors {{
    background: #1a1a2e;
  }}

  /* dot color palette for variety */
</style>
</head>
<body>

<div class="layout">
  <div class="grid-section">
    <div class="axis-label-top">← Low Effort &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; High Effort →</div>
    <div class="grid-row">
      <div class="axis-label-side">← Low Impact &nbsp; High Impact →</div>
      <div id="matrix">
        <div class="quadrant q-quick"><span class="quadrant-label">Quick<br>Wins</span></div>
        <div class="quadrant q-major"><span class="quadrant-label">Major<br>Projects</span></div>
        <div class="quadrant q-fillin"><span class="quadrant-label">Fill-in</span></div>
        <div class="quadrant q-money"><span class="quadrant-label">Thankless<br>Tasks</span></div>
        <div class="divider-h"></div>
        <div class="divider-v"></div>
      </div>
    </div>
  </div>

  <div class="sidebar">
    <div class="sidebar-title">Initiatives</div>
    <div id="legend"></div>
    <div id="empty-state" style="font-size:12px;color:#aaa;padding:8px 0;display:none;">
      Add initiatives using the form above.
    </div>
  </div>
</div>

<script>
const DOT_COLORS = [
  '#1a1a2e','#2d6a4f','#1565c0','#b5451b',
  '#6a0572','#0077b6','#9b2226','#386641'
];

const initiatives = {initiatives_json};

const matrix = document.getElementById('matrix');
const legend = document.getElementById('legend');
const emptyState = document.getElementById('empty-state');

let positions = {{}};
// Load saved positions from sessionStorage
try {{
  const saved = sessionStorage.getItem('matrixPositions');
  if (saved) positions = JSON.parse(saved);
}} catch(e) {{}}

function getQuadrantName(x, y) {{
  // x: 0=left(low effort), 100=right(high effort)
  // y: 0=top(high impact), 100=bottom(low impact)
  const highImpact = y < 50;
  const highEffort = x > 50;
  if (highImpact && !highEffort) return 'Quick Win';
  if (highImpact && highEffort)  return 'Major Project';
  if (!highImpact && !highEffort) return 'Fill-in';
  return 'Thankless Task';
}}

function savePositions() {{
  try {{ sessionStorage.setItem('matrixPositions', JSON.stringify(positions)); }} catch(e) {{}}
}}

function updateLegend() {{
  legend.innerHTML = '';
  if (initiatives.length === 0) {{
    emptyState.style.display = 'block';
    return;
  }}
  emptyState.style.display = 'none';
  initiatives.forEach((item, i) => {{
    const pos = positions[item.id] || {{ x: 50, y: 50 }};
    const quad = getQuadrantName(pos.x, pos.y);
    const color = DOT_COLORS[i % DOT_COLORS.length];
    const el = document.createElement('div');
    el.className = 'legend-item';
    el.id = 'legend_' + item.id;
    el.innerHTML = `
      <div class="legend-dot" style="background:${{color}}">${{i+1}}</div>
      <div class="legend-text">
        <div class="legend-label">${{item.label}}</div>
        <div class="legend-quadrant" id="quad_${{item.id}}">${{quad}}</div>
      </div>
    `;
    legend.appendChild(el);
  }});
}}

function renderDots() {{
  // Remove existing dots
  document.querySelectorAll('.dot').forEach(d => d.remove());

  initiatives.forEach((item, i) => {{
    const pos = positions[item.id] || {{ x: 50, y: 50 }};
    const color = DOT_COLORS[i % DOT_COLORS.length];
    const dot = document.createElement('div');
    dot.className = 'dot';
    dot.id = 'dot_' + item.id;
    dot.style.background = color;
    dot.style.left = pos.x + '%';
    dot.style.top = pos.y + '%';
    dot.innerHTML = `${{i+1}}<div class="dot-tooltip">${{item.label}}</div>`;
    dot.dataset.id = item.id;

    // Drag logic
    let isDragging = false;
    let startX, startY, startLeft, startTop;

    dot.addEventListener('mousedown', (e) => {{
      e.preventDefault();
      isDragging = true;
      dot.classList.add('dragging');
      const rect = matrix.getBoundingClientRect();
      startX = e.clientX;
      startY = e.clientY;
      startLeft = parseFloat(dot.style.left);
      startTop = parseFloat(dot.style.top);

      function onMove(e) {{
        if (!isDragging) return;
        const dx = ((e.clientX - startX) / rect.width) * 100;
        const dy = ((e.clientY - startY) / rect.height) * 100;
        let newX = Math.max(2, Math.min(98, startLeft + dx));
        let newY = Math.max(2, Math.min(98, startTop + dy));
        dot.style.left = newX + '%';
        dot.style.top = newY + '%';
        positions[item.id] = {{ x: newX, y: newY }};
        // Update legend quadrant
        const quadEl = document.getElementById('quad_' + item.id);
        if (quadEl) quadEl.textContent = getQuadrantName(newX, newY);
      }}

      function onUp() {{
        isDragging = false;
        dot.classList.remove('dragging');
        savePositions();
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
      }}

      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onUp);
    }});

    // Touch support
    dot.addEventListener('touchstart', (e) => {{
      e.preventDefault();
      const touch = e.touches[0];
      isDragging = true;
      dot.classList.add('dragging');
      const rect = matrix.getBoundingClientRect();
      startX = touch.clientX;
      startY = touch.clientY;
      startLeft = parseFloat(dot.style.left);
      startTop = parseFloat(dot.style.top);

      function onMove(e) {{
        const touch = e.touches[0];
        const dx = ((touch.clientX - startX) / rect.width) * 100;
        const dy = ((touch.clientY - startY) / rect.height) * 100;
        let newX = Math.max(2, Math.min(98, startLeft + dx));
        let newY = Math.max(2, Math.min(98, startTop + dy));
        dot.style.left = newX + '%';
        dot.style.top = newY + '%';
        positions[item.id] = {{ x: newX, y: newY }};
        const quadEl = document.getElementById('quad_' + item.id);
        if (quadEl) quadEl.textContent = getQuadrantName(newX, newY);
      }}

      function onEnd() {{
        isDragging = false;
        dot.classList.remove('dragging');
        savePositions();
        dot.removeEventListener('touchmove', onMove);
        dot.removeEventListener('touchend', onEnd);
      }}

      dot.addEventListener('touchmove', onMove, {{passive: false}});
      dot.addEventListener('touchend', onEnd);
    }}, {{passive: false}});

    matrix.appendChild(dot);
  }});
}}

updateLegend();
renderDots();
</script>
</body>
</html>
"""

# Render the interactive matrix
components.html(html_code, height=580, scrolling=False)

# Show a clear/reset option if there are initiatives
if st.session_state.initiatives:
    st.divider()
    cols = st.columns([6, 1])
    with cols[1]:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.initiatives = []
            st.rerun()
    with cols[0]:
        st.caption(f"{len(st.session_state.initiatives)} initiative(s) on the board. Drag dots to reposition them.")
