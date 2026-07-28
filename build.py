#!/usr/bin/env python3
"""Single-pass build: Stitch HTML → 4 enhanced pages with Chart.js interactive visuals."""

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

# Shared nav HTML template
def make_nav(active_name):
    lines = []
    lines.append(
        '<header class="fixed top-0 w-full z-50 bg-background/95 backdrop-blur-md border-b border-outline-variant">'
    )
    lines.append(
        '<div class="flex justify-between items-center px-margin-desktop py-4 max-w-container-max mx-auto">'
    )
    lines.append(
        '<a href="index.html" class="font-headline-lg text-headline-lg font-bold text-primary tracking-tighter uppercase no-underline">HAZARD ZONES</a>'
    )
    lines.append(
        '<nav class="hidden md:flex items-center space-x-10 font-label-caps text-label-caps uppercase tracking-widest">'
    )
    for href, label in NAV_TABS:
        if label == active_name:
            lines.append(
                f'<a href="{href}" class="text-primary border-b-2 border-primary pb-1 transition-colors duration-200 no-underline">{label}</a>'
            )
        else:
            lines.append(
                f'<a href="{href}" class="text-on-surface-variant hover:text-primary transition-colors duration-200 no-underline">{label}</a>'
            )
    lines.append("</nav>")
    lines.append(
        '<div class="hidden md:block font-label-caps text-label-caps text-primary-container uppercase tracking-widest">A H Heuristics Project</div>'
    )
    lines.append("</div>")
    lines.append("</header>")
    return "\n".join(lines)


