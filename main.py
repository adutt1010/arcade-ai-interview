import json
from openai import OpenAI
import os
from dotenv import load_dotenv
# from urllib.parse import urlparse

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

image_prompt = "Minimalist Image" + image_prompt


print("\nSummary:\n",summary)

print("\nImage Prompt:\n",image_prompt)
