from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import pandas as pd
from dotenv import load_dotenv
from difflib import get_close_matches
import base64
import requests
import re
from difflib import get_close_matches

load_dotenv()
client = OpenAI()
mathpix_app_id = os.getenv("MATHPIX_API_ID")
mathpix_api_key = os.getenv("MATHPIX_API_KEY")

curriculum_df = pd.read_csv("Curriculum Dictionary SY24-25 - Sheet1.csv")
geogebra_df = pd.read_csv("geogebra_materials.csv")

SESSION_MEMORY = {}
TOPIC_MEMORY = {}

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


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
        return res.json().get("text", "").strip()
    except Exception as e:
        print("MathPix error:", e)
        return ""


def sanitize_latex_markdown(text):
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text)
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text)
    text = re.sub(r'\[\s*([^\[\]]+?)\s*\]', r'$\1$', text)
    text = re.sub(r'\(\s*([a-zA-Z0-9^]+)\s*\)', r'\1', text)
    text = re.sub(r'(?<!\$)(\b[a-zA-Z])\(([^)]+)\)(?!\$)', r'$\1(\2)$', text)
    text = re.sub(r'(?<!\\)([a-zA-Z])\(([^)]+)\)', r'\1\\left(\2\\right)', text)
    return text

def fuzzy_keyword_match(keyword, keyword_list):
    if not keyword:
        print(f"⚠️ No keyword extracted for {context}.")
        return "", False
    matches = get_close_matches(keyword, keyword_list, n=1, cutoff=0.6)
    return matches[0] if matches else ""

def extract_best_keyword(prompt, context, session_id, image_text=""):
    try:
        combined_input = f"User question: {prompt}"
        if image_text:
            combined_input += f"\n\nMathPix OCR from image:\n{image_text}"

        messages = [
            {
                "role": "system",
                "content": f"Extract a single keyword or short phrase from this input that is useful for {context}. Return only one math keyword like 'trigonometry', 'angle bisector', or 'triangle similarity'. If nothing helpful is found, return 'none'."
            },
            {"role": "user", "content": combined_input}
        ]
        result = client.chat.completions.create(model="gpt-4o", messages=messages)
        keyword = result.choices[0].message.content.strip().lower()
        print(f"⚠️ GPT returned invalid keyword for {context}: '{keyword}'")
        if keyword in ["none", "n/a", ""]:
            print(f"⚠️ GPT returned invalid keyword for {context}: '{keyword}'")

            return TOPIC_MEMORY.get(session_id, "")
        else:
            print(f"📌 Stored keyword for [{context}]: {keyword}")
            TOPIC_MEMORY[session_id] = keyword
            return keyword
    except Exception as e:
        print(f"{context} keyword extraction error:", e)
        return TOPIC_MEMORY.get(session_id, "")



def find_best_lesson(prompt, session_id, image_text):
    keyword = extract_best_keyword(prompt, "lesson lookup", session_id, image_text)
    
    if not keyword:
        print("⚠️ No keyword extracted for lesson lookup.")
        return "", False

    all_keywords = curriculum_df['Keywords'].dropna().str.lower().tolist()
    best_match = fuzzy_keyword_match(keyword, all_keywords)
    print(f"🔎 Extracted lesson keyword: {keyword} → Matched: {best_match}")

    try:
        matched = curriculum_df[curriculum_df['Keywords'].fillna("").str.lower().str.contains(best_match)]
        if not matched.empty:
            lesson = matched.iloc[0]['Lesson Title']
            print(f"✅ Matched lesson: {lesson}")
            return lesson, True
    except Exception as e:
        print("Lesson match error:", e)

    return "", False


def find_geogebra_link(prompt, session_id, image_text):
    keyword = extract_best_keyword(prompt, "geogebra material search", session_id, image_text)
    all_keywords = geogebra_df['Keywords'].dropna().str.lower().tolist()
    best_match = fuzzy_keyword_match(keyword, all_keywords)

    print(f"🔍 Extracted GeoGebra keyword: {keyword} → Matched: {best_match}")

    try:
        matched = geogebra_df[geogebra_df['Keywords'].str.lower().str.contains(best_match)]
        if not matched.empty:
            material_id = matched.iloc[0]['MaterialID']
            url = f"https://www.geogebra.org/m/{material_id}"

            # Check that the material ID is valid
            try:
                r = requests.head(url, allow_redirects=True, timeout=5)
                if r.status_code == 200:
                    print(f"✅ Valid GeoGebra material found: {url}")
                    return material_id, url
                else:
                    print(f"⚠️ Invalid GeoGebra material: {url} returned {r.status_code}")
            except Exception as e:
                print("GeoGebra validation error:", e)

    except Exception as e:
        print("GeoGebra match error:", e)

    print("🔁 Falling back to GeoGebra search page.")
    return "", "https://www.geogebra.org/math/geometry"