# Shared footer HTML
FOOTER = """
<footer class="bg-surface-dim mt-stack-xl border-t border-outline-variant">
<div class="grid grid-cols-1 md:grid-cols-2 gap-gutter px-margin-desktop py-stack-lg max-w-container-max mx-auto">
<div class="space-y-6">
<div class="font-headline-lg text-headline-lg text-on-surface uppercase tracking-tighter font-bold">HAZARD ZONES</div>
<p class="font-body-md text-body-md text-on-surface-variant max-w-md">
A H Heuristics Project — mapping the geography of human exposure to environmental hazards.
Investigating where extreme heat, toxic air, flooding, and demographic pressure collide.
</p>
<div class="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-widest">
© 2026 HAZARD ZONES. A H HEURISTICS PROJECT.
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

# ── Chart.js CDN ──
CHARTJS_CDN = '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>'

# ── Chart configurations per page ──

CHARTS_HOME = """
<div class="px-margin-desktop py-stack-lg max-w-container-max mx-auto">
<h2 class="font-headline-lg text-headline-lg text-on-surface mb-stack-lg border-l-4 border-primary-container pl-6 uppercase">Exposed Population by Region</h2>
<div class="bg-surface-container-low p-6 border border-outline-variant" style="max-width:900px;margin:0 auto;">
<canvas id="chartFrontlineBelts" height="350"></canvas>
</div>
</div>
<script>
(function() {
var ctx = document.getElementById('chartFrontlineBelts').getContext('2d');
new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Indo-Gangetic', 'Sahel', 'West Africa', 'MENA Deltas', 'LatAm Dry Corridor'],
        datasets: [{
            label: 'Exposed Population (millions)',
            data: [685, 410, 295, 180, 125],
            backgroundColor: 'rgba(240, 102, 32, 0.7)',
            borderColor: '#f06620',
            borderWidth: 1,
            borderRadius: 2
        }]
    },
    options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false }
        },
        scales: {
            x: {
                ticks: { color: '#a88a7f', font: { family: 'Inter', size: 12 } },
                grid: { color: 'rgba(168,138,127,0.15)' },
                title: { display: true, text: 'Millions', color: '#a88a7f' }
            },
            y: {
                ticks: { color: '#e5e2e1', font: { family: 'Space Grotesk', size: 13, weight: '600' } },
                grid: { display: false }
            }
        }
    }
});
})();
</script>
"""

CHARTS_HEAT = """
<div class="px-margin-desktop py-stack-lg max-w-container-max mx-auto">
<h2 class="font-headline-lg text-headline-lg text-on-surface mb-stack-lg border-l-4 border-primary-container pl-6 uppercase">Frontline Cities: Heat Days vs. Adaptation Readiness</h2>
<div class="bg-surface-container-low p-6 border border-outline-variant" style="max-width:900px;margin:0 auto;">
<canvas id="chartCities" height="400"></canvas>
</div>
</div>
<div class="px-margin-desktop py-stack-lg max-w-container-max mx-auto">
<h2 class="font-headline-lg text-headline-lg text-on-surface mb-stack-lg border-l-4 border-primary-container pl-6 uppercase">Temperature &amp; Cognitive Decline</h2>
<div class="bg-surface-container-low p-6 border border-outline-variant" style="max-width:900px;margin:0 auto;">
<canvas id="chartCognitive" height="350"></canvas>
</div>
</div>
<script>
(function() {
// Bubble chart: Cities vs Adaptation
var ctx1 = document.getElementById('chartCities').getContext('2d');
new Chart(ctx1, {
    type: 'bubble',
    data: {
        datasets: [
            { label: 'Karachi', data: [{x: 62, y: 24, r: 22}], backgroundColor: 'rgba(240,102,32,0.7)' },
            { label: 'Niamey', data: [{x: 110, y: 18, r: 18}], backgroundColor: 'rgba(240,102,32,0.7)' },
            { label: 'Dhaka', data: [{x: 78, y: 28, r: 28}], backgroundColor: 'rgba(240,102,32,0.7)' },
            { label: 'Lagos', data: [{x: 55, y: 32, r: 30}], backgroundColor: 'rgba(240,102,32,0.7)' },
            { label: 'Kolkata', data: [{x: 85, y: 22, r: 25}], backgroundColor: 'rgba(240,102,32,0.7)' },
            { label: 'Jakarta', data: [{x: 48, y: 35, r: 27}], backgroundColor: 'rgba(240,102,32,0.7)' },
            { label: 'Manila', data: [{x: 52, y: 30, r: 23}], backgroundColor: 'rgba(240,102,32,0.7)' },
            { label: 'Khartoum', data: [{x: 95, y: 15, r: 16}], backgroundColor: 'rgba(240,102,32,0.7)' }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: { callbacks: { label: function(c) { return c.dataset.label + ': ' + c.raw.x + ' heat days, readiness ' + c.raw.y; } } }
        },
        scales: {
            x: {
                title: { display: true, text: 'Extreme Heat Days (>38°C) Annually', color: '#a88a7f' },
                ticks: { color: '#a88a7f' }, grid: { color: 'rgba(168,138,127,0.15)' }
            },
            y: {
                title: { display: true, text: 'Adaptation Readiness (out of 100)', color: '#a88a7f' },
                ticks: { color: '#a88a7f' }, grid: { color: 'rgba(168,138,127,0.15)' },
                min: 0, max: 60
            }
        }
    }
});

// Line chart: Temperature vs Cognitive Decline
var ctx2 = document.getElementById('chartCognitive').getContext('2d');
new Chart(ctx2, {
    type: 'line',
    data: {
        labels: ['30°C', '32°C', '34°C', '36°C', '38°C', '40°C', '42°C'],
        datasets: [{
            label: 'Cognitive Performance Index',
            data: [100, 97, 93, 87, 78, 66, 52],
            borderColor: '#f06620',
            backgroundColor: 'rgba(240,102,32,0.1)',
            fill: true,
            tension: 0.3,
            pointBackgroundColor: '#f06620',
            pointRadius: 5
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: '#e5e2e1', font: { family: 'Inter' } } }
        },
        scales: {
            x: {
                title: { display: true, text: 'Ambient Temperature', color: '#a88a7f' },
                ticks: { color: '#a88a7f' }, grid: { color: 'rgba(168,138,127,0.15)' }
            },
            y: {
                title: { display: true, text: 'Cognitive Performance (index)', color: '#a88a7f' },
                ticks: { color: '#a88a7f' }, grid: { color: 'rgba(168,138,127,0.15)' },
                min: 40, max: 105
            }
        }
    }
});
})();
</script>
"""

CHARTS_TRAP = """
<div class="px-margin-desktop py-stack-lg max-w-container-max mx-auto">
<h2 class="font-headline-lg text-headline-lg text-on-surface mb-stack-lg border-l-4 border-primary-container pl-6 uppercase">Post-Secondary Attainment: Hazard Zones vs. OECD</h2>
<div class="bg-surface-container-low p-6 border border-outline-variant" style="max-width:900px;margin:0 auto;">
<canvas id="chartAttainment" height="350"></canvas>
</div>
</div>
<div class="px-margin-desktop py-stack-lg max-w-container-max mx-auto">
<h2 class="font-headline-lg text-headline-lg text-on-surface mb-stack-lg border-l-4 border-primary-container pl-6 uppercase">Adaptation Readiness: Regional Scores</h2>
<div class="bg-surface-container-low p-6 border border-outline-variant" style="max-width:900px;margin:0 auto;">
<canvas id="chartReadiness" height="350"></canvas>
</div>
</div>
<script>
(function() {
// Grouped bar: Tertiary Attainment
var ctx1 = document.getElementById('chartAttainment').getContext('2d');
new Chart(ctx1, {
    type: 'bar',
    data: {
        labels: ['Sahel', 'W. Africa', 'MENA Deltas', 'LatAm Dry Corr.', 'Indo-Gangetic', 'OECD Baseline'],
        datasets: [{
            label: 'Tertiary Attainment (%)',
            data: [18, 22, 34, 28, 25, 58],
            backgroundColor: '#f06620',
            borderRadius: 2
        }, {
            label: 'Adaptation Threshold (~45%)',
            data: [45, 45, 45, 45, 45, 45],
            backgroundColor: 'rgba(156, 202, 255, 0.3)',
            borderColor: '#9ccaff',
            borderWidth: 2,
            borderDash: [6, 4],
            type: 'line',
            fill: false,
            pointRadius: 0
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: '#e5e2e1', font: { family: 'Inter' } } }
        },
        scales: {
            x: { ticks: { color: '#e5e2e1', font: { family: 'Space Grotesk', size: 12, weight: '600' } }, grid: { display: false } },
            y: { ticks: { color: '#a88a7f' }, grid: { color: 'rgba(168,138,127,0.15)' }, max: 70,
                title: { display: true, text: 'Percentage (%)', color: '#a88a7f' } }
        }
    }
});

// Radar: Adaptation Readiness
var ctx2 = document.getElementById('chartReadiness').getContext('2d');
new Chart(ctx2, {
    type: 'radar',
    data: {
        labels: ['Institutional Capacity', 'Infrastructure', 'Education Base', 'Health Systems', 'Economic Resilience', 'Climate Finance Access'],
        datasets: [{
            label: 'Sahel',
            data: [18, 12, 15, 22, 14, 20],
            borderColor: '#f06620',
            backgroundColor: 'rgba(240,102,32,0.15)',
            borderWidth: 2
        }, {
            label: 'MENA Deltas',
            data: [34, 28, 32, 38, 30, 35],
            borderColor: '#9ccaff',
            backgroundColor: 'rgba(156,202,255,0.1)',
            borderWidth: 2
        }, {
            label: 'OECD Benchmark',
            data: [72, 78, 65, 80, 75, 70],
            borderColor: '#c8c6c5',
            backgroundColor: 'transparent',
            borderWidth: 2,
            borderDash: [4, 4]
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: '#e5e2e1', font: { family: 'Inter' } } }
        },
        scales: {
            r: {
                angleLines: { color: 'rgba(168,138,127,0.3)' },
                grid: { color: 'rgba(168,138,127,0.2)' },
                pointLabels: { color: '#e5e2e1', font: { family: 'Space Grotesk', size: 11 } },
                ticks: { color: '#a88a7f', backdropColor: 'transparent' },
                suggestedMin: 0, suggestedMax: 90
            }
        }
    }
});
})();
</script>
"""

CHARTS_OUTLOOK = """
<div class="px-margin-desktop py-stack-lg max-w-container-max mx-auto">
<h2 class="font-headline-lg text-headline-lg text-on-surface mb-stack-lg border-l-4 border-primary-container pl-6 uppercase">Population Growth in Hazard Zones (Projections)</h2>
<div class="bg-surface-container-low p-6 border border-outline-variant" style="max-width:900px;margin:0 auto;">
<canvas id="chartPopulation" height="350"></canvas>
</div>
</div>
<div class="px-margin-desktop py-stack-lg max-w-container-max mx-auto">
<h2 class="font-headline-lg text-headline-lg text-on-surface mb-stack-lg border-l-4 border-primary-container pl-6 uppercase">Intervention Impact Matrix</h2>
<div class="bg-surface-container-low p-6 border border-outline-variant" style="max-width:900px;margin:0 auto;">
<canvas id="chartInterventions" height="350"></canvas>
</div>
</div>
<script>
(function() {
// Stacked bar: Population projections
var ctx1 = document.getElementById('chartPopulation').getContext('2d');
new Chart(ctx1, {
    type: 'bar',
    data: {
        labels: ['2025', '2035', '2050', '2075', '2100'],
        datasets: [
            { label: 'Indo-Gangetic', data: [685, 780, 920, 1050, 1120], backgroundColor: '#f06620' },
            { label: 'Sahel', data: [410, 520, 680, 850, 980], backgroundColor: 'rgba(240,102,32,0.6)' },
            { label: 'West Africa', data: [295, 380, 500, 620, 720], backgroundColor: 'rgba(240,102,32,0.4)' },
            { label: 'MENA Deltas', data: [180, 220, 280, 340, 380], backgroundColor: 'rgba(240,102,32,0.25)' }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: '#e5e2e1', font: { family: 'Inter' } } }
        },
        scales: {
            x: {
                stacked: true,
                ticks: { color: '#e5e2e1', font: { family: 'Space Grotesk', size: 12 } },
                grid: { display: false }
            },
            y: {
                stacked: true,
                ticks: { color: '#a88a7f' },
                grid: { color: 'rgba(168,138,127,0.15)' },
                title: { display: true, text: 'Population (Millions)', color: '#a88a7f' }
            }
        }
    }
});

