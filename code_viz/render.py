"""HTML rendering for code visualization."""

from __future__ import annotations

import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
from typing import Any

from jinja2 import Template

# HTML template with D3.js force-directed graph
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Viz - {{ root_name }}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu,
                sans-serif;
            background: #1a1a2e;
            color: #eee;
            overflow: hidden;
        }

        #header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }

        #header h1 {
            font-size: 20px;
            font-weight: 600;
            color: #e94560;
        }
        
        #stats {
            display: flex;
            gap: 20px;
            font-size: 14px;
        }
        
        .stat {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .stat-value {
            font-weight: bold;
            color: #e94560;
        }
        
        .stat-label {
            font-size: 12px;
            opacity: 0.8;
        }
        
        #controls {
            position: fixed;
            top: 80px;
            right: 20px;
            background: rgba(22, 33, 62, 0.9);
            padding: 15px;
            border-radius: 8px;
            z-index: 100;
            backdrop-filter: blur(10px);
        }
        
        #controls label {
            display: block;
            margin-bottom: 5px;
            font-size: 12px;
        }
        
        #controls input[type="range"] {
            width: 150px;
            margin-bottom: 10px;
        }
        
        #controls button {
            background: #e94560;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin-bottom: 5px;
            width: 100%;
        }
        
        #controls button:hover {
            background: #ff6b6b;
        }
        
        #graph {
            width: 100vw;
            height: 100vh;
            padding-top: 60px;
        }
        
        #tooltip {
            position: fixed;
            background: rgba(22, 33, 62, 0.95);
            color: #eee;
            padding: 12px;
            border-radius: 6px;
            font-size: 13px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            max-width: 300px;
            border: 1px solid #e94560;
            z-index: 2000;
        }
        
        #tooltip.visible {
            opacity: 1;
        }
        
        #tooltip h3 {
            color: #e94560;
            margin-bottom: 8px;
            font-size: 14px;
            word-break: break-all;
        }
        
        #tooltip p {
            margin: 4px 0;
            line-height: 1.4;
        }
        
        #tooltip .tag {
            display: inline-block;
            background: #0f3460;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
            margin: 2px;
        }
        
        .node {
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .node:hover {
            filter: brightness(1.3);
        }
        
        .link {
            stroke-opacity: 0.6;
            transition: all 0.3s ease;
        }
        
        .node-label {
            font-size: 11px;
            fill: #ccc;
            pointer-events: none;
            text-shadow: 0 1px 3px rgba(0,0,0,0.8);
        }
        
        .legend {
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: rgba(22, 33, 62, 0.9);
            padding: 15px;
            border-radius: 8px;
            font-size: 12px;
            backdrop-filter: blur(10px);
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            margin: 5px 0;
        }
        
        .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        #search {
            position: fixed;
            top: 80px;
            left: 20px;
            z-index: 100;
        }
        
        #search input {
            background: rgba(22, 33, 62, 0.9);
            border: 1px solid #0f3460;
            color: #eee;
            padding: 8px 12px;
            border-radius: 4px;
            width: 200px;
            font-size: 13px;
        }
        
        #search input:focus {
            outline: none;
            border-color: #e94560;
        }
    </style>