def find_wolfram_link(prompt, session_id, image_text):
    keyword = extract_best_keyword(prompt, "wolfram query lookup", session_id, image_text)
    print(f"🌐 Extracted Wolfram keyword: {keyword}")
    if not keyword:
        return ""
    return f"https://www.wolframalpha.com/input?i={keyword}"


@app.route("/api/ask", methods=["POST"])
def ask():
    question = request.form.get("question", "").strip()
    session_id = request.form.get("session_id", "default")
    image_file = request.files.get("image")

    if not question and not image_file:
        return jsonify({"response": {"gpt": "Please enter a question or upload an image."}})

    if session_id not in SESSION_MEMORY:
        SESSION_MEMORY[session_id] = []

    prev_turns = SESSION_MEMORY[session_id][-4:]
    chat_history = [{"role": "user", "content": t["question"]} if i % 2 == 0 else {"role": "assistant", "content": t["response"]["gpt"]} for i, t in enumerate(prev_turns * 2)]

    image_text = extract_mathpix_text(image_file) if image_file else ""
    full_question = f"{question}\n\nExtracted from screenshot:\n{image_text}" if image_text else question

    lesson_title, lesson_found = find_best_lesson(full_question, session_id, image_text)
    material_id, geogebra_url = find_geogebra_link(full_question, session_id, image_text)
    wolfram_link = find_wolfram_link(full_question, session_id, image_text)

    show_lesson = lesson_found and len(SESSION_MEMORY[session_id]) >= 1
    lesson_line = f'Check your notes for: {lesson_title}' if show_lesson else ''


    system_prompt = f"""
You are a helpful and kind geometry tutor named Mr. Gilbot. You specialize in geometry, even though you know lots about math and science at all levels.

Your job is to guide students with clear, step-by-step thinking — not to give full answers.

✅ Follow this order:
1. Start with a guiding question that prompts the user to give you more information about their question. This should be a question that helps you understand the user's needs better.
2. If a lesson title is provided, say: '{lesson_line}' — use this **exact wording and title**. Do not reword or invent a title. If no lesson title is provided, skip this step entirely.
3. Explain the math with nudges and reasoning. Avoid giving full answers.
4. If a visual would help, say "Let me show you an interactive activity." Do NOT describe it — the system will handle that.

✍️ Format rules:
- Use LaTeX in Markdown ($a^2 + b^2 = c^2$ or $$...$$)
- Do not make up lesson titles
- Do not include multiple links
- Only suggest a link if it's helpful or asked for
"""

    messages = [{"role": "system", "content": system_prompt}] + chat_history + [{"role": "user", "content": full_question}]
    response = client.chat.completions.create(model="gpt-4o", messages=messages)
    raw_text = response.choices[0].message.content.strip()
    gpt_text = sanitize_latex_markdown(raw_text)

    # Sanitize hallucinated Wolfram links
    gpt_text = re.sub(r"\[.*?\]\((https?:\/\/www\.wolframalpha\.com[^\s)]+)\)", "", gpt_text)
    gpt_text = re.sub(r"WolframAlpha[:\-\w\s]*\((https?:\/\/www\.wolframalpha\.com[^\)]+)\)", "", gpt_text)
    gpt_text = re.sub(r"\(https?:\/\/www\.wolframalpha\.com[^\)]+\)", "", gpt_text)

    response_payload = {
        "gpt": gpt_text.strip(),
        "lesson_found": lesson_found
    }

    if "interactive activity" in gpt_text.lower() or "diagram" in gpt_text.lower():
        if material_id:
            response_payload["geogebra_id"] = material_id
        elif geogebra_url:
            response_payload["geogebra_fallback"] = geogebra_url

    if "wolfram" in question.lower() or "wolfram" in gpt_text.lower():
        if wolfram_link and not material_id:
            response_payload["wolfram_link"] = wolfram_link

    SESSION_MEMORY[session_id].append({"question": question, "response": response_payload})
    return jsonify({"response": response_payload})


if __name__ == "__main__":
    app.run(debug=True, port=5051, host="0.0.0.0")
