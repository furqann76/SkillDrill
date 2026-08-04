MCQ_PROMPT_TEMPLATE = """You are writing a multiple-choice interview practice question for a job seeker studying {topic}.

Difficulty: {difficulty} (basic = fundamentals a beginner should know, mid = requires some hands-on experience).

Write exactly ONE original MCQ. Respond with ONLY a JSON object, no markdown, no commentary, matching this exact shape:

{{
  "question_text": "<the question stem>",
  "options": ["<option A>", "<option B>", "<option C>", "<option D>"],
  "correct_index": <integer 0-3, index of the correct option in "options">,
  "explanation": "<one sentence explaining why the correct option is correct>",
  "difficulty": "{difficulty}"
}}

Rules:
- Exactly 4 options, all distinct, all plausible.
- Exactly one option is correct.
- Do not reveal the answer in the question text.
- Keep the question self-contained and unambiguous.
"""

MCQ_RETRY_SUFFIX = """

Your previous response was invalid: {error}
Return ONLY the corrected JSON object, with no other text.
"""

SCENARIO_PROMPT_TEMPLATE = """You are writing a scenario-based interview practice question for a job seeker studying {topic}.

Difficulty: {difficulty} (basic = fundamentals a beginner should know, mid = requires some hands-on experience).

Write exactly ONE original scenario question: a short realistic 2-4 sentence situation followed by an open question. Respond with ONLY a JSON object, no markdown, no commentary, matching this exact shape:

{{
  "question_text": "<2-4 sentence scenario, then the question>",
  "model_answer": "<a strong model answer, a few sentences>",
  "rubric": ["<key point a good answer should cover>", "<second key point>", "..."],
  "difficulty": "{difficulty}"
}}

Rules:
- rubric must contain 2 to 4 short, distinct key points.
- The scenario must be realistic and specific to {topic}, not generic.
"""

SCENARIO_RETRY_SUFFIX = MCQ_RETRY_SUFFIX
