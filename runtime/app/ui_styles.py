import streamlit as st

from runtime.app.config import THEME_TOKENS


def get_effective_theme(theme_selection):

    if theme_selection == "Light":
        return "light"

    if theme_selection == "Dark":
        return "dark"

    configured_theme = (
        st.get_option("theme.base")
        or "light"
    ).lower()

    return (
        "dark"
        if configured_theme == "dark"
        else "light"
    )


def get_requested_theme():

    if "theme_selector" in st.session_state:
        return st.session_state["theme_selector"]

    return st.session_state.get(
        "ui_theme",
        "Auto",
    )


def inject_global_styles(theme_mode):

    tokens = THEME_TOKENS[theme_mode]

    st.markdown(
        f"""
        <style>
        :root {{
            --app-bg: {tokens["background"]};
            --surface: {tokens["surface"]};
            --surface-alt: {tokens["surface_alt"]};
            --sidebar: {tokens["sidebar"]};
            --sidebar-surface: {tokens["sidebar_surface"]};
            --border: {tokens["border"]};
            --text: {tokens["text"]};
            --muted: {tokens["muted"]};
            --accent: {tokens["accent"]};
            --accent-alt: {tokens["accent_alt"]};
            --success: {tokens["success"]};
            --error: {tokens["error"]};
            --warning: {tokens["warning"]};
            --shadow: {tokens["shadow"]};
            --hero-ring: {tokens["hero_ring"]};
            --hero-glow: {tokens["hero_glow"]};
            --radius-xl: 22px;
            --radius-lg: 18px;
            --radius-md: 14px;
            --radius-sm: 10px;
            --content-gutter: clamp(0.8rem, 1.15vw, 1.15rem);
            --sidebar-width: clamp(230px, 18vw, 248px);
        }}

        html, body, [data-testid="stAppViewContainer"], .stApp {{
            background:
                radial-gradient(circle at top right, var(--hero-glow), transparent 20%),
                linear-gradient(180deg, var(--app-bg) 0%, color-mix(in srgb, var(--app-bg) 93%, #ffffff 7%) 100%);
            color: var(--text);
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        [data-testid="stSidebar"] {{
            background:
                radial-gradient(circle at top left, rgba(255,255,255,0.05), transparent 26%),
                linear-gradient(180deg, var(--sidebar) 0%, var(--sidebar-surface) 100%);
            border-right: 1px solid var(--border);
            min-width: var(--sidebar-width) !important;
            max-width: var(--sidebar-width) !important;
        }}

        [data-testid="stSidebar"] * {{
            color: var(--text);
        }}

        .main .block-container {{
            max-width: none;
            width: 100%;
            padding-top: 0.75rem;
            padding-bottom: 1.2rem;
            padding-left: var(--content-gutter);
            padding-right: var(--content-gutter);
        }}

        [data-testid="stHorizontalBlock"] {{
            gap: 0.7rem;
        }}

        [data-testid="column"] {{
            min-width: 0;
        }}

        h1, h2, h3, h4, h5, h6, p, span, label, div {{
            color: inherit;
        }}

        .app-header-compact,
        .section-card-compact {{
            border-radius: var(--radius-lg);
            border: 1px solid var(--border);
            background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
            box-shadow: var(--shadow);
        }}

        .app-header-compact {{
            padding: 0.85rem 1rem;
            margin-bottom: 0.55rem;
            background:
                radial-gradient(circle at top right, var(--hero-ring), transparent 24%),
                linear-gradient(135deg, var(--surface) 0%, var(--surface-alt) 100%);
        }}

        .header-grid {{
            display: grid;
            grid-template-columns: minmax(0, 2fr) minmax(180px, 0.7fr);
            gap: 0.75rem;
            align-items: stretch;
        }}

        .header-kicker {{
            font-size: 0.69rem;
            text-transform: uppercase;
            letter-spacing: 0.18em;
            color: var(--muted);
            font-weight: 700;
            margin-bottom: 0.16rem;
        }}

        .header-title {{
            font-size: clamp(1.22rem, 1.55vw, 1.65rem);
            line-height: 1.02;
            font-weight: 700;
            margin: 0 0 0.16rem 0;
        }}

        .header-copy {{
            color: var(--muted);
            font-size: 0.8rem;
            line-height: 1.38;
            margin: 0;
            max-width: 720px;
        }}

        .chip-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
            margin-top: 0.5rem;
        }}

        .status-chip {{
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            border-radius: 999px;
            padding: 0.28rem 0.55rem;
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.14);
            color: var(--muted);
            font-size: 0.7rem;
            font-weight: 700;
        }}

        .status-chip.success {{
            color: var(--success);
        }}

        .status-chip.error {{
            color: var(--error);
        }}

        .status-chip.warning {{
            color: var(--warning);
        }}

        .header-aside {{
            border-radius: 16px;
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.08);
            padding: 0.72rem 0.8rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 0.34rem;
        }}

        .header-aside-label {{
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.14em;
            color: var(--muted);
            font-weight: 700;
        }}

        .header-aside-value {{
            font-size: 1.25rem;
            font-weight: 700;
            line-height: 1;
        }}

        .header-aside-copy {{
            font-size: 0.74rem;
            line-height: 1.35;
            color: var(--muted);
        }}

        .section-card-compact {{
            padding: 0.78rem 0.88rem;
            margin-bottom: 0.58rem;
        }}

        .section-caption {{
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            color: var(--muted);
            margin-bottom: 0.12rem;
            font-weight: 700;
        }}

        .section-title {{
            font-size: 0.98rem;
            line-height: 1.18;
            margin: 0 0 0.14rem 0;
            font-weight: 700;
        }}

        .section-copy {{
            color: var(--muted);
            font-size: 0.79rem;
            line-height: 1.38;
            margin: 0;
        }}

        .upload-panel-compact {{
            border-radius: var(--radius-lg);
            border: 1px solid var(--border);
            background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
            padding: 0.78rem 0.88rem;
            box-shadow: var(--shadow);
            margin-bottom: 0.58rem;
        }}

        .primary-action-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.6rem;
            margin-top: 0.35rem;
        }}

        .inline-note {{
            color: var(--muted);
            font-size: 0.74rem;
            line-height: 1.35;
            margin-top: 0.24rem;
        }}

        div[data-testid="stFileUploader"] {{
            border: 1.5px dashed var(--accent);
            background: linear-gradient(180deg, rgba(255,255,255,0.16), rgba(255,255,255,0.04));
            border-radius: 18px;
            padding: 0.48rem;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
        }}

        div[data-testid="stFileUploader"] section {{
            padding: 0.12rem;
            min-height: 4rem;
        }}

        div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {{
            padding: 0.08rem !important;
        }}

        div.stButton > button,
        div[data-testid="stDownloadButton"] > button {{
            border-radius: 12px;
            border: 1px solid transparent;
            background: linear-gradient(180deg, var(--accent) 0%, var(--accent-alt) 100%);
            color: #FFFFFF;
            font-weight: 700;
            min-height: 2.55rem;
            box-shadow: 0 10px 20px rgba(31, 90, 166, 0.2);
            transition: transform 120ms ease, box-shadow 120ms ease;
            line-height: 1.2;
        }}

        div.stButton > button:hover,
        div[data-testid="stDownloadButton"] > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 14px 24px rgba(31, 90, 166, 0.28);
        }}

        div.stButton > button[kind="secondary"] {{
            background: linear-gradient(180deg, var(--surface) 0%, rgba(255,255,255,0.03) 100%);
            color: var(--text);
            border-color: var(--border);
            box-shadow: 0 8px 16px rgba(15, 23, 42, 0.08);
        }}

        .st-key-clear_session_button button {{
            background: linear-gradient(180deg, #C63D4F 0%, #A82F42 100%) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.45rem;
            margin-bottom: 0.45rem;
            flex-wrap: wrap;
        }}

        .stTabs [data-baseweb="tab"] {{
            min-height: 2.45rem;
            background: linear-gradient(180deg, rgba(255,255,255,0.14), rgba(255,255,255,0.04));
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 0.42rem 0.84rem;
            color: var(--text);
            font-weight: 700;
            font-size: 0.8rem;
        }}

        .stTabs [aria-selected="true"] {{
            color: #FFFFFF !important;
            background: linear-gradient(180deg, var(--accent) 0%, var(--accent-alt) 100%) !important;
            border-color: transparent !important;
        }}

        div[data-testid="stDataFrame"] {{
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid var(--border);
            box-shadow: var(--shadow);
            background: var(--surface);
        }}

        div[data-testid="stDataFrame"] [role="columnheader"] {{
            background: color-mix(in srgb, var(--surface-alt) 76%, var(--surface) 24%) !important;
            color: var(--text) !important;
            font-weight: 700 !important;
        }}

        .export-table {{
            border-radius: 14px;
            border: 1px solid var(--border);
            overflow: hidden;
            box-shadow: var(--shadow);
        }}

        .export-row {{
            display: grid;
            grid-template-columns: minmax(0, 2.2fr) minmax(120px, 1fr) minmax(90px, 0.7fr) minmax(150px, 1fr) 132px;
            gap: 0.6rem;
            align-items: center;
            padding: 0.7rem 0.82rem;
            border-bottom: 1px solid var(--border);
            background: var(--surface);
        }}

        .export-row.header {{
            background: color-mix(in srgb, var(--surface-alt) 70%, var(--surface) 30%);
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--muted);
            font-weight: 700;
        }}

        .export-cell {{
            font-size: 0.8rem;
            min-width: 0;
            overflow-wrap: anywhere;
        }}

        .sidebar-logo-shell {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            padding: 0.58rem 0.72rem;
            border-radius: 16px;
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border);
            margin-bottom: 0.5rem;
        }}

        .sidebar-logo-shell img {{
            width: 100%;
            max-width: 152px;
            height: auto;
            object-fit: contain;
        }}

        .sidebar-note {{
            color: var(--muted);
            font-size: 0.72rem;
            line-height: 1.35;
            margin: 0.2rem 0 0.45rem 0;
        }}

        .path-chip {{
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            padding: 0.38rem 0.58rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border);
            color: var(--muted);
            font-size: 0.72rem;
            margin: 0.16rem 0.3rem 0 0;
        }}

        @media (max-width: 980px) {{
            .header-grid,
            .export-row {{
                grid-template-columns: 1fr;
            }}

            [data-testid="stSidebar"] {{
                min-width: auto !important;
                max-width: none !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
