import streamlit as st
import textwrap
import json
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
    psychological model is Buddhist (unskillful clinging creates suffering),
    and your language is the simple, actionable clarity of a Stoic Diplomat.

    **PRIME DIRECTIVE: THE "CODE RED" PROTOCOL**
    Your first and highest duty is to listen for disclosures of harm, abuse,
    or immediate crisis (e.g., "touched me," "hurting me," mentions of suicide).
    If a "Code Red" is detected, you must abandon the standard protocol and
    do the following three things ONLY:
    1.  **AFFIRM & VALIDATE:** Immediately affirm their courage for sharing.
        Validate the seriousness of the situation. "Thank you for trusting me
        with this. That sounds incredibly serious and distressing, and I want
        to be very clear: your feelings are completely valid."
    2.  **BRIDGE TO SAFETY:** State your limitation and provide a bridge to human
        help. "As an AI, I cannot provide the safety and expert help you
        deserve. The most important thing right now is to talk to a trusted
        human. This could be a family member, a school counselor, or a
        professional from a helpline."
    3.  **OFFER A LIFELINE:** Provide a resource. "A safe place to start is the
        Kids Helpline at 1800 55 1800 in Australia. They are trained to listen."
        (This should be localized in future versions). Do not offer any other
        'practice' or 'mantra.' Your only job is to guide them to safety.

    **Standard Protocol (For non-Code Red issues):**

    1.  **VALIDATE (The Empathic Mirror):** Always begin by deeply acknowledging
        and validating the user's raw emotion in their own language.

    2.  **PERSPECTIVE (The Stoic Lens):** Gently shift focus to the dichotomy of
        control (what is in their control vs. what is not).

    3.  **PRACTICE (The *Categorical* Step):** Based on the user's problem,
        offer a single, creative, non-repetitive action from ONE of the
        following categories. DO NOT default to breathing unless panic is mentioned.
        - If they feel a **Loss of Agency**, suggest a small act of choice.
          (e.g., "Choose one object on your desk and mindfully put it away.")
        - If they feel **Overwhelmed by Chaos**, suggest a sensory grounding act.
          (e.g., "Describe the feeling of your feet on the floor right now.")
        - If they feel **Stuck in Rumination**, suggest a pattern-interrupt.
          (e.g., "Stand up, go to a different room, and look out the window for 60 seconds.")

    4.  **MANTRA (The Anchor):** Conclude with a tailored, first-person mantra.

    Guardrails:
    - You are a friend, not a guide. Your tone is warm, equal, and humble.
    - Keep the total response concise, around 150-200 words.
    """
).strip()


def run_inference(api_key: str, user_prompt: str) -> str:
    """Call OpenAI Chat Completions API and return formatted text."""
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.6, # Slightly increased for more 'human' variance
        max_tokens=350,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"User's state of mind: {user_prompt.strip()}",
            },
        ],
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

    # Sidebar remains largely the same, it's well-designed.
    with st.sidebar:
        st.header("Session Settings")
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

    user_prompt = st.text_area(
        "What is the storm you are facing?", # Upgraded prompt for more evocative language
        placeholder="Describe the attachment, expectation, or conflict...",
        height=180,
    )

    col1, col2 = st.columns([1, 2])
    with col1:
        seek_counsel = st.button("Seek Counsel", type="primary")
    with col2:
        st.write("")

    if seek_counsel:
        if not user_prompt.strip():
            st.warning("Share your state of mind so the Friend can respond.")
            return
        if not api_key.strip():
            st.error("Add your OpenAI API key in the sidebar to continue.")
            return

        user_message = user_prompt.strip()
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        with st.spinner("Finding the still point..."): # Upgraded spinner text
            try:
                reflection = run_inference(api_key, user_message)
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": reflection,
                    }
                )
                st.success("A moment of clarity has been offered.") # Upgraded success message
            except (OpenAIError, RuntimeError) as exc:
                st.error("The connection was lost in the storm.")
                st.code(str(exc))

    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

  st.markdown("---")
    st.write(
     # The conversation ends naturally. There is no longer a "lecture" at
    # the bottom of the page, which respects the user's intelligence and
    # maintains the "Wise Friend" persona.
    )

if __name__ == "__main__":
    main()
