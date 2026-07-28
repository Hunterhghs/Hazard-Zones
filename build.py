#!/usr/bin/env python3
"""Single-pass build: Stitch HTML → 4 enhanced pages with Chart.js replacing placeholders."""

import re
import os

STITCH_DIR = "stitch-sources"
OUTPUT_DIR = "."

PAGES = {
    "home": {
        "file": "index.html",
        "stitch": "home.html",
        "title": "Hazard Zones — The Geography of Human Exposure",
        "active": "Home",
    },
    "heat": {
        "file": "heat-cognition.html",
        "stitch": "heat-cognition.html",
        "title": "Heat & Cognition — Hazard Zones",
        "active": "Heat &amp; Cognition",
    },
    "trap": {
        "file": "the-trap.html",
        "stitch": "the-trap.html",
        "title": "The Climate–Education Trap — Hazard Zones",
        "active": "The Trap",
    },
    "outlook": {
        "file": "outlook.html",
        "stitch": "outlook.html",
        "title": "Outlook — Hazard Zones",
        "active": "Outlook",
    },
}

NAV_TABS = [
    ("index.html", "Home"),
    ("heat-cognition.html", "Heat &amp; Cognition"),
    ("the-trap.html", "The Trap"),
    ("outlook.html", "Outlook"),
]

CHARTJS_CDN = '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>'


def make_nav(active_name):
    lines = ['<header class="fixed top-0 w-full z-50 bg-background/95 backdrop-blur-md border-b border-outline-variant">',
             '<div class="flex justify-between items-center px-margin-desktop py-4 max-w-container-max mx-auto">',
             '<a href="index.html" class="font-headline-lg text-headline-lg font-bold text-primary tracking-tighter uppercase no-underline">HAZARD ZONES</a>',
             '<nav class="hidden md:flex items-center space-x-10 font-label-caps text-label-caps uppercase tracking-widest">']
    for href, label in NAV_TABS:
        cls = "text-primary border-b-2 border-primary pb-1" if label == active_name else "text-on-surface-variant hover:text-primary"
        lines.append(f'<a href="{href}" class="{cls} transition-colors duration-200 no-underline">{label}</a>')
    lines.append('</nav>')
    lines.append('<div class="hidden md:block font-label-caps text-label-caps text-primary-container uppercase tracking-widest">A H Heuristics Project</div>')
    lines.append('</div></header>')
    return "\n".join(lines)


FOOTER = """
<footer class="bg-surface-dim mt-stack-xl border-t border-outline-variant">
<div class="grid grid-cols-1 md:grid-cols-2 gap-gutter px-margin-desktop py-stack-lg max-w-container-max mx-auto">
<div class="space-y-6">
<div class="font-headline-lg text-headline-lg text-on-surface uppercase tracking-tighter font-bold">HAZARD ZONES</div>
<p class="font-body-md text-body-md text-on-surface-variant max-w-md">
A H Heuristics Project — mapping the geography of human exposure to environmental hazards.
Investigating where extreme heat, toxic air, flooding, and demographic pressure collide with the
weakest educational and institutional buffers on Earth.
</p>
<div class="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest">
&copy; 2026 HAZARD ZONES. A H HEURISTICS PROJECT.
</div>
</div>
<div class="grid grid-cols-2 gap-stack-lg">
<div class="flex flex-col space-y-4">
<h4 class="font-label-caps text-label-caps text-primary uppercase">Navigate</h4>
<a class="font-body-md text-body-md text-on-surface-variant hover:underline decoration-primary underline-offset-4 no-underline" href="index.html">Home</a>
<a class="font-body-md text-body-md text-on-surface-variant hover:underline decoration-primary underline-offset-4 no-underline" href="heat-cognition.html">Heat &amp; Cognition</a>
<a class="font-body-md text-body-md text-on-surface-variant hover:underline decoration-primary underline-offset-4 no-underline" href="the-trap.html">The Trap</a>
<a class="font-body-md text-body-md text-on-surface-variant hover:underline decoration-primary underline-offset-4 no-underline" href="outlook.html">Outlook</a>
</div>
<div class="flex flex-col space-y-4">
<h4 class="font-label-caps text-label-caps text-primary uppercase">Resources</h4>
<a class="font-body-md text-body-md text-on-surface-variant hover:underline decoration-primary underline-offset-4 no-underline" href="https://hheuristics.com" target="_blank">H Heuristics</a>
<a class="font-body-md text-body-md text-on-surface-variant hover:underline decoration-primary underline-offset-4 no-underline" href="https://open.substack.com/pub/hheuristics/p/hazard-zones-the-geography-of-human" target="_blank">Original Article</a>
</div>
</div>
</div>
</footer>
"""


