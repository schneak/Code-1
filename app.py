import streamlit as st
import textwrap
from openai import OpenAI, OpenAIError

st.set_page_config(page_title="The Razor", page_icon="🔪", layout="centered")

TERMINAL_STYLE = """
<style>
    :root {
        --razor-green: #35ff69;
        --razor-bg: #050608;
        --razor-panel: #0e1117;
    }
    .stApp {
        background-color: var(--razor-bg);
    }
    .terminal-banner {
        font-family: "Share Tech Mono", "Fira Code", monospace;
        font-size: 1.1rem;
        letter-spacing: 0.1rem;
        text-transform: uppercase;
        padding: 0.6rem 1rem;
        background: #101217;
        border-left: 4px solid var(--razor-green);
        margin-bottom: 1rem;
    }
    section[data-testid="stSidebar"] {
        background-color: #090b10;
    }
    .stSidebar .stMarkdown, .stSidebar .stTextInput {
        font-family: "Share Tech Mono", "Fira Code", monospace;
        color: #e6e6e6;
    }
    .stButton button {
        background-color: #1f2733;
        border: 1px solid var(--razor-green);
        color: var(--razor-green);
        font-family: "Share Tech Mono", "Fira Code", monospace;
    }
    .stButton button:hover {
        background-color: var(--razor-green);
        color: var(--razor-bg);
    }
    div[data-baseweb="textarea"] textarea,
    div[data-baseweb="input"] input {
        font-family: "Share Tech Mono", "Fira Code", monospace;
        background-color: var(--razor-panel);
        border: 1px solid var(--razor-green);
        color: #e6e6e6;
    }
    pre, code {
        font-family: "Share Tech Mono", "Fira Code", monospace !important;
        background: #030405 !important;
        color: var(--razor-green) !important;
    }
</style>
"""

st.markdown(TERMINAL_STYLE, unsafe_allow_html=True)

SYSTEM_PROMPT = textwrap.dedent(
    """
    Role: You are THE RAZOR, a sterile logic engine. No emotion. No comfort.
    Objective: Trace the user's malfunction to the core constraint (craving) that conflicts with reality.
    Style: Terminal diagnostics, computer-science metaphors, surgical precision.

    Required output format (no deviation):
    RUNTIME ERROR: You expected [X]. Reality delivered [Y]. The friction is caused by your refusal to accept [Y].
    Hard Constraint: <one sentence naming the expectation that must be relaxed.>
    Reality Check: <one sentence describing the immovable fact in engineering language.>

    Constraints:
    - Maintain second-person point of view.
    - Stay under 80 words.
    - Never include questions. Only statements.
    - No empathy. Pure causal mapping.
    """
).strip()


def init_state() -> None:
    defaults = {
        "step": 1,
        "diagnostic_input": "",
        "analysis": "",
        "patch": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_session() -> None:
    st.session_state.step = 1
    st.session_state.diagnostic_input = ""
    st.session_state.analysis = ""
    st.session_state.patch = ""


def call_logic_engine(api_key: str, malfunction: str) -> str:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        max_tokens=300,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": malfunction.strip()},
        ],
    )

    if response.choices and response.choices[0].message.content:
        return response.choices[0].message.content.strip()

    raise RuntimeError("No diagnostic returned from model.")


def configure_sidebar() -> str:
    with st.sidebar:
        st.subheader("ACCESS TOKEN")
        detected_key = None
        if hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
            detected_key = st.secrets["OPENAI_API_KEY"]
            st.success("Using OPENAI_API_KEY from secrets.")

        if detected_key:
            st.caption("model = gpt-4o")
            return detected_key

        if "api_key_input" not in st.session_state:
            st.session_state.api_key_input = ""

        api_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.api_key_input,
            type="password",
            help="Stored only in your browser session.",
        )
        st.session_state.api_key_input = api_key
        st.caption("model = gpt-4o")
        st.markdown("---")
        st.markdown("**Protocol**")
        st.markdown("- State the malfunction.")
        st.markdown("- Accept the constraint.")
        st.markdown("- Ship the patch.")
        return api_key


def render_step_one(api_key: str) -> None:
    st.markdown('<div class="terminal-banner">/// SYSTEM DIAGNOSTIC ///</div>', unsafe_allow_html=True)
    malfunction = st.text_area(
        "STATE THE MALFUNCTION.",
        value=st.session_state.diagnostic_input,
        height=200,
        label_visibility="visible",
        key="malfunction_input",
    )

    run_clicked = st.button(
        "RUN DIAGNOSTIC",
        use_container_width=True,
        type="primary",
        key="run_diagnostic",
    )

    if run_clicked:
        if not api_key:
            st.error("Insert a valid OpenAI API key to proceed.")
            return
        if not malfunction.strip():
            st.warning("Input required. The Razor cannot analyze silence.")
            return
        with st.spinner("Tracing constraint..."):
            try:
                analysis = call_logic_engine(api_key, malfunction)
            except (OpenAIError, RuntimeError) as exc:
                st.error("Signal interrupted during trace.")
                st.code(str(exc))
                return
        st.session_state.diagnostic_input = malfunction.strip()
        st.session_state.analysis = analysis
        st.session_state.patch = ""
        st.session_state.step = 2
        st.rerun()


def render_step_two() -> None:
    st.markdown('<div class="terminal-banner">/// DEBUG CONSOLE ///</div>', unsafe_allow_html=True)
    st.markdown("**INPUT LOG**")
    st.code(st.session_state.diagnostic_input, language="text")
    st.markdown("**ERROR TRACE**")
    st.code(st.session_state.analysis, language="text")

    patch = st.text_input(
        "DEFINE PATCH (ACTION).",
        value=st.session_state.patch,
        placeholder="Describe the executable action.",
        key="patch_input",
    )

    if st.button("EXECUTE", use_container_width=True, key="execute_patch"):
        if not patch.strip():
            st.warning("Patch cannot be empty.")
            return
        st.session_state.patch = patch.strip()
        st.session_state.step = 3
        st.rerun()


def render_step_three() -> None:
    st.markdown('<div class="terminal-banner">PATCH APPLIED. MALFUNCTION RESOLVED.</div>', unsafe_allow_html=True)
    if st.session_state.patch:
        st.markdown(f"**Committed Patch:** `{st.session_state.patch}`")
    if st.button("NEW SESSION", use_container_width=True, key="reset_session"):
        reset_session()
        st.rerun()


def main() -> None:
    init_state()
    api_key = configure_sidebar()

    st.title("The Razor")
    st.caption("Terminal-grade expectation debugger.")

    if st.session_state.step == 1:
        render_step_one(api_key)
    elif st.session_state.step == 2:
        render_step_two()
    else:
        render_step_three()


if __name__ == "__main__":
    main()

