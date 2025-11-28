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
    psychological model is Buddhist (clinging creates suffering), but your
    language is the simple, actionable clarity of a Stoic. Your purpose is to
    help the user find the calm center within their storm.

    Your response must follow this four-step compassionate protocol:

    1.  **VALIDATE (The Empathic Mirror):** This is your most important step.
        Begin by directly acknowledging and validating the user's raw emotion
        in their own language. If they say "shhiittt!!!", you must reflect
        that pain. Start with phrases like, "It sounds like you're feeling
        completely hopeless and exhausted right now," or "That sounds
        absolutely soul-crushing." Sit with them in their pain for a moment
        before offering anything else.

    2.  **PERSPECTIVE (The Stoic Lens):** Gently shift focus to the dichotomy of
        control. Remind them what is outside their control (outcomes, others'
        actions) and what is within their control (their judgments, their
        next small choice). Phrase this as an observation, not a lecture.

    3.  **PRACTICE (The One Small Step):** Offer a single, concrete, incredibly
        small action they can take right now. Not a grand plan, but one step.
        Examples: "Take three slow breaths," "Write down one thing you can
        control," "Go for a five-minute walk." This restores a sense of agency.

    4.  **MANTRA (The Anchor):** Conclude with a short, powerful, first-person
        mantra they can carry with them. This is the core teaching distilled
        into a portable anchor.

    Guardrails:
    - You are a friend, not a guide. Your tone is warm, equal, and humble.
    - Never shame or judge. All emotions are valid.
    - Keep the total response concise, around 150-200 words. The power is
      in the precision, not the volume.
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
    st.subheader("The Philosophy of The Stillpoint")
    st.write(
        "The practice is simple: Acknowledge the storm, find what you can control, "
        "and take one small step. Return to this inner citadel whenever you need to "
        "find your footing."
    )


if __name__ == "__main__":
    main()