# ── Chart replacement: (pattern_to_find, replacement_html_with_canvas) ──

# index.html: replace the CSS-bar placeholder with a real Chart.js canvas section
REPLACE_HOME_BARS = (
    r'<div class="bg-surface-container-high p-8 border border-outline-variant h-\[400px\][^"]*">.*?</div>\s*</div>\s*</div>\s*</section>',
    r"""<div class="bg-surface-container-low p-6 border border-outline-variant h-[400px]">
<canvas id="chartFrontlineBelts"></canvas>
</div>
</div>
</div>
</section>"""
)

# heat-cognition.html: replace "data-visual-placeholder" bubble chart placeholder
REPLACE_HEAT_BUBBLE = (
    r'<div class="data-visual-placeholder thin-border h-80 flex items-center justify-center relative group">.*?</div>\s*</div>\s*</div>\s*</section>',
    r"""<div class="bg-surface-container-low p-6 border border-outline-variant h-80">
<canvas id="chartCities"></canvas>
</div>
</div>
</div>
</section>"""
)

# heat-cognition.html: replace bg-image line chart placeholder
REPLACE_HEAT_LINE = (
    r'<div class="data-visual-placeholder thin-border h-80 flex items-center justify-center relative overflow-hidden">.*?</div>\s*</div>',
    r"""<div class="bg-surface-container-low p-6 border border-outline-variant h-80">
<canvas id="chartCognitive"></canvas>
</div>
</div>"""
)

# the-trap.html: replace the SVG feedback loop with real canvas
# the-trap also has placeholder chart areas in the "Education Gap" section
REPLACE_TRAP_SVG = (
    r'<svg class="absolute inset-0 w-full h-full pointer-events-none".*?</svg>',
    r'<canvas id="chartReadiness"></canvas>'
)

# the-trap.html: replace attainment placeholder
REPLACE_TRAP_ATTAINMENT = (
    r'<div class="lg:col-span-6 bg-surface-container-low p-8 thin-border flex items-center justify-center min-h-\[350px\]">.*?</div>\s*</div>\s*</div>\s*</section>',
    r"""<div class="lg:col-span-6 bg-surface-container-low p-6 border border-outline-variant">
<canvas id="chartAttainment"></canvas>
</div>
</div>
</div>
</section>"""
)

# outlook.html: replace empty chart containers
REPLACE_OUTLOOK_POP = (
    r'<div class="md:col-span-7 bg-surface p-8 thin-border flex flex-col justify-between min-h-\[400px\]">.*?</div>\s*</div>\s*</div>\s*</section>',
    r"""<div class="md:col-span-7 bg-surface-container-low p-6 border border-outline-variant">
<canvas id="chartPopulation"></canvas>
</div>
</div>
</div>
</section>"""
)

# outlook.html: replace adaptation readiness placeholder
REPLACE_OUTLOOK_INTERV = (
    r'<div class="lg:col-span-7 bg-surface p-8 thin-border flex items-center justify-center min-h-\[350px\]">.*?</div>\s*</div>\s*</div>\s*</section>',
    r"""<div class="lg:col-span-7 bg-surface-container-low p-6 border border-outline-variant">
<canvas id="chartInterventions"></canvas>
</div>
</div>
</div>
</section>"""
)


# ── Chart.js initialization scripts ──

CHART_SCRIPTS_HOME = """
<script>
(function() {
var ctx = document.getElementById('chartFrontlineBelts');
if (!ctx) return;
new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Indo-Gangetic', 'Sahel', 'West Africa', 'MENA Deltas', 'LatAm Dry Corr.'],
        datasets: [{
            label: 'Exposed Population (millions)',
            data: [685, 410, 295, 180, 125],
            backgroundColor: '#f06620',
            borderRadius: 2
        }]
    },
    options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
            x: { ticks: { color: '#a88a7f' }, grid: { color: 'rgba(168,138,127,0.15)' }, title: { display: true, text: 'Millions', color: '#a88a7f' } },
            y: { ticks: { color: '#e5e2e1', font: { family: 'Space Grotesk', size: 13, weight: '600' } }, grid: { display: false } }
        }
    }
});
})();
</script>
"""

