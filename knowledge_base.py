# This file serves as the universal "knowledge base" for our interactive agents.
# It contains the "gold standard" targets that the Interaction Manager ("Y Agent")
# will use to understand its goals and generate clarifying questions.

# --- Gold Standard for the Poster Generator ---
POSTER_AGENT_KNOWLEDGE = {
    "gold_standard_target": """Envision a neon-soaked rain-slicked Mumbai megacity street in 2099, a chrome-armored Mahindra Thar hovers mid-air with glowing energy treads, flanked by holographic street racers and cyber-samurai spectators, electric kanji billboards screaming 'THAR 2099' while the sky erupts in violet lightning, cinematic lens flares slicing through torrential rain and smoke, all captured in ultra-wide cinematic glory.

📐 Layout:
- Top center: Large bold heading — "THAR 2099 UNLEASHED"
- Just below: Smaller subheading — "Legacy Reborn Beyond Gravity"
- Center area: Short paragraph — "Experience the ultimate all-terrain beast reborn for a cyberpunk future."
- Bottom left: Compact highlight of achievements — "1M Pre-Orders | 99.9% Uptime | 5-Star Safety"
- Very bottom: Minimal hyperlink — "reserve.thar2099.mahindra"

🧠 Critical Instructions:
- Do **not** include any field labels like "Success Metrics", "Target Audience", or "Testimonial".
- The text should appear *naturally* as part of the poster design — not as form layout or metadata.
- Treat all text elements as part of the visual composition.
- Avoid overlapping, distortion, and gibberish. Fonts must be clean, sans-serif, and fully legible.

🎨 Background Theme:
A clean, tech-inspired background with modern gradients and soft lighting effects.

🖋 Typography & Composition:
- Fonts: Bold, sans-serif, clean, fully legible.
- Layout: Balanced, white-space aware, no overlaps.
- No gibberish text, no field names like 'Testimonial' shown.
"""
}


# --- Gold Standard for the Lead/Sales Intent Generator ---
SALES_AGENT_KNOWLEDGE = {
    "gold_standard_target": {
        "conversation_history": {
            "required": True,
            "description": "At least 2-3 client messages showing buying signals, objections, or interest level."
        },
        "company_context": {
            "required": True,
            "description": "Information about the client's company size, industry, or use-case if mentioned."
        },
        "objections_or_questions": {
            "required": False,
            "description": "Mentions of price concerns, timeline issues, feature gaps — helps determine pain points."
        },
        "intent_hint": {
            "required": False,
            "description": "Optional: If the sales rep has a gut feeling about intent, they can include it."
        },
        "rep_notes": {
            "required": False,
            "description": "Optional internal notes about client behavior or call summary — improves context for next best action."
        }
    },
    "system_generated_fields": [
        "predicted_intent",
        "next_best_action"
    ]
}
