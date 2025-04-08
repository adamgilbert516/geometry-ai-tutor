from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import pandas as pd
from dotenv import load_dotenv
from difflib import get_close_matches
import json
import re
import base64
import requests

load_dotenv()
client = OpenAI()
wolfram_app_id = os.getenv("WOLFRAM_APP_ID")
mathpix_app_id = os.getenv("MATHPIX_API_ID")
mathpix_api_key = os.getenv("MATHPIX_API_KEY")

curriculum_df = pd.read_csv("Curriculum Dictionary SY24-25 - Sheet1.csv")
with open("geogebra_links_cleaned_v2.json", "r") as f:
    geogebra_data = json.load(f)

SESSION_MEMORY = {}

app = Flask(__name__)
CORS(app)

def find_best_lesson(question):
    concepts = curriculum_df['Main Concepts'].dropna().tolist()
    match = get_close_matches(question.lower(), concepts, n=1, cutoff=0.5)
    if match:
        row = curriculum_df[curriculum_df['Main Concepts'] == match[0]].iloc[0]
        key = row['Lesson']
        topic = row['Lesson Title']
        links = []
        for col in ['Notes Link', 'Classwork Link', 'Supplement Link']:
            if pd.notna(row.get(col)):
                links.append(f"[{col.split()[0]}]({row[col]})")
        return f"{key} - {topic}\n" + " | ".join(links)
    return ""

def find_geogebra_link(question):
    question_lower = question.lower()
    for entry in geogebra_data:
        keywords = entry.get("Keywords", [])
        if any(keyword.lower() in question_lower for keyword in keywords):
            return entry.get("GeoGebraLink", "")
    return ""

def suggest_wolfram_image(query):
    wolfram_keywords = [
        "unit circle", "trigonometry", "pythagorean", "circle", "volume",
        "area", "cone", "sphere", "triangle", "perimeter", "angles", "tangent"
    ]
    if any(keyword in query.lower() for keyword in wolfram_keywords):
        query_param = re.sub(r'\s+', '+', query.strip())
        return f"https://api.wolframalpha.com/v1/simple?appid={wolfram_app_id}&i={query_param}"
    return ""

def extract_mathpix_text(image_file):
    try:
        image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
        headers = {
            "app_id": mathpix_app_id,
            "app_key": mathpix_api_key,
            "Content-type": "application/json"
        }
        payload = {
            "src": f"data:image/jpg;base64,{image_base64}",
            "formats": ["text", "data"],
            "ocr": ["math", "text"],
            "math_inline_delimiters": ["$", "$"]
        }
        res = requests.post("https://api.mathpix.com/v3/text", json=payload, headers=headers)
        data = res.json()
        return data.get("text", "").strip()
    except Exception as e:
        print("MathPix error:", e)
        return ""

def sanitize_latex_markdown(text):
    import html
    text = html.unescape(text)

    # Convert \(...\) and \[...\] to $...$ and $$...$$
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text)
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text)

    # Replace [ a^2 + b^2 = c^2 ] with $a^2 + b^2 = c^2$
    text = re.sub(r'\[\s*([^\[\]]+?)\s*\]', r'$\1$', text)

    # Process only math spans to avoid touching regular text
    def fix_functions_in_math(match):
        expr = match.group(1)
        expr = re.sub(r'([a-zA-Z])\(([^()]+?)\)', r'\1\\left(\2\\right)', expr)
        return f"${expr}$"

    text = re.sub(r'\$(.+?)\$', fix_functions_in_math, text)

    def fix_block_math(m):
        expr = m.group(1).strip()
        expr = re.sub(r'([a-zA-Z])\(([^()]+?)\)', r'\1\\left(\2\\right)', expr)
        return f"$$\n{expr}\n$$"

    text = re.sub(r'\$\$(.+?)\$\$', fix_block_math, text, flags=re.DOTALL)

    return text




@app.route("/api/ask", methods=["POST"])
def ask():
    question = request.form.get("question", "").strip()
    session_id = request.form.get("session_id", "default")
    image_file = request.files.get("image")

    if not question and not image_file:
        return jsonify({"response": {"gpt": "Please enter a question or upload an image."}})

    if session_id not in SESSION_MEMORY:
        SESSION_MEMORY[session_id] = []

    previous_turns = SESSION_MEMORY[session_id][-4:]
    chat_history = []
    for pair in previous_turns:
        chat_history.append({"role": "user", "content": pair["question"]})
        chat_history.append({"role": "assistant", "content": pair["response"]})

    image_text = extract_mathpix_text(image_file) if image_file else ""
    full_question = f"{question}\n\nExtracted from screenshot:\n{image_text}" if image_text else question

    lesson_ref = find_best_lesson(full_question)
    geogebra_link = find_geogebra_link(full_question)
    wolfram_img = suggest_wolfram_image(full_question)

    lesson_line = f"\n\nSuggested resource:\n{lesson_ref}" if lesson_ref else "\n\nCheck your notes. Hopefully your binder is organized! If not, you can find everything on Canvas."
    visual_line = ""
    if wolfram_img:
        visual_line += f"\n\n![Wolfram Visual]({wolfram_img})"
    elif geogebra_link:
        visual_line += f"\n\nGeoGebraID: {geogebra_link}"

    system_prompt = f"""
You are a helpful geometry tutor.

NEVER give the student the final answer. Instead, follow this structure strictly:
1. Always start with a guiding question to prompt thinking.
2. If the student already asked this before, you may give a slightly stronger hint.
3. If the question is too vague, say: "Please ask a more specific question so that I can help you better."
4. If appropriate, recommend a specific topic like this:{lesson_line}
5. If you want to suggest a visual, include the full GeoGebra link like this or a WolframAlpha image like this:{visual_line}
6. If students ask for formulas, definitions, or theorems, you may prompt their thinking first, but eventually you may provide this information.
7. If they present a problem to solve, ask them to show a screenshot of their work so far to help move them forward. Give guidance only.

Use LaTeX for math, using `$...$` for inline expressions and `$$...$$` for block expressions. For example:

Inline: $a^2 + b^2 = c^2$  
Block:

$$
a^2 + b^2 = c^2
$$


Write raw Markdown with LaTeX syntax — the frontend will handle rendering.
Never solve full problems. Only give nudges to guide their thinking.
"""

    messages = [{"role": "system", "content": system_prompt}] + chat_history + [{"role": "user", "content": full_question}]
    response = client.chat.completions.create(model="gpt-4o", messages=messages)
    try:
        raw_text = response.choices[0].message.content.strip()
        print("RAW GPT RESPONSE:\n", raw_text)
        gpt_text = sanitize_latex_markdown(raw_text) or "Sorry, I wasn't able to generate a response."
    except Exception as e:
        print("Error processing GPT response:", e)
        gpt_text = "Sorry, something went wrong while formatting the AI response."



    SESSION_MEMORY[session_id].append({"question": question, "response": gpt_text})
    return jsonify({"response": {"gpt": gpt_text}})

if __name__ == "__main__":
    app.run(debug=True, port=5051, host="0.0.0.0")