CHART_SCRIPTS_HEAT = """
<script>
(function() {
// Bubble chart: Cities vs Adaptation
var c1 = document.getElementById('chartCities');
if (c1) { new Chart(c1, { type: 'bubble', data: { datasets: [
    { label: 'Karachi', data: [{x:62,y:24,r:22}], backgroundColor: 'rgba(240,102,32,0.7)' },
    { label: 'Niamey', data: [{x:110,y:18,r:18}], backgroundColor: 'rgba(240,102,32,0.7)' },
    { label: 'Dhaka', data: [{x:78,y:28,r:28}], backgroundColor: 'rgba(240,102,32,0.7)' },
    { label: 'Lagos', data: [{x:55,y:32,r:30}], backgroundColor: 'rgba(240,102,32,0.7)' },
    { label: 'Kolkata', data: [{x:85,y:22,r:25}], backgroundColor: 'rgba(240,102,32,0.7)' },
    { label: 'Jakarta', data: [{x:48,y:35,r:27}], backgroundColor: 'rgba(240,102,32,0.7)' },
    { label: 'Manila', data: [{x:52,y:30,r:23}], backgroundColor: 'rgba(240,102,32,0.7)' },
    { label: 'Khartoum', data: [{x:95,y:15,r:16}], backgroundColor: 'rgba(240,102,32,0.7)' }
]}, options: { responsive: true, maintainAspectRatio: false,
    plugins: { legend: { labels: { color: '#e5e2e1', font: { family: 'Inter' } } },
        tooltip: { callbacks: { label: function(c) { return c.dataset.label + ': ' + c.raw.x + ' heat days, readiness ' + c.raw.y; } } } },
    scales: {
        x: { title: { display: true, text: 'Extreme Heat Days (>38°C) Annually', color: '#a88a7f' }, ticks: { color: '#a88a7f' }, grid: { color: 'rgba(168,138,127,0.15)' } },
        y: { title: { display: true, text: 'Adaptation Readiness (out of 100)', color: '#a88a7f' }, ticks: { color: '#a88a7f' }, grid: { color: 'rgba(168,138,127,0.15)' }, min: 0, max: 60 }
    }
}}); }

// Line chart: Temperature vs Cognitive Decline
var c2 = document.getElementById('chartCognitive');
if (c2) { new Chart(c2, { type: 'line', data: {
    labels: ['30°C','32°C','34°C','36°C','38°C','40°C','42°C'],
    datasets: [{ label: 'Cognitive Performance Index', data: [100,97,93,87,78,66,52],
        borderColor: '#f06620', backgroundColor: 'rgba(240,102,32,0.1)', fill: true, tension: 0.3, pointBackgroundColor: '#f06620', pointRadius: 5 }]
}, options: { responsive: true, maintainAspectRatio: false,
    plugins: { legend: { labels: { color: '#e5e2e1', font: { family: 'Inter' } } } },
    scales: {
        x: { title: { display: true, text: 'Ambient Temperature', color: '#a88a7f' }, ticks: { color: '#a88a7f' }, grid: { color: 'rgba(168,138,127,0.15)' } },
        y: { title: { display: true, text: 'Cognitive Performance (index)', color: '#a88a7f' }, ticks: { color: '#a88a7f' }, grid: { color: 'rgba(168,138,127,0.15)' }, min: 40, max: 105 }
    }
}}); }
})();
</script>
"""

