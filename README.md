# CogniLearn AI

> **Autonomous Adaptive Pedagogical Engine & Socratic Micro-Learning Studio**

CogniLearn AI is an adaptive pedagogical learning engine that dynamically deconstructs complex textbooks, technical whitepapers, and curriculum documents into high-retention micro-lessons, interactive Socratic dialogs, and adaptive spaced-repetition flashcards.

---

## ðŸš€ Tech Stack & Core Technologies

Python 3.10+ Flask Groq LLM (LLaMA-3.1-8B) Supabase TailwindCSS Vercel

- **Python 3.10+ & Flask:** Modular web backend handling syllabus decomposition, session persistence, and API orchestration.
- **Groq LLM Engine:** High-velocity pedagogical reasoning providing personalized Socratic inquiry and concept breakdowns.
- **Supabase Cloud Backend:** Distributed database persistence for user progress, quiz results, and spaced-repetition schedules.
- **Interactive Micro-Learning Studio:** Clean responsive UI with dynamic theme customizations, active-recall drills, and progress analytics.
- **Serverless Cloud Ready:** Native zero-config architecture for Vercel deployment.

---

## âœ¨ Key Features

- **Document-to-Lesson Decomposition:** Converts lengthy syllabus chapters and technical PDFs into bite-sized, digestible learning modules.
- **Adaptive Socratic Dialogue:** Engages students in guided questioning rather than passive lecture delivery to deepen conceptual mastery.
- **Spaced-Repetition Flashcard Engine:** Automatically schedules active-recall reviews based on individual retention curves.
- **Concept Dependency Graphing:** Visually tracks prerequisite knowledge and flags conceptual bottlenecks.
- **Secure Learner Profiles:** Persistent user history, customizable UI themes, and complete session isolation.

---

## ðŸ› ï¸ Getting Started

### 1. Clone & Set Up Virtual Environment

`ash
git clone https://github.com/Rhythm2903/CogniLearn-AI.git
cd CogniLearn-AI

# Create and activate Python virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
`

### 2. Install Dependencies

`ash
pip install -r requirements.txt
`

### 3. Configure Environment Variables

`ash
cp .env.example .env
`

Populate .env with your GROQ_API_KEY and optional SUPABASE_URL / SUPABASE_ANON_KEY.

### 4. Run the Application

`ash
python -m flask run
`

---

## ðŸ” Environment Variables

Refer to [.env.example](.env.example) for required configuration keys.

---

## ðŸ“„ License

This project is open-source and available under the [MIT License](LICENSE).

---

## ðŸ‘¤ Author

Developed & Maintained by **Rhythm Agarwal** ([@Rhythm2903](https://github.com/Rhythm2903))