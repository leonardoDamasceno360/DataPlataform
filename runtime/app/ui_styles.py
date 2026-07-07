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
            --radius-lg: 18px;
            --radius-md: 14px;
            --radius-sm: 10px;
            --content-gutter: clamp(1rem, 1.4vw, 1.4rem);
            --sidebar-width: clamp(224px, 16.5vw, 242px);
            --soft-border: color-mix(in srgb, var(--border) 82%, transparent);
            --soft-fill: color-mix(in srgb, var(--surface) 92%, var(--surface-alt) 8%);
            --panel-fill: color-mix(in srgb, var(--surface) 95%, var(--surface-alt) 5%);
            --panel-fill-strong: color-mix(in srgb, var(--surface) 88%, var(--surface-alt) 12%);
        }}

        html, body, [data-testid="stAppViewContainer"], .stApp {{
            background:
                radial-gradient(circle at top right, var(--hero-glow), transparent 18%),
                linear-gradient(180deg, var(--app-bg) 0%, color-mix(in srgb, var(--app-bg) 96%, #ffffff 4%) 100%);
            color: var(--text);
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        [data-testid="stSidebar"] {{
            background:
                radial-gradient(circle at top left, rgba(255,255,255,0.04), transparent 24%),
                linear-gradient(180deg, var(--sidebar) 0%, var(--sidebar-surface) 100%);
            border-right: 1px solid var(--soft-border);
            min-width: var(--sidebar-width) !important;
            max-width: var(--sidebar-width) !important;
        }}

        [data-testid="stSidebar"] * {{
            color: var(--text);
        }}

        .main .block-container {{
            max-width: 1240px;
            width: 100%;
            padding-top: 0.82rem;
            padding-bottom: 1.2rem;
            padding-left: var(--content-gutter);
            padding-right: var(--content-gutter);
        }}

        [data-testid="stHorizontalBlock"] {{
            gap: 0.72rem;
        }}

        [data-testid="column"] {{
            min-width: 0;
        }}

        h1, h2, h3, h4, h5, h6, p, span, label, div {{
            color: inherit;
        }}

        .app-header-compact {{
            margin-bottom: 1.2rem;
            padding: 0.28rem 0.1rem 1.1rem 0.1rem;
            border-bottom: 1px solid var(--soft-border);
        }}

        .header-inline {{
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            gap: 1.25rem;
        }}

        .header-kicker {{
            font-size: 0.74rem !important;
            text-transform: uppercase;
            letter-spacing: 0.18em;
            color: var(--muted);
            font-weight: 800;
            margin-bottom: 0.32rem;
        }}

        h1.header-title {{
            font-size: clamp(2.85rem, 4.6vw, 4.3rem) !important;
            line-height: 0.96 !important;
            font-weight: 800 !important;
            letter-spacing: -0.045em !important;
            margin: 0 0 0.72rem 0 !important;
        }}

        p.header-copy {{
            color: var(--muted);
            font-size: 1.12rem !important;
            line-height: 1.38 !important;
            margin: 0 !important;
            max-width: 720px;
        }}

        .header-flow-line {{
            white-space: nowrap;
            color: var(--muted);
            font-size: 0.82rem !important;
            line-height: 1.2;
            padding-bottom: 0.2rem;
        }}

        .header-flow-line span {{
            margin: 0 0.22rem;
            color: var(--accent);
            font-weight: 700;
        }}

        .section-card-compact {{
            padding: 0.9rem 1rem;
            margin-bottom: 0.7rem;
            border-radius: var(--radius-lg);
            border: 1px solid var(--soft-border);
            background: var(--panel-fill);
            box-shadow: 0 10px 26px rgba(15, 23, 42, 0.035);
        }}

        .section-caption {{
            font-size: 0.72rem !important;
            text-transform: uppercase;
            letter-spacing: 0.18em;
            color: var(--muted);
            margin-bottom: 0.22rem;
            font-weight: 800;
        }}

        h2.section-title,
        h3.section-title {{
            font-size: 1.34rem !important;
            line-height: 1.14 !important;
            margin: 0 0 0.28rem 0 !important;
            font-weight: 800 !important;
            letter-spacing: -0.02em;
        }}

        p.section-copy {{
            color: var(--muted);
            font-size: 0.96rem !important;
            line-height: 1.45 !important;
            margin: 0 !important;
        }}

        .upload-guidance {{
            color: var(--muted);
            font-size: 0.8rem !important;
            line-height: 1.2;
            margin-top: 0.22rem;
            margin-bottom: 0.6rem;
        }}

        .inline-note {{
            color: var(--muted);
            font-size: 0.84rem !important;
            line-height: 1.35;
            margin-top: 0.1rem;
        }}

        div[data-testid="stFileUploader"] + div[data-testid="stButton"] {{
            display: flex;
            align-items: stretch;
        }}

        div[data-testid="stFileUploader"] {{
            border: 1px solid color-mix(in srgb, var(--soft-border) 68%, transparent);
            background: var(--panel-fill);
            border-radius: 16px;
            padding: 0.28rem 0.36rem;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.03);
            margin: 0;
        }}

        div[data-testid="stFileUploader"] section {{
            padding: 0.08rem;
            min-height: 3.08rem;
        }}

        div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {{
            padding: 0.08rem !important;
            border: none !important;
            background: transparent !important;
        }}

        div[data-testid="stFileUploader"] button {{
            border-radius: 12px !important;
            border: 1px solid color-mix(in srgb, var(--soft-border) 54%, transparent) !important;
            background: color-mix(in srgb, var(--surface) 98%, var(--surface-alt) 2%) !important;
            color: var(--text) !important;
            box-shadow: none !important;
            min-height: 2.48rem !important;
            padding: 0.42rem 1.1rem !important;
            font-size: 0.98rem !important;
            font-weight: 700 !important;
        }}

        div[data-testid="stFileUploader"] small,
        div[data-testid="stFileUploader"] span,
        div[data-testid="stFileUploader"] p {{
            color: var(--muted) !important;
            font-size: 0.94rem !important;
        }}

        div.stButton > button,
        div[data-testid="stDownloadButton"] > button {{
            border-radius: var(--radius-md);
            border: 1px solid transparent;
            background: linear-gradient(180deg, var(--accent) 0%, var(--accent-alt) 100%);
            color: #FFFFFF;
            font-weight: 700;
            min-height: 2.45rem;
            box-shadow: 0 8px 18px rgba(31, 90, 166, 0.18);
            transition: transform 120ms ease, box-shadow 120ms ease;
            line-height: 1.14;
        }}

        div.stButton > button:hover,
        div[data-testid="stDownloadButton"] > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 12px 22px rgba(31, 90, 166, 0.22);
        }}

        .st-key-process_button button {{
            font-size: 1rem !important;
            min-height: 2.74rem !important;
            font-weight: 800 !important;
            min-width: 196px !important;
            max-width: 236px !important;
            width: 100% !important;
            color: #FFFFFF !important;
            background: linear-gradient(180deg, var(--accent) 0%, var(--accent-alt) 100%) !important;
            border-color: transparent !important;
            box-shadow: 0 12px 22px rgba(31, 90, 166, 0.24) !important;
        }}

        .st-key-process_button button *,
        .st-key-process_button button div,
        .st-key-process_button button p,
        .st-key-process_button button span {{
            color: #FFFFFF !important;
        }}

        .st-key-process_button button:hover {{
            background: linear-gradient(180deg, color-mix(in srgb, var(--accent) 88%, #000000 12%) 0%, color-mix(in srgb, var(--accent-alt) 88%, #000000 12%) 100%) !important;
            box-shadow: 0 14px 24px rgba(31, 90, 166, 0.26) !important;
        }}

        .st-key-process_button button:disabled {{
            background: color-mix(in srgb, var(--surface-alt) 70%, var(--surface) 30%) !important;
            color: var(--muted) !important;
            border-color: var(--soft-border) !important;
            box-shadow: none !important;
        }}

        .st-key-process_button button:disabled * {{
            color: var(--muted) !important;
        }}

        div.stButton > button[kind="secondary"] {{
            background: var(--soft-fill);
            color: var(--text);
            border-color: var(--soft-border);
            box-shadow: none;
        }}

        div[data-testid="stPopover"] > button,
        button[data-testid="baseButton-secondary"] {{
            border-radius: var(--radius-md) !important;
            border: 1px solid var(--soft-border) !important;
            background: color-mix(in srgb, var(--surface) 95%, var(--surface-alt) 5%) !important;
            color: var(--text) !important;
            box-shadow: none !important;
        }}

        div[data-baseweb="select"] > div,
        div[data-baseweb="base-input"] > div {{
            background: color-mix(in srgb, var(--surface) 95%, var(--surface-alt) 5%) !important;
            border-color: var(--soft-border) !important;
            color: var(--text) !important;
        }}

        .st-key-clear_session_button button {{
            background: color-mix(in srgb, var(--surface) 92%, #C63D4F 8%) !important;
            color: var(--text) !important;
            border: 1px solid var(--soft-border) !important;
            box-shadow: none !important;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.44rem;
            margin-bottom: 0.32rem;
            flex-wrap: wrap;
        }}

        .stTabs [data-baseweb="tab"] {{
            min-height: 2rem;
            background: color-mix(in srgb, var(--surface) 95%, var(--surface-alt) 5%);
            border: 1px solid var(--soft-border);
            border-radius: 999px;
            padding: 0.18rem 0.72rem;
            color: var(--text);
            font-weight: 700;
            font-size: 0.76rem;
            box-shadow: none !important;
        }}

        .stTabs [aria-selected="true"] {{
            color: #FFFFFF !important;
            background: linear-gradient(180deg, var(--accent) 0%, var(--accent-alt) 100%) !important;
            border-color: transparent !important;
        }}

        div[data-testid="stDataFrame"] {{
            border-radius: var(--radius-lg);
            overflow: hidden;
            border: 1px solid var(--soft-border);
            box-shadow: 0 10px 26px rgba(15, 23, 42, 0.04);
            background: var(--surface);
        }}

        div[data-testid="stDataFrame"] [role="columnheader"] {{
            background: color-mix(in srgb, var(--surface-alt) 76%, var(--surface) 24%) !important;
            color: var(--text) !important;
            font-weight: 700 !important;
            font-size: 0.78rem !important;
        }}

        div[data-testid="stDataFrame"] [role="gridcell"] {{
            font-size: 0.79rem !important;
        }}

        .export-table {{
            border-radius: var(--radius-lg);
            border: 1px solid var(--soft-border);
            overflow: hidden;
            box-shadow: 0 10px 26px rgba(15, 23, 42, 0.035);
            background: var(--surface);
        }}

        .export-row {{
            display: grid;
            grid-template-columns: minmax(0, 2.2fr) minmax(120px, 1fr) minmax(90px, 0.7fr) minmax(150px, 1fr) 122px;
            gap: 0.42rem;
            align-items: center;
            padding: 0.5rem 0.7rem;
            border-bottom: 1px solid var(--soft-border);
            background: var(--surface);
        }}

        .export-row.header {{
            background: color-mix(in srgb, var(--surface-alt) 66%, var(--surface) 34%);
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--muted);
            font-weight: 700;
        }}

        .export-cell {{
            font-size: 0.78rem;
            min-width: 0;
            overflow-wrap: anywhere;
        }}

        .export-note {{
            margin-top: 0.2rem;
        }}

        div[data-testid="stDownloadButton"] button {{
            font-size: 0.74rem !important;
        }}

        .st-key-download_zip_button button {{
            min-height: 2.12rem !important;
            font-size: 0.76rem !important;
            font-weight: 700 !important;
        }}

        .sidebar-logo-shell {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            padding: 0.52rem 0.64rem;
            border-radius: var(--radius-lg);
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--soft-border);
            margin-bottom: 0.36rem;
        }}

        .sidebar-logo-shell img {{
            width: 100%;
            max-width: 148px;
            height: auto;
            object-fit: contain;
        }}

        .sidebar-note {{
            color: var(--muted);
            font-size: 0.74rem;
            line-height: 1.35;
            margin: 0.08rem 0 0.2rem 0;
        }}

        .sidebar-meta {{
            color: var(--muted);
            font-size: 0.72rem;
            line-height: 1.25;
            margin: 0.12rem 0 0.14rem 0;
        }}

        .stRadio label,
        .stSlider label,
        .stCaption,
        [data-testid="stWidgetLabel"] {{
            color: var(--text) !important;
        }}

        .path-chip {{
            display: inline-flex;
            align-items: center;
            gap: 0.26rem;
            padding: 0.38rem 0.62rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--soft-border);
            color: var(--muted);
            font-size: 0.74rem;
            margin: 0.18rem 0.18rem 0 0;
            overflow-wrap: anywhere;
        }}

        [data-testid="stSidebar"] .stRadio > div,
        [data-testid="stSidebar"] .stSlider,
        [data-testid="stSidebar"] .stButton,
        [data-testid="stSidebar"] [data-testid="stPopover"] {{
            margin-bottom: 0.14rem;
        }}

        .stCodeBlock, pre {{
            border-radius: var(--radius-lg) !important;
            border: 1px solid var(--soft-border) !important;
            background: color-mix(in srgb, var(--surface) 90%, #000000 10%) !important;
        }}

        [data-testid="stInfo"],
        [data-testid="stWarning"],
        [data-testid="stSuccess"],
        [data-testid="stError"] {{
            border-radius: var(--radius-md);
            border: 1px solid var(--soft-border);
        }}

        @media (max-width: 980px) {{
            .header-inline,
            .export-row {{
                display: block;
            }}

            .header-flow-line {{
                margin-top: 0.5rem;
                white-space: normal;
            }}

            .st-key-process_button button {{
                max-width: none !important;
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