</head>
<body>
    <div id="header">
        <h1>🔍 Code Viz: {{ root_name }}</h1>
        <div id="stats">
            <div class="stat">
                <span class="stat-value">{{ stats.total_modules }}</span>
                <span class="stat-label">Modules</span>
            </div>
            <div class="stat">
                <span class="stat-value">{{ stats.total_dependencies }}</span>
                <span class="stat-label">Dependencies</span>
            </div>
            <div class="stat">
                <span class="stat-value">{{ "%.1f"|format(stats.avg_degree) }}</span>
                <span class="stat-label">Avg Connections</span>
            </div>
        </div>
    </div>
    
    <div id="search">
        <input type="text" id="searchInput" placeholder="Search module..." autocomplete="off">
    </div>
    
    <div id="controls">
        <label>Charge Strength: <span id="chargeValue">-300</span></label>
        <input type="range" id="chargeSlider" min="-1000" max="-50" value="-300">
        
        <label>Link Distance: <span id="distanceValue">100</span></label>
        <input type="range" id="distanceSlider" min="30" max="300" value="100">
        
        <button id="resetBtn">Reset View</button>
        <button id="toggleLabelsBtn">Toggle Labels</button>
        <button id="exportBtn">Export PNG</button>
    </div>
    
    <div id="graph"></div>
    
    <div id="tooltip"></div>
    
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background: #e94560;"></div>
            <span>High Activity (>10 connections)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #0f3460;"></div>
            <span>Medium Activity (5-10)</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #533483;"></div>
            <span>Low Activity (<5)</span>
        </div>
    </div>

    <script>
        const graphData = {{ data | tojson }};
        
        const width = window.innerWidth;
        const height = window.innerHeight - 60;
        
        const svg = d3.select("#graph")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", [0, 0, width, height]);
        
        // Add zoom behavior
        const g = svg.append("g");
        
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {
                g.attr("transform", event.transform);
            });
        
        svg.call(zoom);
        
        // Color scale based on connections
        const colorScale = d3.scaleThreshold()
            .domain([5, 10])
            .range(["#533483", "#0f3460", "#e94560"]);
        
        // Size scale based on lines of code
        const sizeScale = d3.scaleSqrt()
            .domain([0, d3.max(graphData.nodes, d => d.line_count) || 100])
            .range([3, 20]);
        
        // Create simulation
        const simulation = d3.forceSimulation(graphData.nodes)
            .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(d => sizeScale(d.line_count) + 5));
        
        // Create links
        const link = g.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(graphData.links)
            .join("line")
            .attr("class", "link")
            .attr("stroke", "#4a5568")
            .attr("stroke-width", d => Math.sqrt(d.weight));
        
        // Create nodes
        const node = g.append("g")
            .attr("class", "nodes")
            .selectAll("circle")
            .data(graphData.nodes)
            .join("circle")
            .attr("class", "node")
            .attr("r", d => sizeScale(d.line_count))
            .attr("fill", d => colorScale(d.degree))
            .attr("stroke", "#fff")
            .attr("stroke-width", 1.5)
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        // Create labels
        const labels = g.append("g")
            .attr("class", "labels")
            .selectAll("text")
            .data(graphData.nodes)
            .join("text")
            .attr("class", "node-label")
            .attr("dx", d => sizeScale(d.line_count) + 5)
            .attr("dy", ".35em")
            .text(d => d.id.split('.').pop())
            .style("opacity", d => d.degree > 3 ? 1 : 0.7);
        
        // Tooltip
        const tooltip = d3.select("#tooltip");
        
        node.on("mouseover", (event, d) => {
            const classes = d.classes.slice(0, 5).map(c => `<span class="tag">class: ${c}</span>`).join('');
            const functions = d.functions.slice(0, 5).map(f => `<span class="tag">fn: ${f}</span>`).join('');
            
            tooltip.html(`
                <h3>${d.id}</h3>
                <p><strong>Path:</strong> ${d.path}</p>
                <p><strong>Lines:</strong> ${d.line_count}</p>
                <p><strong>Connections:</strong> ${d.degree} (in: ${d.in_degree}, out: ${d.out_degree})</p>
                ${classes ? `<p>${classes}${d.classes.length > 5 ? ' ...' : ''}</p>` : ''}
                ${functions ? `<p>${functions}${d.functions.length > 5 ? ' ...' : ''}</p>` : ''}
            `);
            
            tooltip
                .style("left", (event.clientX + 15) + "px")
                .style("top", (event.clientY - 15) + "px")
                .classed("visible", true);
        })
        .on("mouseout", () => {
            tooltip.classed("visible", false);
        });
        
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            if (term.length < 2) {
                node.attr("opacity", 1);
                link.attr("opacity", 0.6);
                return;
            }
            
            const matched = graphData.nodes.filter(n => 
                n.id.toLowerCase().includes(term) || 
                n.path.toLowerCase().includes(term)
            );
            const matchedIds = new Set(matched.map(n => n.id));
            
            node.attr("opacity", d => matchedIds.has(d.id) ? 1 : 0.1);
            link.attr("opacity", d => // noqa: E501
                matchedIds.has(d.source.id || d.source) && matchedIds.has(d.target.id || d.target) ? 0.6 : 0.05
            );
        });
        
        // Controls
        document.getElementById('chargeSlider').addEventListener('input', (e) => {
            const val = +e.target.value;
            document.getElementById('chargeValue').textContent = val;
            simulation.force("charge").strength(val);
            simulation.alpha(0.3).restart();
        });
        
        document.getElementById('distanceSlider').addEventListener('input', (e) => {
            const val = +e.target.value;
            document.getElementById('distanceValue').textContent = val;
            simulation.force("link").distance(val);
            simulation.alpha(0.3).restart();
        });
        
        document.getElementById('resetBtn').addEventListener('click', () => {
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity
            );
            simulation.alpha(1).restart();
        });
        
        let labelsVisible = true;
        document.getElementById('toggleLabelsBtn').addEventListener('click', () => {
            labelsVisible = !labelsVisible;
            labels.transition().style("opacity", labelsVisible ? d => d.degree > 3 ? 1 : 0.7 : 0);
        });
        
        document.getElementById('exportBtn').addEventListener('click', () => {
            const svgEl = document.querySelector('svg');
            const svgData = new XMLSerializer().serializeToString(svgEl);
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            canvas.width = width;
            canvas.height = height;
            
            img.onload = () => {
                ctx.fillStyle = '#1a1a2e';
                ctx.fillRect(0, 0, width, height);
                ctx.drawImage(img, 0, 0);
                const pngFile = canvas.toDataURL('image/png');
                const downloadLink = document.createElement('a');
                downloadLink.download = 'code-viz.png';
                downloadLink.href = pngFile;
                downloadLink.click();
            };
            
            img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
        });
        
        // Simulation tick
        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
            
            labels
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        });
        
        // Drag functions
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        
        // Handle window resize
        window.addEventListener('resize', () => {
            const newWidth = window.innerWidth;
            const newHeight = window.innerHeight - 60;
            svg.attr("width", newWidth).attr("height", newHeight);
            simulation.force("center", d3.forceCenter(newWidth / 2, newHeight / 2));
            simulation.alpha(0.3).restart();
        });
    </script>
