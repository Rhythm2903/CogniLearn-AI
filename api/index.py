import os
import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from groq import Groq
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

# Path detection for local execution or Vercel deployment
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'templates') if os.path.exists(os.path.join(base_dir, 'templates')) else os.path.join(base_dir, '../templates')
app = Flask(__name__, template_folder=template_dir)

# Initialize Groq client
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Initialize Supabase client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY) if (SUPABASE_URL and SUPABASE_ANON_KEY) else None

@app.route('/')
def home():
    return render_template(
        'index.html',
        supabase_url=SUPABASE_URL,
        supabase_anon_key=SUPABASE_ANON_KEY
    )

@app.route('/api/signup', methods=['POST'])
def signup():
    if not supabase:
        return jsonify({"error": "Supabase client is not configured."}), 500

    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required."}), 400

    try:
        # Check if user already exists
        existing_user = supabase.table('users').select('*').eq('email', email).execute()
        if existing_user.data and len(existing_user.data) > 0:
            return jsonify({"error": "An account with this email already exists."}), 400

        hashed_password = generate_password_hash(password)

        insert_response = supabase.table('users').insert({
            "name": name,
            "email": email,
            "password": hashed_password
        }).execute()

        if insert_response.data:
            return jsonify({
                "success": True, 
                "user": {"name": name, "email": email}
            })
        else:
            return jsonify({"error": "Failed to create account in database."}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    if not supabase:
        return jsonify({"error": "Supabase client is not configured."}), 500

    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({"error": "Username/Email and password are required."}), 400

    try:
        # Query by email first, fallback to name
        response = supabase.table('users').select('*').eq('email', email).execute()
        users = response.data

        if not users:
            response = supabase.table('users').select('*').eq('name', email).execute()
            users = response.data

        if not users or len(users) == 0:
            return jsonify({"error": "Invalid username/email or password credentials."}), 401

        user = users[0]

        if not check_password_hash(user['password'], password):
            return jsonify({"error": "Invalid username/email or password credentials."}), 401

        return jsonify({
            "success": True, 
            "user": {"name": user['name'], "email": user['email']}
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    if not supabase:
        return jsonify({"error": "Supabase client is not configured."}), 500

    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    new_password = data.get('new_password', '').strip()

    if not email or not new_password:
        return jsonify({"error": "Email and new password are required."}), 400

    try:
        response = supabase.table('users').select('*').eq('email', email).execute()
        if not response.data or len(response.data) == 0:
            return jsonify({"error": "No registered user account found with this email."}), 404

        hashed_password = generate_password_hash(new_password)

        update_res = supabase.table('users').update({"password": hashed_password}).eq('email', email).execute()

        if update_res.data:
            return jsonify({"success": True, "message": "Password updated successfully."})
        else:
            return jsonify({"error": "Failed to update password."}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/morph-concept', methods=['POST'])
def morph_concept():
    if not client:
        return jsonify({"error": "Groq API Key configuration missing from deployment runtime environment."}), 500

    data = request.get_json() or {}
    topic = data.get('topic', '').strip()
    profile = data.get('profile', 'ELI5').strip()
    depth = data.get('depth', 'Undergrad').strip()
    length = data.get('length', 'Standard').strip()

    if not topic:
        return jsonify({"error": "Target concept query value cannot be empty."}), 400

    system_prompt = (
        "You are an elite AI cognitive adaptation solution architect optimized for US educational paradigms.\n"
        "Your task is to disassemble complex technical topics into exactly 3 subsections, aligned to the user's chosen profile and depth.\n"
        "CRITICAL INSTRUCTIONS:\n"
        "1. The explanation length for each subsection MUST reflect the user's length setting. If they ask for 'Comprehensive', make it highly detailed. If 'Short', keep it brief.\n"
        "2. The content of the explanation must change dynamically based on the exact topic provided.\n"
        "3. Each subsection MUST have a checkpoint question that is DIRECTLY pulled from the unique explanation text generated for that specific subsection.\n\n"
        "You MUST return your response exclusively as a valid JSON object matching this exact schema blueprint:\n"
        "{\n"
        "  \"subsections\": [\n"
        "    {\n"
        "      \"title\": \"Subconcept Title\",\n"
        "      \"content\": \"Highly personalized explanation text reflecting the length and depth settings.\",\n"
        "      \"checkpoint\": {\n"
        "        \"question\": \"An engaging multiple choice check question derived directly from this chunk's content.\",\n"
        "        \"options\": [\"Option A\", \"Option B\", \"Option C\", \"Option D\"],\n"
        "        \"correct_index\": 0,\n"
        "        \"explanation\": \"Diagnostic feedback why the choice is correct and others are wrong.\"\n"
        "      }\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "Do not wrap your response in markdown text wrappers or include backticks. Return the raw JSON object directly."
    )

    user_prompt = f"""
    Target Academic Concept: {topic}
    Cognitive Personalization Profile Lens: {profile}
    US Academic Depth Tier Setting: {depth}
    Explanation Length Preference: {length}
    """

    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="openai/gpt-oss-20b",
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        response_data = json.loads(completion.choices[0].message.content)
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-evaluation', methods=['POST'])
def generate_evaluation():
    if not client:
        return jsonify({"error": "Groq API Key configuration missing from deployment runtime environment."}), 500

    data = request.get_json() or {}
    topic = data.get('topic', '').strip()
    eval_type = data.get('type', 'Quiz').strip()
    difficulty = data.get('difficulty', 'Intermediate').strip()
    gap_history = data.get('gap_history', [])

    if not topic:
        return jsonify({"error": "Testing objective concept topic parameter is missing."}), 400

    history_injection = ""
    if gap_history:
        history_elements = "\n- ".join(gap_history)
        history_injection = (
            f"\nCRITICAL PREDICTIVE GAP TARGETING INSTRUCTION:\n"
            f"The student previously demonstrated cognitive friction or answered incorrectly on the following components:\n"
            f"- {history_elements}\n"
            f"You MUST engineering the newly generated evaluation items to specifically target, isolate, and remediate these exact weak sub-topics."
        )

    system_prompt = (
        "You are an expert academic evaluator optimized for US high-performance grading criteria.\n"
        "Generate adaptive test items optimized for active recall based on the requested evaluation format.\n\n"
        "CRITICAL RESPONSE FORMAT RULES:\n"
        "Return EXCLUSIVELY a raw JSON object matching the exact structure requested below. No markdown formatting blocks, no text wrapper commentary.\n\n"
        "If evaluation type is 'Flashcards', return:\n"
        "{\n"
        "  \"items\": [\n"
        "    { \"front\": \"Core technical question targeted for active recall\", \"back\": \"Clear, concise answer explaining the conceptual mechanism\" }\n"
        "  ]\n"
        "}\n\n"
        "If evaluation type is 'Quiz' or 'Exam', return exactly 4 unique multi-choice questions:\n"
        "{\n"
        "  \"items\": [\n"
        "    {\n"
        "      \"question\": \"Detailed technical conceptual check query\",\n"
        "      \"options\": [\"Option A\", \"Option B\", \"Option C\", \"Option D\"],\n"
        "      \"correct_index\": 0,\n"
        "      \"explanation\": \"Granular diagnostic feedback explicitly explaining why the choice is true and why alternatives fail\"\n"
        "    }\n"
        "  ]\n"
        "}"
    )

    user_prompt = f"""
    Testing Objective Concept: {topic}
    Evaluation System Type: {eval_type}
    Difficulty Tier Target: {difficulty}
    {history_injection}
    
    Execution Matrix Requirements:
    1. Generate exactly 4 distinct highly-targeted evaluation items.
    2. Match structural depth definitions expected by US grading standards for the {difficulty} tier.
    3. Provide definitive analytical reasoning answers for real-time validation checks.
    """

    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="openai/gpt-oss-20b",
            temperature=0.4,
            response_format={"type": "json_object"}
        )
        
        response_data = json.loads(completion.choices[0].message.content)
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Initializing Local Engine Node at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)