// Horizontal bar: Intervention impact
var ctx2 = document.getElementById('chartInterventions').getContext('2d');
new Chart(ctx2, {
    type: 'bar',
    data: {
        labels: ['Climate-Proof Schools', 'Applied Tech Institutes', 'Cash Transfers', 'Female Education Access', 'Infrastructure Only'],
        datasets: [{
            label: 'Estimated Impact (lives improved per $1M)',
            data: [850, 720, 680, 920, 310],
            backgroundColor: ['#f06620', '#f06620', '#f06620', '#f06620', '#474746'],
            borderRadius: 2
        }]
    },
    options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false }
        },
        scales: {
            x: {
                ticks: { color: '#a88a7f' },
                grid: { color: 'rgba(168,138,127,0.15)' },
                title: { display: true, text: 'Estimated lives improved per $1M investment', color: '#a88a7f' }
            },
            y: {
                ticks: { color: '#e5e2e1', font: { family: 'Space Grotesk', size: 12, weight: '600' } },
                grid: { display: false }
            }
        }
    }
});
})();
</script>
"""

CHART_BLOCKS = {
    "home": CHARTS_HOME,
    "heat": CHARTS_HEAT,
    "trap": CHARTS_TRAP,
    "outlook": CHARTS_OUTLOOK,
}


def build_page(page_key):
    cfg = PAGES[page_key]
    stitch_path = os.path.join(STITCH_DIR, cfg["stitch"])
    output_path = os.path.join(OUTPUT_DIR, cfg["file"])

    with open(stitch_path, "r") as f:
        html = f.read()

    # 1. Fix DOCTYPE placement — move .nojekyll comment after DOCTYPE
    html = re.sub(r"<!-- \.nojekyll -->\s*<!DOCTYPE", "<!DOCTYPE", html, flags=re.DOTALL)

    # 1b. Remove duplicate Material Symbols link (Stitch puts it twice)
    html = re.sub(
        r'(<link href="https://fonts\.googleapis\.com/css2\?family=Material\+Symbols\+Outlined[^"]*"[^>]*>)\s*\1',
        r"\1",
        html,
        flags=re.DOTALL,
    )

    # 1c. Fix body background-color to match Tailwind config (#131313 not #0D0D0D)
    html = html.replace("background-color: #0D0D0D;", "background-color: #131313;")

    # 1d. Add Chart.js CDN in head (before </head>)
    html = html.replace("</head>", f"{CHARTJS_CDN}\n</head>")

    # 2. Replace the existing <header>...</header> OR <nav class="fixed top-0...">...</nav> with our corrected nav
    html = re.sub(
        r"<header[^>]*>.*?</header>",
        make_nav(cfg["active"]),
        html,
        flags=re.DOTALL,
    )
    # Also catch <nav class="fixed top-0... masthead patterns
    html = re.sub(
        r"<nav\s+class=\"fixed top-0[^>]*>.*?</nav>",
        make_nav(cfg["active"]),
        html,
        flags=re.DOTALL,
    )

    # 3. Replace the existing <footer>...</footer> with our standardized footer
    html = re.sub(
        r"<footer[^>]*>.*?</footer>",
        FOOTER,
        html,
        flags=re.DOTALL,
    )

    # 4. Replace the old micro-interactions script block + remove it
    html = re.sub(
        r"<script>\s*// Optional Micro-interactions.*?</script>",
        "",
        html,
        flags=re.DOTALL,
    )

    # 5. Adjust main top padding (footer is added, charts injected)
    html = html.replace('class="pt-24"', 'class="pt-24 pb-stack-xl"')

    # 6. Fix the title
    html = re.sub(r"<title>.*?</title>", f"<title>{cfg['title']}</title>", html)

    # 7. Inject chart blocks BEFORE </body>
    chart_block = CHART_BLOCKS.get(page_key, "")
    html = html.replace("</body>", f"{chart_block}\n</body>")

    # 8. Add .nojekyll marker comment
    html = "<!-- .nojekyll -->\n" + html

    with open(output_path, "w") as f:
        f.write(html)

    print(f"  Built: {output_path} ({len(html)} bytes)")


def main():
    print("Building Hazard Zones website...")
    for key in PAGES:
        build_page(key)

    # Also create .nojekyll file
    with open(".nojekyll", "w") as f:
        f.write("")

    # Create GitHub Pages workflow
    os.makedirs(".github/workflows", exist_ok=True)
    with open(".github/workflows/pages.yml", "w") as f:
        f.write(
            """name: Deploy to GitHub Pages
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
"""
        )
    print("  Created: .github/workflows/pages.yml")
    print("  Created: .nojekyll")
    print("\nBuild complete. 4 pages ready.")


if __name__ == "__main__":
    main()
