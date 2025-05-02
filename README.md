# Geometry AI Tutor

**Live site:** [https://geometry-ai-tutor.vercel.app/](https://geometry-ai-tutor.vercel.app/)

## Overview

The Geometry AI Tutor is a web-based educational assistant designed to help students engage more deeply with geometry concepts through guided questioning, interactive visuals, and context-aware feedback. Unlike traditional AI solutions that provide direct answers, this tool encourages step-by-step reasoning and supports learning by prompting students with strategic hints and interactive diagrams.

Built using a React + Vite frontend and a Flask backend, the app integrates OpenAI for natural language understanding, GeoGebra for visual interactivity, MathPix OCR for image-based question parsing, and Khan Academy for video enrichment. The application is optimized for both student usability and educator deployment, with support for session memory, image uploads, curriculum-aligned lesson suggestions, and dark mode.

## Features

- **Natural Language Interaction**: Students can ask questions in plain English. The AI (nicknamed *Mr. Gilbot*) replies with hints and questions to promote deeper thinking.
- **Session Awareness**: Remembers recent interactions to improve the relevance of follow-up prompts and lessons.
- **Image OCR**: Upload screenshots of problems. MathPix extracts the math content, which is used for generating a response.
- **GeoGebra Embeds**: If the AI determines a visual is helpful, it includes an interactive GeoGebra diagram.
- **Khan Academy Video Suggestions**: Relevant instructional videos are embedded or linked when appropriate.
- **Curriculum Integration**: Suggests lessons aligned to a curriculum CSV, allowing customization for different schools or districts.
- **Dark Mode**: Built-in toggleable theme for user comfort.
- **Drag & Drop File Uploads**: Upload files directly into the chat interface.

## Technologies Used

### Frontend
- **React 19** with **Vite**
- **TailwindCSS 4** + **DaisyUI** for styling
- **Framer Motion** for chat animation
- **react-markdown** with **remark-math** and **rehype-katex** for LaTeX rendering
- **Google OAuth** for student login
- **GeoGebra deployggb.js** for applet integration

### Backend
- **Python 3.10+**
- **Flask** API with CORS support
- **OpenAI API (GPT-4o)** for natural language responses
- **MathPix API** for OCR
- **Pandas** and **fuzzy matching** for curriculum and resource lookups

## Folder Structure

- `/frontend`: React + Vite application
  - `App.jsx`: main logic for chat UI, authentication, and state
  - `AIResponseBlock.jsx`: handles AI message rendering with markdown, KaTeX, and embedded media
  - `GeoGebraEmbed.jsx`: embeds interactive applets based on `material_id`
  - `main.jsx`: entry point
  - `index.css`, `App.css`: custom styling
- `/backend`: Flask app
  - `app.py`: handles question routing, OCR, keyword extraction, and resource lookup
  - `geogebra_materials.csv`, `khan_video_matches.csv`, and `Curriculum Dictionary.csv`: data sources
  - `geogebra_topics.py`: keyword index for GeoGebra matching

## Setup Instructions

### Local Development

#### Prerequisites
- Node.js (v18+)
- Python 3.10+
- `pip`, `virtualenv`, or `conda`
- `npm` or `yarn`

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
```

Set your `.env` file in `/backend` with the following:

```
OPENAI_API_KEY=...
MATHPIX_API_KEY=...
MATHPIX_API_ID=...
```

Ensure CORS is properly set to allow requests between `localhost:3000` and your backend (default Flask port is `5051`).

### Production

The frontend is deployed to Vercel:
📍 [https://geometry-ai-tutor.vercel.app](https://geometry-ai-tutor.vercel.app)

The backend can be deployed on Render or any Flask-compatible cloud host. The frontend expects the API at `/api/ask`.

## Future Plans

- Support for multilingual OCR and translation
- Curriculum support for Algebra, Precalculus, and Calculus
- Admin panel for educators to view student progress
- Support for multiple file uploads and expanded image previews
- Enhanced keyword extraction using GPT for broader content alignment

## Contributing

If you're interested in extending the project (e.g., adding new curriculum datasets or improving the OCR flow), feel free to fork the repo and submit a pull request. Feature requests and issue reports are welcome.