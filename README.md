
# 📐 Geometry AI Tutor

**Geometry AI Tutor** is an interactive, AI-powered web application designed to support students in learning geometry through guided hints, interactive visuals, and curated resources — **without giving away full answers**. Built with React, TailwindCSS, Flask, and integrated with advanced AI tools, this tutor mimics the behavior of a thoughtful human teacher.

---

## 🚀 Features

- 💡 **AI-Powered Guidance**: Uses GPT-4o to provide step-by-step hints and probing questions.
- 📊 **Interactive GeoGebra Visuals**: Embeds dynamic geometry diagrams when helpful.
- 🎥 **Khan Academy Video Integration**: Suggests relevant videos for deeper understanding.
- ➕ **Wolfram Alpha Links**: Offers clean, embedded explanations for advanced concepts.
- 🖼️ **Screenshot Support**: Upload math problems via image; MathPix OCR extracts and interprets text.
- 🌗 **Dark Mode Toggle**: Smooth, user-friendly UI with light/dark themes.
- 🗂️ **Session Memory**: Tracks conversation history for context-aware tutoring.
- 🔒 **Google OAuth Login**: Personalized experience with secure Google sign-in.
- 📂 **Drag-and-Drop File Uploads**: Chat interface supports intuitive file sharing.

---

## 🛠️ Tech Stack

### **Frontend** 
- React + Vite
- TailwindCSS + DaisyUI
- Framer Motion (animations)
- Google OAuth
- React-Markdown + KaTeX for LaTeX rendering

### **Backend**
- Flask (Python)
- OpenAI GPT-4o API
- MathPix OCR API
- CSV-based resource lookups (Curriculum, GeoGebra, Khan Academy)
- CORS-enabled API for frontend integration

---

## 🌐 Live Demo
> _Coming Soon_ — Deployed on **Vercel** (Frontend) and **Render** (Backend).

---

## 📸 Screenshots
*(Add screenshots or GIFs here once deployed!)*

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/geometry-ai-tutor.git
cd geometry-ai-tutor
```

### 2. Backend Setup (`/backend`)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_key
MATHPIX_API_KEY=your_mathpix_key
MATHPIX_API_ID=your_mathpix_app_id
```
Run the Flask server:
```bash
python app.py
```

### 3. Frontend Setup (`/frontend`)
```bash
cd ../frontend
npm install
npm run dev
```

Visit: `http://localhost:5173`

---

## 📂 Project Structure
```
geometry-ai-tutor/
├── backend/          # Flask API + CSV resources
├── frontend/         # React + Vite frontend
├── dev-tools/        # Helper scripts (scrapers, CSV generators)
└── README.md
```

---

## 🚧 Roadmap
- [ ] Deploy to Vercel & Render
- [ ] Add multilingual support
- [ ] Improve AI hint sequencing
- [ ] Expand resource database
- [ ] Implement student progress tracking

---

## 🤝 Contributing
This is a personal project, but contributions or suggestions are welcome! Feel free to open issues or pull requests.

---

## 🙌 Acknowledgements
- [OpenAI](https://openai.com/)
- [GeoGebra](https://www.geogebra.org/)
- [Khan Academy](https://www.khanacademy.org/)
- [MathPix](https://mathpix.com/)
- [Wolfram Alpha](https://www.wolframalpha.com/)
