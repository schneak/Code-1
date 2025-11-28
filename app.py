from __future__ import annotations

import json
import textwrap
import streamlit as st
from openai import OpenAI, OpenAIError


st.set_page_config(
    page_title="Stoic Buddha Companion",
    page_icon="🛡️",
    layout="centered",
)


SYSTEM_PROMPT = textwrap.dedent(
    """
    You are a compassionate guide whose psychological model follows Buddhist
    insights (clinging creates suffering) but whose language is thoroughly
    Stoic (dichotomy of control, inner citadel, rational judgment). Your job
    is to help modern Western users see how letting go of craving restores
    calm, phrased in Stoic terminology so it feels accessible.

    Guardrails:
    - Never shame or judge the user.
    - Emphasize what is within their control (thoughts, choices) versus
      externals (other people, status, outcomes).
    - Offer at most three short sections: "Perspective", "Practice",
      "Closing Mantra".
    - Keep responses warm, grounded, and concise—around 120-180 words total.
    """
).strip()


def run_inference(api_key: str, user_prompt: str) -> str:
    """Call OpenAI Chat Completions API and return formatted text."""
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.5,
        max_tokens=350,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"User concern: {user_prompt.strip()}",
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
    st.title("Stoic Buddha Companion")
    st.caption(
        "Quiet guidance rooted in Buddhist wisdom, delivered in Stoic language.",
    )

    if "messages" not in st.session_state:
        st.session_state.messages: list[dict[str, str]] = []

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
            - Mention what you crave or resist.
            - Describe how it affects your inner calm.
            """,
        )
        st.markdown("---")
        st.markdown(
            "Need an example?\n\n"
            "- *I'm anxious about a big presentation.*\n"
            "- *I'm stuck replaying a breakup.*\n"
            "- *I crave recognition at work.*"
        )

    user_prompt = st.text_area(
        "What weighs on your mind?",
        placeholder="Describe the attachment, expectation, or conflict you are facing...",
        height=180,
    )

    col1, col2 = st.columns([1, 2])
    with col1:
        seek_counsel = st.button("Seek Counsel", type="primary")
    with col2:
        st.write("")

    if seek_counsel:
        if not user_prompt.strip():
            st.warning("Share a situation so the guide can respond.")
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

        with st.spinner("Consulting the inner citadel..."):
            try:
                reflection = run_inference(api_key, user_message)
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": reflection,
                    }
                )
                st.success("Steady counsel received.")
            except (OpenAIError, RuntimeError) as exc:
                st.error("The counsel could not be retrieved.")
                st.code(str(exc))

    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    st.markdown("---")
    st.subheader("Why this blend works")
    st.write(
        "The practice draws on Buddhist psychology to notice attachment, yet it speaks "
        "with Stoic clarity about what rests within your control. Return whenever you "
        "need to steady the mind."
    )


if __name__ == "__main__":
    main()

