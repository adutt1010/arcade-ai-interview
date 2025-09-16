# Arcade AI Interview Challenge – Development Report

## 📝 Overview
The goal of this project was to analyze a `flow.json` file, extract key user interactions, generate a human-friendly summary of user intent, and produce a social-media-ready image that represents the flow.  

Throughout the process I had to balance **generality vs. specificity** and **cost efficiency vs. output quality**, while also making sure the final solution was simple enough to understand and extend.

---

## 🔑 Step-by-Step Thought Process

### 1. Parsing the Flow Data
- I began by loading the JSON and printing out the top-level keys and a sample step to understand the structure.
- I focused on the `steps` array since that’s where most actionable data lived.
- I built a parser to capture:
  - **Chapter titles/subtitles** → gives context.
  - **Hotspots** and **clickContext** → captures actual user interactions.

**Decision:**  
I decided **not** to hardcode handling of specific domains/products (like Target.com). This keeps the parser generalized for any flow.

**Alternative (not chosen):**  
I could have extracted domain/product names explicitly. This would make summaries more specific, but risked breaking generalization on flows without that data.

---

### 2. Summarization
- Once I had a clean list of actions, I needed a **short summary**.  
- I used **GPT-4o-mini** because:
  - It’s much cheaper than GPT-4o.
  - Summarization doesn’t need the full power of GPT-4o to still look polished.
- I structured the prompt to explicitly separate:
  - **Task 1:** Write a professional 2–3 sentence summary.
  - **Task 2:** Write an image generation prompt.

**Decision:**  
I combined both tasks into **one API call** for efficiency.

**Alternative (not chosen):**  
I could have made two separate calls (one for summary, one for image prompt). This would give me finer control but double the API cost.

---

### 3. Image Generation
- I tested prompts in **incognito ChatGPT and DALL·E playground** first before wiring it into the script.  
- This saved API costs by letting me refine prompts manually.
- I discovered that if I told the model *what not to do* (“no text”), it often ignored that. Instead, I refocused the prompts on **positive instructions** (“icons only, pastel palette, flat style”).
- I standardized the design:
  - Flat, minimalist pastel icons.
  - Left-to-right flow with arrows.
  - No text, no logos, no brand names.

**Decision:**  
I switched to **`gpt-image-1`** for consistency and because it integrates more reliably with the OpenAI Python client. This model produced consistent text-free results. `DALL E` image generation seems to not produce satisfactory results when rendering text comes into play. gpt-image-1 follows consistency a lot better.

**Alternative (not chosen):**  
Stick with DALL·E directly. It would have been slightly cheaper, but I found `gpt-image-1` gave cleaner results and fewer surprises.

---

### 4. Local vs. Remote Image Handling
- At first, I only printed the image URL.  
- Then I added support to **save the image locally** (`images/user_flow.png`) so the report could embed it.
- I made the code flexible enough to handle both `b64_json` and `url` outputs from the API.
- Image handling wasted a few API calls, as I took to understanding the differences in output of `DALL E` and `gpt-image-1`. I ended up handling both cases of output.

**Decision:**  
Keep both options in place (local save and URL), defaulting to local save for reproducibility.

**Alternative (not chosen):**  
Only display the URL. This would avoid dependencies like `requests`, but I wanted a guaranteed file I could commit and show in the REPORT.

---

### 5. Markdown Report
- Finally, I built a generator to produce a `REPORT.md` file automatically.  
- It includes:
  - Title (taken from the JSON if available).
  - Summary of user intent.
  - List of actions extracted.
  - Embedded image.

This makes the deliverable **self-contained and shareable**.

---

## ⚖️ Cost vs. Quality Tradeoffs

- **Summarization Model:** Chose `gpt-4o-mini` (lower cost, still high quality).  
- **Image Model:** Chose `gpt-image-1` (more consistent outputs, even if slightly more expensive).  
- **Prompt Testing:** Did manual prompt iteration outside the pipeline first to minimize wasted calls.  

---

## 📌 Lessons & What I Could Do Differently
- **Caching**: Implementing caching was where I wasted the most API generation, debugging it resulted in me wasting a few API calls but overall I believe that I kept API call generation to the minimum.  
- **Could have included video handling** in the parser, but chose to limit scope to chapter and image because video steps may not provide enough information to extract user action.  
- **Could have made the summary more abstract** (avoiding product names), but I decided to keep specifics in Task 1 and stay general in Task 2, which felt like the best balance.

---

## ✅ Final Workflow
1. Parse JSON → extract human-readable actions.  
2. Generate both summary & image prompt in one API call.  
3. Call `gpt-image-1` → generate local image.  
4. Write everything (summary, actions, image) into `REPORT.md`.  

This balances **clarity, cost efficiency, and generalization** while delivering a polished, reusable pipeline.

---

## 🧩 Implementation Notes

- Models: Uses `gpt-4o-mini` for summary/prompt and `gpt-image-1` for image generation.
- Images API: Single `images.generate` call; handles either `b64_json` or `url` in the response (removed unsupported `response_format`). Saves to `images/user_flow.png` and overwrites each run.
- Dimensions: Generates native 1080×1080 square for Instagram-style usage. Margins encouraged via prompt; optional Pillow padding helper exists but is not invoked.
- Parsing Scope: Extracts from `CHAPTER` and `IMAGE` steps using `hotspots[].label` and `clickContext.{text, elementType}`. `VIDEO` steps can be added later if needed.
- Report: Writes `REPORT.md` at repo root on every run (overwrite). Embeds the image if generation succeeded; otherwise omits the image section.
- Console Output: Prints the summary and the image prompt to stdout for visibility while keeping REPORT.md clean.
- Configuration: Loads `OPENAI_API_KEY` from `.env` via `python-dotenv`. Dependencies: `openai`, `requests`, `python-dotenv` (Pillow optional and currently unused).

