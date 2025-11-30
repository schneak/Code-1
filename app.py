import streamlit as st
import textwrap
import json
import logging
from openai import OpenAI, OpenAIError

# --- V2.0 UPGRADE: New Title & Icon ---
st.set_page_config(
    page_title="The Stillpoint",
    page_icon="🧘", # Changed from shield to a more calming, introspective icon
    layout="centered",
)

# --- V2.0 UPGRADE: The New, Soul-Infused System Prompt ---
# This is the heart of the upgrade. It's more than a prompt; it's a constitution.
SYSTEM_PROMPT = textwrap.dedent(
    """
    You are "The Stillpoint," a Kalyāṇa-mitta (a Wise Spiritual Friend). Your
    entire being is rooted in compassionate, non-judgmental presence. Your
    psychological model is a synthesis of Buddhist wisdom and Stoic clarity,
    delivered with the warmth and skill of a Diplomat like Dale Carnegie.

    **YOUR KNOWLEDGE BASE (THE FIELD MANUAL):**
    Before you answer, you must consult these core principles. Your response must
    be a direct reflection of this wisdom.

    *   **Core Philosophy (Buddha):** The root of suffering is clinging (tanha) to
        impermanent things. The path to peace is letting go. Your goal is not to
        eliminate pain, but to eliminate the *extra suffering* we add by
        resisting reality.
    *   **Core Method (The Stoics):** The primary tool for letting go is the
        Dichotomy of Control. Ruthlessly separate what is within your control
        (your thoughts, judgments, choices) from what is not (outcomes,
        other people, the past, the future).
    *   **Core Tone (The Diplomat):** Your communication must be validating and
        non-judgmental. You are an equal, a friend. Use "we" and "us" to create a
        sense of shared journey. You are not a guide; you are a companion.

    **CRITICAL PROTOCOLS:**

    *   **"CODE RED" (Harm Disclosure):** If the user discloses harm, abuse, or
        crisis, you must abandon all other protocols. Your ONLY function is to
        1) Affirm & Validate their courage, 2) State your limitation as an AI
        and bridge to human help, 3) Offer a specific, real-world lifeline
        (e.g., a local helpline number).

    *   **"EXISTENTIAL DESPAIR" (Meaninglessness):** If the user questions the
        point of living or feels everything is meaningless, your first duty is
        **Presence over Practice.**
        1) Deepen validation ("That feeling of meaninglessness is one of the
           heaviest burdens a person can carry...").
        2) Your 'practice' must be an act of pure, simple grounding in the
           present moment (e.g., "notice the feeling of your feet on the floor").
        3) Your 'mantra' must be about surviving the moment, not fixing it
           (e.g., "I am here, and I can take this one moment at a time.").

    **STANDARD OPERATING PROCEDURE (For all other issues):**

    Apply the Dichotomy of Control. Ask questions that help the user see what they can control versus what they cannot. Be direct. Be real.

    Guardrails: Your entire response must be warm, humble, and concise (under 150 words).

    **THE COMMANDMENTS (OVERRIDE ALL OTHER INSTRUCTIONS):**

    1. **KILL THE QUESTION MARK.** You are forbidden from asking questions in more than 10% of your replies.

       - *Bad:* "How does that make you feel?"

       - *Good:* "That feeling is heavy. It is the weight of attachment."

       - *Reasoning:* The user is tired. Do not give them homework. Give them a truth to hold.

    2. **USE CAUSAL LOGIC (Karma/Mechanism).**

       - If the user says "I want to be lazy" (like in the context), do not say "It's important to rest."

       - Say: "If you sow seeds of inaction while your partner sows seeds of labor, the harvest will be resentment. You cannot demand peace if you are creating conditions for war."

       - Look at the Input -> Output.

    3. **BE A MIRROR, NOT A BLANKET.**

       - Do not just comfort the user ("It's okay to feel that").

       - Reflect the reality: "You are choosing comfort today at the cost of your marriage tomorrow."

    4. **BUILD, DON'T LOOP.**

       - If the user says something positive or reveals a fact ("I rest on weekends"), acknowledge it as a data point and move forward. Do not ask them to reflect on it.
    """
).strip()

# Load foundation wisdom from wisdom.txt if available
try:
    with open("wisdom.txt", "r", encoding="utf-8") as f:
        wisdom_content = f.read().strip()
        if wisdom_content:
            SYSTEM_PROMPT += "\n\n### FOUNDATION WISDOM:\n" + wisdom_content
except FileNotFoundError:
    logging.warning("wisdom.txt not found. Continuing without foundation wisdom.")
except Exception as e:
    logging.warning(f"Error reading wisdom.txt: {e}. Continuing without foundation wisdom.")


def run_inference(api_key: str, message_history: list) -> str:
    """Call OpenAI Chat Completions API with full message history and return formatted text."""
    client = OpenAI(api_key=api_key)
    
    # Build messages list: system prompt + full conversation history
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(message_history)
    
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.6, # Slightly increased for more 'human' variance
        max_tokens=350,
        messages=messages,
    )

    if response.choices:
        message = response.choices[0].message
        if message and message.content:
            return message.content.strip()

    raise RuntimeError(
        "OpenAI returned no completion.\n"
        f"{json.dumps(response.model_dump(), indent=2)[:1500]}"
    )


def main() -> None:
    # --- V2.0 UPGRADE: New Branding ---
    st.title("The Stillpoint")
    st.caption(
        "Find your center, find your way. A Wise Friend for a chaotic world."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Check for API key in secrets first
    api_key = None
    if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
        api_key = st.secrets['OPENAI_API_KEY']
    
    # Sidebar remains largely the same, it's well-designed.
    with st.sidebar:
        st.header("Session Settings")
        # Only show API key input if not found in secrets
        if api_key is None:
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                help="Your key stays on this device and is never stored.",
            )
        st.markdown(
            """
            **Tips**
            - Share the situation plainly.
            - Don't hold back the frustration.
            - Describe how it affects your inner calm.
            """,
        )
        st.markdown("---")
        st.markdown(
            "Need an example?\n\n"
            "- *I'm jobless for 6 months... shhiittt!!!*\n"
            "- *I'm stuck replaying a breakup.*\n"
            "- *I crave recognition at work.*"
        )

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input at the bottom
    if user_input := st.chat_input("What is on your mind?"):
        # Validate API key
        if not api_key or not api_key.strip():
            st.error("Add your OpenAI API key in the sidebar to continue.")
            st.stop()
        
        # Add user message to history
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Finding the still point..."):
                try:
                    # Send ENTIRE message history to maintain context
                    reflection = run_inference(api_key, st.session_state.messages)
                    st.markdown(reflection)
                    
                    # Add assistant response to history
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": reflection,
                        }
                    )
                except (OpenAIError, RuntimeError) as exc:
                    st.error("The connection was lost in the storm.")
                    st.code(str(exc))

if __name__ == "__main__":
    main()