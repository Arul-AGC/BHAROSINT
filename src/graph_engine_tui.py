import math
from typing import Dict, List, Tuple
import networkx as nx

try:
    from textual.app import App, ComposeResult
    from textual.widgets import Header, Footer, Static
    from textual.containers import ScrollableContainer
    from textual.geometry import Size
    from rich.text import Text
    from rich.style import Style
    TEXTUAL_ERR = None
except ImportError as e:
    TEXTUAL_ERR = e

# Canvas dimensions
CANVAS_WIDTH = 250
CANVAS_HEIGHT = 100

def draw_line(canvas: List[List[str]], color_canvas: List[List[str]], x0: int, y0: int, x1: int, y1: int, color: str = "white"):
    """Bresenham's Line Algorithm for terminal characters."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    
    while True:
        if 0 <= x0 < CANVAS_WIDTH and 0 <= y0 < CANVAS_HEIGHT:
            if canvas[y0][x0] == " ":
                # Choose line character based on slope
                if dx == 0: char = "|"
                elif dy == 0: char = "-"
                elif (sx > 0 and sy > 0) or (sx < 0 and sy < 0): char = "\\"
                else: char = "/"
                canvas[y0][x0] = char
                color_canvas[y0][x0] = color

        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy

class GraphCanvasWidget(Static):
    """A widget that renders the precomputed 2D text canvas."""
    def __init__(self, text_content: Text):
        super().__init__()
        self.text_content = text_content

    def render(self) -> Text:
        return self.text_content
        
    def get_content_width(self, container: Size, viewport: Size) -> int:
        return CANVAS_WIDTH

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return CANVAS_HEIGHT

class ThreatMapApp(App):
    """Textual App to display the Threat Map."""
    CSS = """
    Screen {
        background: $surface;
    }
    ScrollableContainer {
        width: 100%;
        height: 100%;
        scrollbar-size: 1 1;
    }
    GraphCanvasWidget {
        width: auto;
        height: auto;
    }
    """
    BINDINGS = [
        ("q", "quit", "Quit Map"),
        ("up", "scroll_up", "Pan Up"),
        ("down", "scroll_down", "Pan Down"),
        ("left", "scroll_left", "Pan Left"),
        ("right", "scroll_right", "Pan Right")
    ]

    def __init__(self, nlp_analysis: Dict, query: str = "TARGET"):
        super().__init__()
        self.nlp_analysis = nlp_analysis
        self.query = query
        self.rendered_text = Text()

    def _build_graph(self) -> nx.Graph:
        G = nx.Graph()
        G.add_node(self.query, type="TARGET")

        # Combine items
        entities = self.nlp_analysis.get("entities", {})
        threats = self.nlp_analysis.get("threat", {})
        keywords = self.nlp_analysis.get("keywords", [])[:10] # limit keywords

        def add_nodes(items, ntype):
            for item in items:
                if item:
                    # Clean newline chars which break rendering
                    clean_item = str(item).replace("\n", "").replace("\r", "")
                    if clean_item not in G:
                        G.add_node(clean_item, type=ntype)
                        G.add_edge(self.query, clean_item)

        if "persons" in entities: add_nodes(entities["persons"], "PERSON")
        if "organizations" in entities: add_nodes(entities["organizations"], "ORG")
        if "locations" in entities: add_nodes(entities["locations"], "LOC")
        if "IP Addresses" in entities: add_nodes(entities["IP Addresses"], "IP")
        if "threat_terms" in threats: add_nodes(threats["threat_terms"], "THREAT")
        add_nodes(keywords, "KEYWORD")

        return G

    def on_mount(self) -> None:
        G = self._build_graph()
        
        if len(G.nodes) <= 1:
            self.rendered_text = Text("Not enough data to generate a Threat Map.", style="bold red")
            return

        # 1. Physics layout
        pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
        
        # 2. Scale to canvas
        # pos values are [-1, 1], we map to [5..WIDTH-5, 5..HEIGHT-5]
        scaled_pos = {}
        for node, (x, y) in pos.items():
            # Invert y because terminal y goes down
            sx = int(((x + 1) / 2) * (CANVAS_WIDTH - 20) + 10)
            sy = int(((-y + 1) / 2) * (CANVAS_HEIGHT - 10) + 5)
            # Clamp bounds safely
            sx = max(0, min(CANVAS_WIDTH - 1, sx))
            sy = max(0, min(CANVAS_HEIGHT - 1, sy))
            scaled_pos[node] = (sx, sy)

        # 3. Render setup
        canvas = [[" " for _ in range(CANVAS_WIDTH)] for _ in range(CANVAS_HEIGHT)]
        color_canvas = [[" " for _ in range(CANVAS_WIDTH)] for _ in range(CANVAS_HEIGHT)]

        # 4. Draw edges
        for u, v in G.edges():
            x0, y0 = scaled_pos[u]
            x1, y1 = scaled_pos[v]
            draw_line(canvas, color_canvas, x0, y0, x1, y1, color="grey37")

        # 5. Draw nodes (labels)
        for node, attr in G.nodes(data=True):
            node_x, node_y = scaled_pos[node]
            ntype = attr.get("type", "UNKNOWN")
            
            # Label styling
            if ntype == "TARGET": color = "bold red"
            elif ntype == "PERSON": color = "cyan"
            elif ntype == "ORG": color = "magenta"
            elif ntype == "LOC": color = "green"
            elif ntype == "IP": color = "yellow"
            elif ntype == "THREAT": color = "bright_red"
            else: color = "white"

            label = f"[{node}]"
            start_x = node_x - len(label) // 2
            
            # Draw label characters
            for i, char in enumerate(label):
                cx = start_x + i
                if 0 <= cx < CANVAS_WIDTH and 0 <= node_y < CANVAS_HEIGHT:
                    canvas[node_y][cx] = char
                    color_canvas[node_y][cx] = color

        # 6. Convert 2D arrays to Rich Text
        rich_text = Text()
        for y in range(CANVAS_HEIGHT):
            current_style = None
            chunk = ""
            for x in range(CANVAS_WIDTH):
                c = canvas[y][x]
                col = color_canvas[y][x]
                
                # If color changes, append chunk and start new
                if col != current_style:
                    if chunk:
                        if current_style and current_style != " ":
                            rich_text.append(chunk, style=current_style)
                        else:
                            rich_text.append(chunk)
                    chunk = c
                    current_style = col
                else:
                    chunk += c
            
            if chunk:
                if current_style and current_style != " ":
                    rich_text.append(chunk, style=current_style)
                else:
                    rich_text.append(chunk)
            rich_text.append("\n")

        self.rendered_text = rich_text

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="canvas_scroll"):
            yield GraphCanvasWidget(self.rendered_text)
        yield Footer()

def display_interactive_map(analysis_data: Dict, query: str):
    if TEXTUAL_ERR:
        print(f"[!] Cannot open Threat Map. Missing dependencies: {TEXTUAL_ERR}")
        print("    Run: pip install networkx textual")
        return

    app = ThreatMapApp(nlp_analysis=analysis_data, query=query)
    app.run()
