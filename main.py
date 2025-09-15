import json

with open("flow.json","r") as f:
    data = json.load(f)

print("Type:", type(data))
print("Keys:", data.keys())

print("\nNumber of steps: ", len(data.get("steps",[])))
print("First step example:\n", json.dumps(data['steps'][0], indent=2)[:500])

actions  = []

for step in data.get("steps",[]):
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


# Display extracted actions
print("\n Extracted Actions:")
for i,action in enumerate(actions,1):
    print(f"{i}. {action}")


# test to see if .env was not committed