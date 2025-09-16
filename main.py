import json
from openai import OpenAI
import os
from dotenv import load_dotenv
import requests
from pathlib import Path
import base64
# from urllib.parse import urlparse

from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("flow.json","r") as f:
    data = json.load(f)


actions  = []

steps = data.get("steps",[])


for step in steps:
    step_type = step.get("type", "")

# Handling chapter steps
    if step_type == "CHAPTER":
        title = step.get("title")
        subtitle = step.get("subtitle")
        if title:
            actions.append(f"Chapter: {title}")
        if subtitle:
            actions.append(f"   {subtitle}")
        
# Handling text input steps
    elif step_type == "IMAGE":

        for hotspot in step.get("hotspots",[]):
            actions.append(hotspot.get("label","Interacted with image"))

    # Handling clicked elements
        if "clickContext" in step:
            text = step["clickContext"].get("text")
            element = step["clickContext"].get("elementType","element")
            if text:
                actions.append(f"Clicked on {text} ({element})")
            else:
                actions.append(f"Clicked on {element}")



def generate_summary_and_prompt(actions):

    prompt = (
        "Here is a list of user actions:\n" +
        "\n".join(actions) +
        "\n\nPlease respond in the following exact format:\n\n"
        "Task 1: [Write a professional 2–3 sentence summary of what the user was trying to accomplish. "
        "Be specific if websites or products are mentioned.]\n\n"
        "Task 2: [Write a short DALL·E image prompt that visually represents this sequence as icons "
        "arranged in a left-to-right flow with arrows. Each action should map to an abstract icon "
        "(e.g., magnifying glass for search, grid of thumbnails for browsing, color swatches for choosing options, "
        "shopping cart for adding to cart, shield with an X for declining coverage, clipboard with checkmarks for reviewing order). "
        "Use flat, minimalist pastel icons, no text or labels.]"
    )

    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        temperature=0.3,
        messages = [{
            "role": "user",
            "content": prompt
        }]
    )

    return response.choices[0].message.content

def save_image_bytes(content: bytes, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(content)
    return out_path

def generate_and_save_image(prompt: str, out_path: Path) -> Path:
    if not prompt or len(prompt) < 10:
        raise ValueError("Image prompt looks empty/too short.")

    # Single call; handle either b64_json or url from the SDK
    resp = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
        n=1,
    )

    item = resp.data[0]
    b64 = getattr(item, "b64_json", None)
    url = getattr(item, "url", None)

    if b64:
        raw = base64.b64decode(b64)
        return save_image_bytes(raw, out_path)

    if url:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return save_image_bytes(r.content, out_path)

    raise RuntimeError("Images API did not return b64_json or url.")

output = generate_summary_and_prompt(actions)
summary = ""
image_prompt = ""

if "Task 1:" in output and "Task 2:" in output:
    parts = output.split("Task 2:")
    summary = parts[0].replace("Task 1:","").strip()
    image_prompt = parts[1].strip()
else:
    summary = output
    image_prompt = "Flat icons representing the user flow"

image_prompt = (
    "Square 1:1 canvas, vivid saturated colors, high contrast, "
    "generous safe margins, centered composition, no text. "
    + image_prompt
)





# print("\nSummary:\n",summary)

# print("\nImage Prompt:\n",image_prompt)

try:
    output_path = Path("images/user_flow.png")
    saved_path = generate_and_save_image(image_prompt, output_path)
    print(f"Image saved to {saved_path.resolve()}")
    try:
        if os.name == 'nt':  
            os.startfile(saved_path)
    except Exception:
        pass
except Exception as e:
    print(f"Image generation failed: {e}")
    saved_path = None

def build_markdown_report(flow_title: str, summary_text: str, actions_list: list[str], image_rel_path: str | None) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    title = flow_title or "Arcade Flow Report"
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"Generated: {ts}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(summary_text.strip() if summary_text else "(No summary)")
    lines.append("")
    lines.append("## Actions")
    lines.append("")
    if actions_list:
        for a in actions_list:
            lines.append(f"- {a}")
    else:
        lines.append("- (No actions extracted)")
    lines.append("")
    if image_rel_path:
        lines.append("## Social Image")
        lines.append("")
        lines.append(f"![Flow Social Image]({image_rel_path})")
        lines.append("")
    return "\n".join(lines)

# Choose a flow title from JSON data
flow_title = data.get("name")
if not flow_title:
    for s in steps:
        if s.get("type") == "CHAPTER" and s.get("title"):
            flow_title = s.get("title")
            break
if not flow_title:
    flow_title = "Arcade Flow Report"

# Build and write REPORT.md (overwrite each run)
report_md = build_markdown_report(
    flow_title=flow_title,
    summary_text=summary,
    actions_list=actions,
    image_rel_path=(str(Path("images/user_flow.png")) if 'saved_path' in locals() and saved_path else None),
)
Path("REPORT.md").write_text(report_md, encoding="utf-8")
# print("Wrote REPORT.md")
