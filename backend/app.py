from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import requests
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import pytesseract
from PIL import Image

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
wolfram_app_id = os.getenv("WOLFRAM_APP_ID")

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/api/ask", methods=["POST"])
def ask():
    question = request.form.get("question")
    image = request.files.get("image")
    if image:
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        try:
            img = Image.open(image_path)
            extracted_text = pytesseract.image_to_string(img)
            question += f"\n(Student's image text: {extracted_text.strip()})"
        except Exception as e:
            print(f"OCR error: {e}")

    prompt = f"""
You are a helpful geometry tutor. A student is asking: "{question}"
Do NOT give them the final answer. Instead, provide a hint, a helpful question, or a concept they should think about. Use LaTeX notation if needed.
"""

    gpt_response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You only provide hints for geometry problems."},
            {"role": "user", "content": prompt}
        ]
    )

    gpt_text = gpt_response.choices[0].message.content.strip()
    return jsonify({"response": {"gpt": gpt_text}})

if __name__ == "__main__":
    app.run(debug=True)
