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
CORS(app, resources={r"/api/*": {"origins": "http://localhost:*"}})


def find_best_lesson(question):
    concepts = curriculum_df['Main Concepts'].dropna().tolist()
    match = get_close_matches(question.lower(), concepts, n=1, cutoff=0.5)
    if match:
        row = curriculum_df[curriculum_df['Main Concepts'] == match[0]].iloc[0]
        return row['Lesson Title']
    return ""


def find_geogebra_link(question):
    question_lower = question.lower()
    for entry in geogebra_data:
        keywords = entry.get("Keywords", [])
        if any(keyword.lower() in question_lower for keyword in keywords):
            return entry.get("GeoGebraLink", "")
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


def extract_best_wolfram_keyword(text):
    try:
        messages = [
            {
                "role": "system",
                "content": "Extract a single math keyword or concept from the following question or statement. Return just one keyword like 'pythagorean theorem', 'volume', 'euler formula'. If nothing meaningful is found, return 'none'."
            },
            {"role": "user", "content": text}
        ]
        result = client.chat.completions.create(model="gpt-4o", messages=messages)
        keyword = result.choices[0].message.content.strip().lower()
        if keyword in ["", "none", "nothing", "n/a"]:
            return ""
        return keyword.replace(" ", "+")
    except Exception as e:
        print("Keyword extraction error:", e)
        return ""


def suggest_wolfram_link(query, image_text):
    if image_text.strip():  # Avoid suggesting if the question came from an image
        return ""
    keyword = extract_best_wolfram_keyword(query)
    if keyword:
        return f"https://www.wolframalpha.com/input?i={keyword}"
    return ""


def should_suggest_wolfram(text):
    return "wolfram" in text.lower() or "wolfram link" in text.lower()


def sanitize_latex_markdown(text):
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text)
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text)
    text = re.sub(r'\[\s*([^\[\]]+?)\s*\]', r'$\1$', text)
    text = re.sub(r'\(\s*([a-zA-Z0-9^]+)\s*\)', r'\1', text)
    text = re.sub(r'(?<!\$)(\b[a-zA-Z])\(([^)]+)\)(?!\$)', r'$\1(\2)$', text)
    text = re.sub(r'(?<!\\)([a-zA-Z])\(([^)]+)\)', r'\1\\left(\2\\right)', text)
    block_math_matches = re.findall(r'\$\$.*?\$\$', text, re.DOTALL)
    for block in block_math_matches:
        if block.count('$$') != 2:
            text = text.replace(block, '')
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
    wolfram_link = suggest_wolfram_link(question, image_text) if should_suggest_wolfram(question) else ""

    lesson_line = f"\n\nSuggested resource:\n{lesson_ref}" if lesson_ref else ""
    visual_line = ""
    if geogebra_link:
        visual_line += f"\n\nGeoGebraID: {geogebra_link}"
    elif wolfram_link:
        visual_line += f"\n\nWolframURL: {wolfram_link}"

    system_prompt = f"""
You are a helpful geometry tutor, named Mr. Gilbot.

NEVER give the student the final answer. Instead, follow this structure strictly:
1. Always start with a guiding question to prompt thinking.
2. If the student already asked this before, you may give a slightly stronger hint.
3. If the question is too vague, say: "Please ask a more specific question so that I can help you better."
4. If appropriate, recommend a specific topic like this:{lesson_line}
5. If you want to suggest a visual, include the full GeoGebra link like this or a WolframAlpha link like this:{visual_line}
6. If students ask for formulas, definitions, or theorems, you may prompt their thinking first, but eventually you may provide this information.
7. If they present a problem to solve, ask them to show a screenshot of their work so far to help move them forward. Give guidance only.

Use LaTeX for math, using $...$ for inline expressions and $$...$$ for block expressions.

Write raw Markdown with LaTeX syntax — the frontend will handle rendering.
Never solve full problems. Only give nudges to guide their thinking.
"""

    messages = [{"role": "system", "content": system_prompt}] + chat_history + [{"role": "user", "content": full_question}]
    response = client.chat.completions.create(model="gpt-4o", messages=messages)

    raw_text = response.choices[0].message.content.strip()
    gpt_text = sanitize_latex_markdown(raw_text)

    if not geogebra_link and wolfram_link:
    # Remove hallucinated link labels like [Text](Wolfram link) or WolframAlpha:Label(...)
        gpt_text = re.sub(r"\[.*?\]\((https?:\/\/www\.wolframalpha\.com[^\s)]+)\)", "", gpt_text)
        gpt_text = re.sub(r"WolframAlpha[:\-\w\s]*\((https?:\/\/www\.wolframalpha\.com[^\)]+)\)", "", gpt_text)

        # Remove standalone raw link text like just (https://...)
        gpt_text = re.sub(r"\(https?:\/\/www\.wolframalpha\.com[^\)]+\)", "", gpt_text)

        # Finally, add one clean, clear link to the end
        gpt_text += f"\n\n[Here is an explanation from Wolfram Alpha]({wolfram_link})"



    SESSION_MEMORY[session_id].append({"question": question, "response": gpt_text})
    return jsonify({"response": {"gpt": gpt_text}})


if __name__ == "__main__":
    app.run(debug=True, port=5051, host="0.0.0.0")