CHART_SCRIPTS_TRAP = """
<script>
(function() {
// Grouped bar: Tertiary Attainment
var c1 = document.getElementById('chartAttainment');
if (c1) { new Chart(c1, { type: 'bar', data: {
    labels: ['Sahel','W. Africa','MENA Deltas','LatAm Dry','Indo-Gangetic','OECD'],
    datasets: [
        { label: 'Tertiary Attainment (%)', data: [18,22,34,28,25,58], backgroundColor: '#f06620', borderRadius: 2 },
        { label: 'Adaptation Threshold (~45%)', data: [45,45,45,45,45,45], backgroundColor: 'rgba(156,202,255,0.3)', borderColor: '#9ccaff', borderWidth: 2, borderDash: [6,4], type: 'line', fill: false, pointRadius: 0 }
    ]
}, options: { responsive: true, maintainAspectRatio: false,
    plugins: { legend: { labels: { color: '#e5e2e1', font: { family: 'Inter' } } } },
    scales: {
        x: { ticks: { color: '#e5e2e1', font: { family: 'Space Grotesk', size: 12, weight: '600' } }, grid: { display: false } },
        y: { ticks: { color: '#a88a7f' }, grid: { color: 'rgba(168,138,127,0.15)' }, max: 70, title: { display: true, text: 'Percentage (%)', color: '#a88a7f' } }
    }
}}); }

// Radar: Adaptation Readiness
var c2 = document.getElementById('chartReadiness');
if (c2) { new Chart(c2, { type: 'radar', data: {
    labels: ['Institutional','Infrastructure','Education','Health','Economy','Climate Finance'],
    datasets: [
        { label: 'Sahel', data: [18,12,15,22,14,20], borderColor: '#f06620', backgroundColor: 'rgba(240,102,32,0.15)', borderWidth: 2 },
        { label: 'MENA Deltas', data: [34,28,32,38,30,35], borderColor: '#9ccaff', backgroundColor: 'rgba(156,202,255,0.1)', borderWidth: 2 },
        { label: 'OECD Benchmark', data: [72,78,65,80,75,70], borderColor: '#c8c6c5', backgroundColor: 'transparent', borderWidth: 2, borderDash: [4,4] }
    ]
}, options: { responsive: true, maintainAspectRatio: false,
    plugins: { legend: { labels: { color: '#e5e2e1', font: { family: 'Inter' } } } },
    scales: { r: { angleLines: { color: 'rgba(168,138,127,0.3)' }, grid: { color: 'rgba(168,138,127,0.2)' },
        pointLabels: { color: '#e5e2e1', font: { family: 'Space Grotesk', size: 11 } },
        ticks: { color: '#a88a7f', backdropColor: 'transparent' }, suggestedMin: 0, suggestedMax: 90 } }
}}); }
})();
</script>
"""

CHART_SCRIPTS_OUTLOOK = """
<script>
(function() {
// Stacked bar: Population projections
var c1 = document.getElementById('chartPopulation');
if (c1) { new Chart(c1, { type: 'bar', data: {
    labels: ['2025','2035','2050','2075','2100'],
    datasets: [
        { label: 'Indo-Gangetic', data: [685,780,920,1050,1120], backgroundColor: '#f06620' },
        { label: 'Sahel', data: [410,520,680,850,980], backgroundColor: 'rgba(240,102,32,0.6)' },
        { label: 'West Africa', data: [295,380,500,620,720], backgroundColor: 'rgba(240,102,32,0.4)' },
        { label: 'MENA Deltas', data: [180,220,280,340,380], backgroundColor: 'rgba(240,102,32,0.25)' }
    ]
}, options: { responsive: true, maintainAspectRatio: false,
    plugins: { legend: { labels: { color: '#e5e2e1', font: { family: 'Inter' } } } },
    scales: {
        x: { stacked: true, ticks: { color: '#e5e2e1', font: { family: 'Space Grotesk', size: 12 } }, grid: { display: false } },
        y: { stacked: true, ticks: { color: '#a88a7f' }, grid: { color: 'rgba(168,138,127,0.15)' }, title: { display: true, text: 'Population (Millions)', color: '#a88a7f' } }
    }
}}); }

// Horizontal bar: Intervention impact
var c2 = document.getElementById('chartInterventions');
if (c2) { new Chart(c2, { type: 'bar', data: {
    labels: ['Climate-Proof Schools','Tech Institutes','Cash Transfers','Female Education','Infrastructure Only'],
    datasets: [{ label: 'Impact (per $1M)', data: [850,720,680,920,310],
        backgroundColor: ['#f06620','#f06620','#f06620','#f06620','#474746'], borderRadius: 2 }]
}, options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
        x: { ticks: { color: '#a88a7f' }, grid: { color: 'rgba(168,138,127,0.15)' }, title: { display: true, text: 'Lives improved per $1M', color: '#a88a7f' } },
        y: { ticks: { color: '#e5e2e1', font: { family: 'Space Grotesk', size: 12, weight: '600' } }, grid: { display: false } }
    }
}}); }
})();
</script>
"""

