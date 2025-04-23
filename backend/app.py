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

load_dotenv()
client = OpenAI()
mathpix_app_id = os.getenv("MATHPIX_API_ID")
mathpix_api_key = os.getenv("MATHPIX_API_KEY")

curriculum_df = pd.read_csv("geometry-curriculum.csv")
geogebra_df = pd.read_csv("geogebra-materials.csv")
khan_df = pd.read_csv("khan-videos.csv")
BANNED_KEYWORDS = {"wolfram", "video", "activity", "geogebra", "resource", "interactive", "lesson", "none", "none of the above", "none of these", "none of the above"}



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

def sanitize_text(text):
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text)
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text)
    text = re.sub(r'\[\s*([^\[\]]+?)\s*\]', r'$\1$', text)
    text = re.sub(r'\(\s*([a-zA-Z0-9^]+)\s*\)', r'\1', text)
    text = re.sub(r'(?<!\$)(\b[a-zA-Z])\(([^)]+)\)(?!\$)', r'$\1(\2)$', text)
    text = re.sub(r'(?<!\\)([a-zA-Z])\(([^)]+)\)', r'\1\\left(\2\\right)', text)
    text = text.replace(r'\left\left', r'\left').replace(r'\right\right', r'\right')
    text = re.sub(r"\[.*?\]\((https?:\/\/www\.wolframalpha\.com[^\s)]+)\)", "", text)
    text = re.sub(r"WolframAlpha[:\-\w\s]*\((https?:\/\/www\.wolframalpha\.com[^\)]+)\)", "", text)
    text = re.sub(r"\(https?:\/\/www\.wolframalpha\.com[^\)]+\)", "", text)

    return text.strip()

def get_geogebra_matches(keyword, max_results=5):
    if not keyword:
        return []

    all_keywords = geogebra_df['Keywords'].dropna().str.lower().tolist()
    best_match = fuzzy_keyword_match(keyword, all_keywords, "geogebra search")
    matched = geogebra_df[geogebra_df['Keywords'].str.lower().str.contains(best_match)] if best_match else pd.DataFrame()

    activities = []
    if not matched.empty:
        for _, row in matched.iterrows():
            material_id = row['MaterialID']
            url = f"https://www.geogebra.org/m/{material_id}"
            title = row['Title'] if 'Title' in row else f"GeoGebra Activity {len(activities)+1}"
            activities.append({
                "material_id": material_id,
                "url": url,
                "title": title
            })
            if len(activities) >= max_results:
                break
    return activities

def fuzzy_keyword_match(keyword, candidates, source=""):
    keyword = keyword.lower().strip()
    candidates_lower = [c.lower().strip() for c in candidates]

    # ✅ First, check for an exact match
    if keyword in candidates_lower:
        exact = candidates[candidates_lower.index(keyword)]
        print(f"✅ Exact match found for '{keyword}' in {source}: {exact}")
        return exact

    # 🔁 Fallback: use fuzzy matching
    match = get_close_matches(keyword, candidates_lower, n=1, cutoff=0.6)
    if match:
        matched_index = candidates_lower.index(match[0])
        fuzzy = candidates[matched_index]
        print(f"🔍 Fuzzy match for '{keyword}' in {source}: {fuzzy}")
        return fuzzy

    print(f"❌ No match found for '{keyword}' in {source}")
    return None

def extract_best_keyword(prompt, context, session_id, image_text=""):
    try:
        combined_input = f"User question: {prompt}"
        if image_text:
            combined_input += f"\n\nMathPix OCR from image:\n{image_text}"

        messages = [
            {
                "role": "system",
                "content": f"Extract a single math keyword useful for {context}. If irrelevant, return 'none'."
            },
            {"role": "user", "content": combined_input}
        ]
        result = client.chat.completions.create(model="gpt-4o", messages=messages)
        keyword = result.choices[0].message.content.strip().lower()

        if keyword in BANNED_KEYWORDS or keyword == "none":
            print(f"⚠️ Banned or invalid keyword '{keyword}' returned.")
            return TOPIC_MEMORY.get(session_id, TOPIC_MEMORY.get("global", ""))
        else:
            print(f"📌 Stored keyword: {keyword}")
            TOPIC_MEMORY[session_id] = keyword
            TOPIC_MEMORY["global"] = keyword
            return keyword

    except Exception as e:
        print(f"{context} keyword extraction error:", e)
        return TOPIC_MEMORY.get(session_id, "")

def find_geogebra_alternates(keyword):
    matches = get_geogebra_matches(keyword)
    return matches[1:] if len(matches) > 1 else []

def find_best_lesson(keyword, max_results=3):
    if not keyword:
        print("⚠️ No keyword for lesson lookup.")
        return None

    exact_matches = []
    fuzzy_matches = []

    for _, row in curriculum_df.iterrows():
        lesson_keywords = str(row['Keywords']).lower().split(',')
        lesson_keywords = [k.strip() for k in lesson_keywords if k.strip()]

        # ✅ Check for exact match first
        if keyword in lesson_keywords:
            exact_matches.append(row['Lesson Title'])
        else:
            # Fuzzy fallback
            for k in lesson_keywords:
                if fuzzy_keyword_match(keyword, [k], "lesson fuzzy") == k:
                    fuzzy_matches.append(row['Lesson Title'])
                    break

    if exact_matches:
        return {
            "primary": exact_matches[0],
            "alternates": exact_matches[1:max_results]
        }
    elif fuzzy_matches:
        return {
            "primary": fuzzy_matches[0],
            "alternates": fuzzy_matches[1:max_results]
        }

    return None

