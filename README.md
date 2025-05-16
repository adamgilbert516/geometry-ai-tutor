# GEOMETRY AI TUTOR
#### Video URL: <[ Project Description ](https://youtu.be/DcenZZnQq3Y)>

**Live site:** [https://geometry-ai-tutor.vercel.app/](https://geometry-ai-tutor.vercel.app/)

## Description

### Overview

Geometry AI Tutor, aka *Mr. Gilbot*, is a web-based educational AI tutor that is designed to help high school students with classwork, homework, or large projects related, but not limited to, Geometry. Students are always encouraged first and foremost to use **human** teachers for help and assistance after they have already checked their own resources or worked through a problem with a peer. 

Students are not permitted to use ChatGPT, Deepseek, or any other GPT model available on the internet to help with their work as it can harm their ability to learn the content thoroughly. However, they will have to navigate a world with AI and learning how to use it properly is a skill in of itself. *Mr. Gilbot* offers guardrails for students and pushes their thinking by prompting with questions and directing students to course-specific resources in a similar manner of their teacher, using hints, videos, and interactive diagrams.

### Structural Decisions

This application was built using a *React + Vite* frontend and a *Flask* backend, the app integrates *OpenAI* for natural language understanding, *GeoGebra* for visual interactivity, *MathPix OCR* for image-based question parsing, and *Khan Academy* for video enrichment. The application is optimized for both student usability and educator deployment, with support for session memory, image uploads, curriculum-aligned lesson suggestions, and dark mode.

#### Frontend
- **React 19** with **Vite**
- **TailwindCSS 4** + **DaisyUI** for styling
- **Framer Motion** for chat animation
- **react-markdown** with **remark-math** and **rehype-katex** for LaTeX rendering
- **Google OAuth** for student login
- **GeoGebra deployggb.js** for applet integration

The main purpose of the frontend of this application is to take the raw JSON response payload, which includes the GPT response, links for GeoGebra activities, lesson titles, and links for Khan Academy videos and render it nicely in the chat interface. The files `index.html` and `App.jsx` are the main frontend files with `main.jsx` as the entry point. The additional components `AIResponseBlock.jsx` and `GeoGebraEmbed.jsx` offer additional frontend functionality to Mr. Gilbot's response within the chat container.

I decided to use *React + Vite* for this project because React is relatively simple to learn and it offers scalability and efficiency, especially when paired with *Vite*. I learned how to use React in *Full Stack open*'s course on modern Web Development. *ChatGPT* helped me integrate *React + Vite* and create a directory structure with some starter files with templates inside them. React + Vite work well with `jsx`(Javascript XML), which is essentially a hybrid of Javascipt and HTML, and while it is similar to both languages it is separate.

*TailwindCSS* is a utility library that allowed me to create modern and dynamic UI with lots of control over the look and feel of the interface. Combined with *Framer Motion* I was able to create a sleek chat animation with both light and dark mode. *DaisyUI* is a component library built on top of *TailwindCSS* that allowed me to even more simply integrate it into the frontend.

Using *react-markdown*, *remark-math*, and *rehype-katex*, the LaTeX in the raw GPT response is able to be rendered beautifully for the user to clearly see mathematical steps and relationships. The *GeoGebra deployggb.js* allows the GeoGebra activities to embed within the chat inferface container, so the user has the option to use the applet directly or use an external link.

#### Backend
- **Python 3.10+**
- **Flask** API with CORS support
- **OpenAI API (GPT-4o)** for natural language responses
- **MathPix API** for OCR
- **Pandas** and **fuzzy matching** for curriculum and resource lookups

Since CS50 teaches Flask, I chose to use Flask as my backend Web Framework since this application is lightweight on the backend. The file `app.py` is the main backend file with additional data files provided in `.csv` format. The route `/api/ask` is the main endpoint for processing user questions and images. In the function, `ask`, user input, image text (if applicable) parsed with *MathPix OCR* is combined with a `system_prompt` that is send to Open AI for a response. This response is then cleaned into a variable called `gpt_text`, which is then integrated with data from Wolfram Alpha, GeoGebra, and Khan Academy, relevant to the `keyword` that was extracted from the user's question. A variable called `response_payload` is list of dictionaries containing the data that will be transformed into a JSON to be sent to the frontend using `jsonify`. The `/api/alternates` route handles any alternate resources that the user needs.

The file also includes helper functions like `extract_best_keyword` extract the best keyword from the user's question in order to find relevant links with GeoGebra, Khan Academy, and relevant lessons. The functions that take this keyword as input and return this data are `find_geogebra_link`, `find_best_video`, and `find_best_lesson` with some additional helper functions that find matches within the `.csv` files mapping keywords to relevant data needed.

#### Directory Structure

- `root`
- `requirements.txt`: required installments to deploy
- `/dev-tools`: Scripts written in development
- `/frontend`: React + Vite application
  - `/public`: files needed for styling/logo
  - `/src`
    - `App.jsx`: main logic for chat UI, authentication, and state
    - `main.jsx`: entry point
    - `index.css`, `App.css`: custom styling
    - `/components`: main frontend components
      - `AIResponseBlock.jsx`, `GeoGebraEmbed.jsx`: handles AI message rendering with markdown, KaTeX, and embedded media and embeds interactive applets based on `material_id`
- `/backend`: Flask application
  - `app.py`: handles question routing, OCR, keyword extraction, and resource lookup
  - `geogebra_materials.csv`, `khan_video_matches.csv`, and `Curriculum Dictionary.csv`: data sources


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