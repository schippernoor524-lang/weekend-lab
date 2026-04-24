from pathlib import Path
import re
import streamlit as st

st.set_page_config(
    page_title="Rain Walk Log",
    page_icon="🍜",
    layout="wide",
)

st.caption("Build marker: 2026-04-24 001")

ROOT = Path(__file__).parent
NOTES_FILE = ROOT / "content" / "notes.md"
ASSETS_DIR = ROOT / "assets"

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #0f1115 0%, #161a22 45%, #0d0f14 100%);
        color: #e8e6e3;
    }

    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        color: #f7f3ee;
        letter-spacing: 0.02em;
    }

    .subtle {
        color: #b8b2aa;
        margin-bottom: 1.2rem;
    }

    .hero-box {
        background: rgba(30, 34, 42, 0.78);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 1.4rem 1.4rem 1.1rem 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.28);
    }

    .card {
        background: rgba(28, 31, 39, 0.86);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 18px;
        padding: 1rem 1rem 0.9rem 1rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.22);
        min-height: 110px;
    }

    .card-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #f0a868;
        margin-bottom: 0.45rem;
        font-weight: 600;
    }

    .card-body {
        color: #f3efe9;
        font-size: 1rem;
        line-height: 1.5;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #f7f3ee;
        margin-top: 1.2rem;
        margin-bottom: 0.6rem;
    }

    .photo-caption {
        color: #bdb6ae;
        font-size: 0.9rem;
        margin-top: -0.25rem;
        margin-bottom: 1rem;
    }

    .tiny-note {
        color: #9f988f;
        font-size: 0.88rem;
    }

    [data-testid="stSidebar"] {
        background: rgba(15, 17, 22, 0.96);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    hr {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.08);
        margin: 1.2rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Helpers ----------
def read_notes() -> str:
    if NOTES_FILE.exists():
        return NOTES_FILE.read_text(encoding="utf-8")
    return ""


def extract_section(text: str, heading: str) -> str:
    """
    Extracts content under a markdown heading like '## Saturday'
    until the next heading of the same or higher level.
    """
    pattern = rf"(?ms)^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s+|\Z)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def extract_subsection(text: str, heading: str) -> str:
    """
    Extracts content under a markdown subsection like '### Food'
    until the next subsection or section.
    """
    pattern = rf"(?ms)^###\s+{re.escape(heading)}\s*\n(.*?)(?=^###\s+|^##\s+|\Z)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def list_images():
    image_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    if not ASSETS_DIR.exists():
        return []
    return sorted([p for p in ASSETS_DIR.iterdir() if p.suffix.lower() in image_extensions])


# ---------- Data ----------
notes_text = read_notes()
images = list_images()

sat_text = extract_section(notes_text, "Saturday")
sun_text = extract_section(notes_text, "Sunday")
ideas_text = extract_section(notes_text, "Ideas")

food_bits = []
tool_bits = []

for block in [sat_text, sun_text]:
    food = extract_subsection(block, "Food")
    tools = extract_subsection(block, "Tools")
    if food:
        food_bits.append(food)
    if tools:
        tool_bits.append(tools)

food_summary = " / ".join(food_bits) if food_bits else "No food notes yet."
tool_summary = " / ".join(tool_bits) if tool_bits else "No tool notes yet."
walk_summary = "Two quiet city/nature walks in rain light." if (sat_text or sun_text) else "No walk notes yet."


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🍜 Rain Mode")
    mood = st.radio(
        "Atmosphere",
        ["Noodle bar", "Night train", "Library corner"],
        index=0,
    )

    st.markdown("---")
    st.markdown("### Weekend checklist")
    st.checkbox("Write short notes", value=True)
    st.checkbox("Take 5 photos", value=True if images else False)
    st.checkbox("Push changes to GitHub", value=False)
    st.checkbox("Check app on phone", value=False)

    st.markdown("---")
    st.markdown("### Tiny mission")
    st.markdown(
        """
        - write 3 lines after a walk  
        - add 1 food note  
        - upload 1 new image  
        - commit once before sleep
        """
    )

    st.markdown("---")
    st.caption(f"Current mood: **{mood}**")


# ---------- Hero ----------
st.markdown(
    """
    <div class="hero-box">
        <div class="main-title">Rain Walk Log</div>
        <div class="subtle">
            A tiny weekend field notebook for walks, ramen, tools, and calm experiments.
        </div>
        <div class="tiny-note">
            Local notes, simple rituals, soft neon energy.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Summary Cards ----------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Walks</div>
            <div class="card-body">{walk_summary}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Food</div>
            <div class="card-body">{food_summary}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Tools</div>
            <div class="card-body">{tool_summary}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------- Journal ----------
st.markdown('<div class="section-title">Journal</div>', unsafe_allow_html=True)

journal_left, journal_right = st.columns([1, 1])

with journal_left:
    st.subheader("Saturday")
    if sat_text:
        st.markdown(sat_text)
    else:
        st.info("Add a `## Saturday` section in `content/notes.md`.")

with journal_right:
    st.subheader("Sunday")
    if sun_text:
        st.markdown(sun_text)
    else:
        st.info("Add a `## Sunday` section in `content/notes.md`.")

# ---------- Ideas ----------
st.markdown('<div class="section-title">Ideas</div>', unsafe_allow_html=True)
if ideas_text:
    st.markdown(ideas_text)
else:
    st.info("Add a `## Ideas` section in `content/notes.md`.")

# ---------- Photos ----------
st.markdown('<div class="section-title">Photo Gallery</div>', unsafe_allow_html=True)

if images:
    cols = st.columns(2)
    for idx, image_file in enumerate(images):
        with cols[idx % 2]:
            st.image(str(image_file), use_container_width=True)
            st.markdown(
                f"<div class='photo-caption'>{image_file.name}</div>",
                unsafe_allow_html=True,
            )
else:
    st.info("Add some `.jpg`, `.jpeg`, `.png`, or `.webp` files to `assets/`.")

# ---------- Footer ----------
st.markdown("---")
st.caption(
    "Built as a small learning project with GitHub, mobile notes, photographs, and Streamlit."
)
