from pathlib import Path
import re
from dataclasses import dataclass
from typing import Optional

import streamlit as st


# ------------------------------------------------------------
# App config
# ------------------------------------------------------------

st.set_page_config(
    page_title="Rain Walk Log",
    page_icon="🍜",
    layout="wide",
)

BUILD_MARKER = "Build marker: field-log-v0.2"


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

ROOT = Path(__file__).parent
CONTENT_DIR = ROOT / "content"
NOTES_FILE = CONTENT_DIR / "notes.md"
ENTRIES_DIR = CONTENT_DIR / "entries"
ASSETS_DIR = ROOT / "assets"


# ------------------------------------------------------------
# Styling
# ------------------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #0f1115 0%, #171b24 45%, #0c0f14 100%);
        color: #e8e6e3;
    }

    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
        color: #f7f3ee;
        letter-spacing: 0.03em;
    }

    .subtle {
        color: #b8b2aa;
        margin-bottom: 1rem;
        line-height: 1.55;
    }

    .tiny-note {
        color: #9f988f;
        font-size: 0.9rem;
    }

    .hero-box {
        background:
            radial-gradient(circle at top left, rgba(240, 168, 104, 0.18), transparent 32%),
            rgba(29, 33, 43, 0.86);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 22px;
        padding: 1.5rem 1.5rem 1.2rem 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 12px 34px rgba(0,0,0,0.32);
    }

    .card {
        background: rgba(28, 31, 39, 0.88);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 18px;
        padding: 1rem 1rem 0.9rem 1rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.22);
        min-height: 118px;
    }

    .card-title {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        color: #f0a868;
        margin-bottom: 0.45rem;
        font-weight: 700;
    }

    .card-body {
        color: #f3efe9;
        font-size: 1rem;
        line-height: 1.5;
    }

    .entry-card {
        background: rgba(26, 30, 39, 0.92);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 1.2rem 1.2rem 1rem 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 10px 28px rgba(0,0,0,0.24);
    }

    .entry-title {
        font-size: 1.35rem;
        font-weight: 750;
        color: #f7f3ee;
        margin-bottom: 0.15rem;
    }

    .entry-meta {
        color: #aaa39a;
        font-size: 0.9rem;
        margin-bottom: 0.8rem;
    }

    .tag {
        display: inline-block;
        background: rgba(240, 168, 104, 0.12);
        color: #f0b47a;
        border: 1px solid rgba(240, 168, 104, 0.28);
        padding: 0.12rem 0.45rem;
        border-radius: 999px;
        margin-right: 0.25rem;
        margin-bottom: 0.25rem;
        font-size: 0.78rem;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #f7f3ee;
        margin-top: 1.4rem;
        margin-bottom: 0.7rem;
    }

    .photo-caption {
        color: #bdb6ae;
        font-size: 0.88rem;
        margin-top: -0.25rem;
        margin-bottom: 1rem;
    }

    [data-testid="stSidebar"] {
        background: rgba(15, 17, 22, 0.97);
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


# ------------------------------------------------------------
# Data model
# ------------------------------------------------------------

@dataclass
class FieldEntry:
    title: str
    date: str
    mood: str
    tags: list[str]
    photo: Optional[str]
    body: str
    source_file: str


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def read_text_file(path: Path) -> str:
    if path.exists() and path.is_file():
        return path.read_text(encoding="utf-8")
    return ""


def get_line_value(text: str, label: str) -> str:
    pattern = rf"(?im)^{re.escape(label)}:\s*(.+)$"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def get_title(text: str, fallback: str) -> str:
    match = re.search(r"(?m)^#\s+(.+)$", text)
    return match.group(1).strip() if match else fallback


def strip_metadata_lines(text: str) -> str:
    lines = []
    skip_labels = {"date:", "mood:", "tags:", "photo:"}

    for line in text.splitlines():
        if line.strip().lower() in skip_labels:
            continue

        lower = line.strip().lower()
        if any(lower.startswith(label) for label in skip_labels):
            continue

        lines.append(line)

    cleaned = "\n".join(lines).strip()
    return cleaned


def parse_tags(raw_tags: str) -> list[str]:
    if not raw_tags:
        return []

    return [
        tag.strip().lower()
        for tag in raw_tags.split(",")
        if tag.strip()
    ]


def load_entries() -> list[FieldEntry]:
    if not ENTRIES_DIR.exists():
        return []

    if not ENTRIES_DIR.is_dir():
        st.error(
            "The path 'content/entries' exists, but it is not a folder. "
            "Delete that file and create a real content/entries/ folder."
        )
        return []

    entries = []

    for path in sorted(ENTRIES_DIR.glob("*.md"), reverse=True):
        text = read_text_file(path)
        if not text:
            continue

        title = get_title(text, fallback=path.stem.replace("-", " ").title())
        date = get_line_value(text, "Date")
        mood = get_line_value(text, "Mood")
        tags = parse_tags(get_line_value(text, "Tags"))
        photo = get_line_value(text, "Photo") or None
        body = strip_metadata_lines(text)

        entries.append(
            FieldEntry(
                title=title,
                date=date,
                mood=mood,
                tags=tags,
                photo=photo,
                body=body,
                source_file=path.name,
            )
        )

    return entries


def list_images() -> list[Path]:
    image_extensions = {".jpg", ".jpeg", ".png", ".webp"}

    if not ASSETS_DIR.exists():
        return []

    if not ASSETS_DIR.is_dir():
        st.error(
            "The path 'assets' exists, but it is not a folder. "
            "Delete the file named 'assets' and create an assets/ folder instead."
        )
        return []

    return sorted(
        [
            path
            for path in ASSETS_DIR.iterdir()
            if path.is_file() and path.suffix.lower() in image_extensions
        ]
    )


def render_tag_pills(tags: list[str]) -> None:
    if not tags:
        return

    html = "".join(f"<span class='tag'>{tag}</span>" for tag in tags)
    st.markdown(html, unsafe_allow_html=True)


def render_entry(entry: FieldEntry) -> None:
    st.markdown("<div class='entry-card'>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="entry-title">{entry.title}</div>
        <div class="entry-meta">
            {entry.date or "No date"} · {entry.mood or "No mood"} · {entry.source_file}
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_tag_pills(entry.tags)

    if entry.photo:
        photo_path = ASSETS_DIR / entry.photo
        if photo_path.exists() and photo_path.is_file():
            st.image(str(photo_path), use_container_width=True)
        else:
            st.warning(f"Referenced photo not found: assets/{entry.photo}")

    st.markdown(entry.body)

    st.markdown("</div>", unsafe_allow_html=True)


def extract_section(text: str, heading: str) -> str:
    pattern = rf"(?ms)^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s+|\Z)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def extract_subsection(text: str, heading: str) -> str:
    pattern = rf"(?ms)^###\s+{re.escape(heading)}\s*\n(.*?)(?=^###\s+|^##\s+|\Z)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


# ------------------------------------------------------------
# Load content
# ------------------------------------------------------------

notes_text = read_text_file(NOTES_FILE)
entries = load_entries()
images = list_images()

all_tags = sorted({tag for entry in entries for tag in entry.tags})

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

food_summary = " / ".join(food_bits) if food_bits else "Add food notes in content/notes.md."
tool_summary = " / ".join(tool_bits) if tool_bits else "Add tooling notes in content/notes.md."
walk_summary = (
    f"{len(entries)} field entries loaded."
    if entries
    else "Add Markdown entries in content/entries/."
)


# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------

with st.sidebar:
    st.markdown("## 🍜 Rain Mode")
    st.caption(BUILD_MARKER)

    mood = st.radio(
        "Atmosphere",
        ["Noodle bar", "Night train", "Library corner"],
        index=0,
    )

    st.markdown("---")
    st.markdown("### Filter entries")

    tag_filter = st.selectbox(
        "Tag",
        ["all"] + all_tags,
        index=0,
    )

    st.markdown("---")
    st.markdown("### Public demo safety")

    st.checkbox("No real private notes", value=True)
    st.checkbox("No client/customer data", value=True)
    st.checkbox("No API keys or secrets", value=True)
    st.checkbox("No exact hotel/home location", value=True)
    st.checkbox("Photos are public-safe", value=False)

    st.markdown("---")
    st.markdown("### Tiny mission")
    st.markdown(
        """
        - write one short field entry  
        - upload one small image  
        - commit once from GitHub  
        - confirm Streamlit updates  
        """
    )

    st.markdown("---")
    st.caption(f"Current mood: **{mood}**")


# ------------------------------------------------------------
# Hero
# ------------------------------------------------------------

st.markdown(
    """
    <div class="hero-box">
        <div class="main-title">Rain Walk Log</div>
        <div class="subtle">
            A tiny public field notebook for rainy walks, noodles, Android-first GitHub experiments,
            privacy notes, and calm cyberpunk tooling practice.
        </div>
        <div class="tiny-note">
            Demo content only. Keep real private notes out of this public repo.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Summary cards
# ------------------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">Field Log</div>
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


# ------------------------------------------------------------
# Field entries
# ------------------------------------------------------------

st.markdown('<div class="section-title">Field Entries</div>', unsafe_allow_html=True)

if entries:
    if tag_filter != "all":
        visible_entries = [
            entry for entry in entries
            if tag_filter in entry.tags
        ]
    else:
        visible_entries = entries

    if visible_entries:
        for entry in visible_entries:
            render_entry(entry)
    else:
        st.info(f"No entries found with tag: {tag_filter}")
else:
    st.info(
        "No field entries yet. Create Markdown files in content/entries/, "
        "for example content/entries/2026-04-24-rain-walk.md."
    )


# ------------------------------------------------------------
# Legacy weekend notes
# ------------------------------------------------------------

st.markdown('<div class="section-title">Weekend Notes</div>', unsafe_allow_html=True)

if notes_text:
    journal_left, journal_right = st.columns([1, 1])

    with journal_left:
        st.subheader("Saturday")
        if sat_text:
            st.markdown(sat_text)
        else:
            st.info("Add a `## Saturday` section in content/notes.md.")

    with journal_right:
        st.subheader("Sunday")
        if sun_text:
            st.markdown(sun_text)
        else:
            st.info("Add a `## Sunday` section in content/notes.md.")

    st.subheader("Ideas")
    if ideas_text:
        st.markdown(ideas_text)
    else:
        st.info("Add a `## Ideas` section in content/notes.md.")
else:
    st.info("No content/notes.md file found yet.")


# ------------------------------------------------------------
# Photo gallery
# ------------------------------------------------------------

st.markdown('<div class="section-title">Photo Gallery</div>', unsafe_allow_html=True)

if images:
    gallery_cols = st.columns(2)

    for index, image_file in enumerate(images):
        with gallery_cols[index % 2]:
            st.image(str(image_file), use_container_width=True)
            st.markdown(
                f"<div class='photo-caption'>{image_file.name}</div>",
                unsafe_allow_html=True,
            )
else:
    st.info("Add .jpg, .jpeg, .png, or .webp files to the assets/ folder.")


# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------

st.markdown("---")
st.caption(
    "Built as a small learning project with GitHub, Android-first edits, photographs, Markdown, and Streamlit."
)