def find_geogebra_link(keyword):
    matches = get_geogebra_matches(keyword)
    if matches:
        primary = matches[0]
        return primary["material_id"], primary["url"]
    return "", "https://www.geogebra.org/math/geometry"


def find_wolfram_link(keyword):
    return f"https://www.wolframalpha.com/input?i={keyword}" if keyword else ""

def find_best_video(keyword, max_results=3):
    if not keyword:
        return None

    keyword = keyword.lower().strip()
    exact_matches = []
    fuzzy_matches = []

    for _, row in khan_df.iterrows():
        if pd.notna(row['keywords']):
            topics = [k.strip().lower() for k in row['keywords'].split(',')]
            # Exact match first
            if keyword in topics:
                exact_matches.append({
                    "title": row["video_title"],
                    "video_id": row["video_id"],
                    "url": row["video_url"]
                })
            else:
                # Fuzzy match fallback
                for t in topics:
                    if fuzzy_keyword_match(keyword, [t], "video fuzzy") == t:
                        fuzzy_matches.append({
                            "title": row["video_title"],
                            "video_id": row["video_id"],
                            "url": row["video_url"]
                        })
                        break

        if len(exact_matches) >= max_results:
            break

    final_matches = exact_matches if exact_matches else fuzzy_matches

    if final_matches:
        return {
            "primary": final_matches[0],
            "alternates": final_matches[1:max_results]
        }

    return None

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

    keyword = extract_best_keyword(full_question, "unified lookup", session_id, image_text)
    material_id, geogebra_url = find_geogebra_link(keyword)
    wolfram_link = find_wolfram_link(keyword)
    video_data = find_best_video(keyword)
    lesson_data = find_best_lesson(keyword)

    suggest_lesson = False

    # Trigger if it's the first question OR if the user asks about reviewing concepts
    if len(SESSION_MEMORY[session_id]) <= 1:
        suggest_lesson = True
    elif any(word in question.lower() for word in ["lesson", "notes", "review", "topic"]):
        suggest_lesson = True


    lesson_line = f'Check your notes for: {lesson_data["primary"]}' if suggest_lesson and lesson_data else ''

    print(f"✅ FINAL RESULTS:")
    print(f"   ➤ Keyword: {keyword}")
    if lesson_data:
        print(f"   ➤ Lesson Primary: {lesson_data['primary']}")
        print(f"   ➤ Lesson Alternates: {lesson_data['alternates']}")
    else:
        print("   ➤ No lesson found.")
    print(f"   ➤ GeoGebra: {geogebra_url}")
    print(f"   ➤ Wolfram: {wolfram_link}")
    if video_data:
        print(f"   ➤ Khan Academy Primary: {video_data['primary']['title']}")
        print(f"   ➤ Khan Academy Alternates: {len(video_data['alternates'])}")


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
    gpt_text = sanitize_text(raw_text)

    response_payload = {
        "gpt": gpt_text.strip()
    }

    if suggest_lesson and lesson_data:
        response_payload["lesson_primary"] = lesson_data["primary"]
        if lesson_data["alternates"]:
            response_payload["lesson_alternates"] = lesson_data["alternates"]

    # GeoGebra Handling
    if "interactive activity" in gpt_text.lower() or "diagram" in gpt_text.lower():
        geogebra_matches = get_geogebra_matches(keyword)
        if geogebra_matches:
            primary = geogebra_matches[0]
            response_payload["geogebra_id"] = primary["material_id"]
            if len(geogebra_matches) > 1:
                response_payload["geogebra_alternates"] = geogebra_matches[1:]
        else:
            response_payload["geogebra_fallback"] = "https://www.geogebra.org/math/geometry"
        print(f"   ➤ GeoGebra Alternates: {len(response_payload.get('geogebra_alternates', []))}")

    # Video Handling
    if video_data and (
        "video" in question.lower() 
        or "khan" in question.lower() 
        or "video" in gpt_text.lower()
    ):
        response_payload["khan_video"] = {
            "primary": {
                "title": video_data["primary"]["title"],
                "video_id": video_data["primary"]["video_id"],
                "url": video_data["primary"]["url"]
            },
            "alternates": video_data["alternates"]
        }
        print(f"✅ Video suggestion included with {len(video_data['alternates'])} alternates.")

        # Inject helper text if GPT didn't mention video
        if "video" not in gpt_text.lower() and "let me show you a video" not in gpt_text.lower():
            gpt_text += "\n\nLet me show you a video."

    # Finalize GPT response after possible injection
    response_payload["gpt"] = gpt_text.strip()



    SESSION_MEMORY[session_id].append({"question": question, "response": response_payload})
    return jsonify({"response": response_payload})

@app.route("/api/alternates", methods=["POST"])
def get_alternates():
    session_id = request.form.get("session_id", "default")
    keyword = TOPIC_MEMORY.get(session_id, "")

    video_data = find_best_video(keyword)
    geogebra_matches = get_geogebra_matches(keyword)

    response_payload = {
        "video_alternates": video_data["alternates"] if video_data and len(video_data["alternates"]) > 0 else [],
        "geogebra_alternates": geogebra_matches[1:] if geogebra_matches and len(geogebra_matches) > 1 else []
    }

    print(f"📦 /api/alternates for keyword: {keyword}")
    print(f"   ➤ Video alternates: {len(response_payload['video_alternates'])}")
    print(f"   ➤ GeoGebra alternates: {len(response_payload['geogebra_alternates'])}")

    return jsonify(response_payload)




if __name__ == "__main__":
    app.run(debug=True, port=5051, host="0.0.0.0")