</body>
</html>
'''


class GraphRenderer:
    """Renders code dependency graph as interactive HTML."""

    def __init__(self, output_dir: Path | str | None = None) -> None:
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def render(
        self,
        data: dict[str, Any],
        filename: str = "code-viz.html",
        auto_open: bool = True,
    ) -> Path:
        """Render graph data to HTML file."""
        template = Template(HTML_TEMPLATE)

        root_name = Path(data.get("root_path", "project")).name

        html_content = template.render(
            data=data,
            root_name=root_name,
            stats=data.get("stats", {}),
        )

        output_path = self.output_dir / filename
        output_path.write_text(html_content, encoding="utf-8")

        if auto_open:
            webbrowser.open(f"file://{output_path.resolve()}")

        return output_path

    def serve(
        self,
        data: dict[str, Any],
        port: int = 8080,
        auto_open: bool = True,
    ) -> HTTPServer:
        """Start HTTP server with live visualization."""
        output_path = self.render(data, "code-viz-live.html", auto_open=False)

        class VizHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                super().__init__(*args, directory=str(output_path.parent), **kwargs)

            def log_message(self, format: str, *args: Any) -> None:
                pass  # Suppress logs

        server = HTTPServer(("localhost", port), VizHandler)

        def run_server() -> None:
            server.serve_forever()

        thread = Thread(target=run_server, daemon=True)
        thread.start()

        if auto_open:
            webbrowser.open(f"http://localhost:{port}/{output_path.name}")

        return server