# Map page keys to chart script blocks
CHART_SCRIPTS = {
    "home": CHART_SCRIPTS_HOME,
    "heat": CHART_SCRIPTS_HEAT,
    "trap": CHART_SCRIPTS_TRAP,
    "outlook": CHART_SCRIPTS_OUTLOOK,
}

# Map page keys to lists of (pattern, replacement) tuples
PAGE_REPLACEMENTS = {
    "home": [REPLACE_HOME_BARS],
    "heat": [REPLACE_HEAT_BUBBLE, REPLACE_HEAT_LINE],
    "trap": [REPLACE_TRAP_SVG, REPLACE_TRAP_ATTAINMENT],
    "outlook": [REPLACE_OUTLOOK_POP, REPLACE_OUTLOOK_INTERV],
}


def build_page(page_key):
    cfg = PAGES[page_key]
    stitch_path = os.path.join(STITCH_DIR, cfg["stitch"])
    output_path = os.path.join(OUTPUT_DIR, cfg["file"])

    with open(stitch_path, "r") as f:
        html = f.read()

    # 1. Clean Stitch artifacts
    html = re.sub(r'(<link href="https://fonts\.googleapis\.com/css2\?family=Material\+Symbols\+Outlined[^"]*"[^>]*>)\s*\1', r'\1', html, flags=re.DOTALL)
    html = html.replace("background-color: #0D0D0D;", "background-color: #131313;")
    html = html.replace("</head>", f"{CHARTJS_CDN}\n</head>")

    # 2. Replace header/nav (both <header> and <nav class="fixed..."> patterns)
    html = re.sub(r"<header[^>]*>.*?</header>", make_nav(cfg["active"]), html, flags=re.DOTALL)
    html = re.sub(r'<nav\s+class="fixed top-0[^>]*>.*?</nav>', make_nav(cfg["active"]), html, flags=re.DOTALL)

    # 3. Replace old footer
    html = re.sub(r"<footer[^>]*>.*?</footer>", FOOTER, html, flags=re.DOTALL)

    # 4. Remove old micro-interactions script
    html = re.sub(r"<script>\s*// Optional Micro-interactions.*?</script>", "", html, flags=re.DOTALL)

    # 5. Replace placeholder chart areas with real canvases
    for pattern, replacement in PAGE_REPLACEMENTS.get(page_key, []):
        html = re.sub(pattern, replacement, html, flags=re.DOTALL)

    # 6. Fix main padding
    html = html.replace('class="pt-24"', 'class="pt-24 pb-stack-xl"')

    # 7. Fix title
    html = re.sub(r"<title>.*?</title>", f"<title>{cfg['title']}</title>", html)

    # 8. Remove any leftover data-visual-placeholder elements
    html = re.sub(r'<div class="data-visual-placeholder[^"]*".*?</div>\s*</div>\s*</div>', '', html, flags=re.DOTALL)

    # 9. Remove any leftover empty chart containers from Stitch
    html = re.sub(r'<div class="bg-cover bg-center grayscale opacity-40"[^>]*></div>', '', html)

    # 10. Inject chart scripts before </body>
    chart_script = CHART_SCRIPTS.get(page_key, "")
    html = html.replace("</body>", f"{chart_script}\n</body>")

    # 11. Add .nojekyll hint
    html = "<!-- .nojekyll -->\n" + html

    with open(output_path, "w") as f:
        f.write(html)

    print(f"  Built: {output_path} ({len(html)} bytes)")


def main():
    print("Building Hazard Zones website...")
    for key in PAGES:
        build_page(key)

    with open(".nojekyll", "w") as f:
        f.write("")

    # CNAME for custom domain
    with open("CNAME", "w") as f:
        f.write("hazardzones.hheuristics.com\n")

    os.makedirs(".github/workflows", exist_ok=True)
    with open(".github/workflows/pages.yml", "w") as f:
        f.write("""name: Deploy to GitHub Pages
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: "pages"
  cancel-in-progress: false
jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: '.'
      - uses: actions/deploy-pages@v4
""")
    print("  Created: .github/workflows/pages.yml")
    print("  Created: .nojekyll")
    print("  Created: CNAME → hazardzones.hheuristics.com")
    print("\nBuild complete. 4 pages ready.")


if __name__ == "__main__":
    main()
