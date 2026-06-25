import os
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from src.data_cleaner import load_and_clean
from src.document_loader import load_all_documents, chunk_documents
from src.rag_pipeline import build_vectorstore, load_vectorstore, get_llm
from src.agents import build_pandas_agent, answer
from src.visualizations import (
    plot_sales_by_region, plot_profit_by_category,
    plot_monthly_trend, plot_top_subcategories,
    plot_discount_vs_profit, generate_auto_insights,
)

st.set_page_config(
    page_title="InsightForge",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded",
)


def load_css(path: str):
    with open(path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css("static/style.css")

CHROMA_DIR = "chroma_db"


@st.cache_resource(show_spinner=False)
def _get_data():
    return load_and_clean()


@st.cache_resource(show_spinner=False)
def _get_vectorstore():
    if not os.path.exists(CHROMA_DIR) or not os.listdir(CHROMA_DIR):
        docs = load_all_documents()
        chunks = chunk_documents(docs)
        return build_vectorstore(chunks)
    return load_vectorstore()


@st.cache_resource(show_spinner=False)
def _get_llm():
    return get_llm()


@st.cache_resource(show_spinner=False)
def _get_pandas_agent():
    return build_pandas_agent(_get_llm())


if not (os.path.exists(CHROMA_DIR) and os.listdir(CHROMA_DIR)):
    with st.status("Building document index for the first time…", expanded=True) as _status:
        st.write("Cleaning sales data…")
        df = _get_data()
        st.write("Loading and indexing documents…")
        vs = _get_vectorstore()
        st.write("Connecting to Azure OpenAI…")
        llm = _get_llm()
        pandas_agent = _get_pandas_agent()
        _status.update(label="InsightForge ready!", state="complete", expanded=False)
else:
    with st.spinner("Loading InsightForge…"):
        df = _get_data()
        vs = _get_vectorstore()
        llm = _get_llm()
        pandas_agent = _get_pandas_agent()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>📊 InsightForge</h1>
  <p>AI-powered Business Intelligence &nbsp;·&nbsp; Chat with your data &nbsp;·&nbsp; RAG + Pandas agent</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # ── 1. About the dataset ──────────────────────────────────────────────────
    st.markdown('<p class="sidebar-section">📂 Dataset</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="label">Rows</div><div class="value">{len(df):,}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><div class="label">Regions</div><div class="value">{df["Region"].nunique()}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="label">Categories</div><div class="value">{df["Category"].nunique()}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><div class="label">Customers</div><div class="value">{df["Customer Name"].nunique():,}</div></div>', unsafe_allow_html=True)

    # ── 2. Business KPIs from the data ───────────────────────────────────────
    st.markdown('<p class="sidebar-section">💼 Business KPIs</p>', unsafe_allow_html=True)
    total_sales  = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    margin       = total_profit / total_sales
    top_region   = df.groupby("Region")["Sales"].sum().idxmax()
    st.markdown(f'<div class="metric-card"><div class="label">Total Revenue</div><div class="value">${total_sales/1e6:.2f}M</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-card"><div class="label">Total Profit</div><div class="value">${total_profit/1e3:.0f}K</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-card"><div class="label">Profit Margin</div><div class="value">{margin:.1%}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-card"><div class="label">Top Region</div><div class="value" style="font-size:1.1rem">{top_region}</div></div>', unsafe_allow_html=True)

    # ── 3. AI system stats ────────────────────────────────────────────────────
    st.markdown('<p class="sidebar-section">🤖 AI System</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-card"><div class="label">Indexed Chunks</div><div class="value">{vs._collection.count()}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-card"><div class="label">Vector Store</div><div class="value" style="font-size:1rem">Chroma</div></div>', unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── Tabs (display only — no chat_input inside) ────────────────────────────────
tab_chat, tab_dashboard, tab_insights = st.tabs(["💬  Chat", "📈  Dashboard", "💡  Auto-Insights"])

# Hide the chat input bar when the user is not on the Chat tab
st.html("""
<script>
(function () {
    function sync() {
        const tabs = document.querySelectorAll('[data-baseweb="tab"]');
        if (!tabs.length) return;
        const active = Array.from(tabs).find(t => t.getAttribute('aria-selected') === 'true');
        const onChat = !active || active.innerText.includes('Chat');
        const bar = document.querySelector('[data-testid="stBottom"]');
        if (bar) bar.style.display = onChat ? '' : 'none';
    }

    const observer = new MutationObserver(sync);
    observer.observe(document.body, {
        attributes: true,
        attributeFilter: ['aria-selected'],
        subtree: true
    });

    sync();
})();
</script>
""")

# ── Chat tab: message history display only ────────────────────────────────────
with tab_chat:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("error"):
                with st.expander("Error details"):
                    st.code(msg["error"])
            if msg.get("meta"):
                route     = msg["meta"]["route"]
                badge_cls = "badge-rag" if route == "document" else "badge-pandas"
                sources   = ", ".join(msg["meta"]["sources"]) or "—"
                with st.expander("Details"):
                    st.markdown(f'<span class="{badge_cls}">{route.upper()}</span>', unsafe_allow_html=True)
                    st.caption(f"Sources: {sources}")

# ── Chat input OUTSIDE tabs — Streamlit pins this natively to bottom ──────────
if question := st.chat_input("Ask about sales, profit, regions, board meetings…"):
    st.session_state.messages.append({"role": "user", "content": question})

    with st.spinner("Thinking…"):
        try:
            result = answer(question, pandas_agent, vs, llm, st.session_state.chat_history)
            st.session_state.messages.append({
                "role":    "assistant",
                "content": result["answer"],
                "meta":    {"route": result["route"], "sources": result["sources"]},
            })
            st.session_state.chat_history.append(HumanMessage(content=question))
            st.session_state.chat_history.append(AIMessage(content=result["answer"]))
            st.session_state.chat_history = st.session_state.chat_history[-10:]
        except Exception as e:
            st.session_state.messages.append({
                "role":    "assistant",
                "content": "Sorry, I couldn't process that question. Please try rephrasing or ask something else.",
                "error":   str(e),
            })
    st.rerun()

# ── Dashboard ─────────────────────────────────────────────────────────────────
with tab_dashboard:
    st.markdown('<p class="dash-heading">Sales &amp; Profit Overview</p>', unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.pyplot(plot_sales_by_region(df))
        st.pyplot(plot_top_subcategories(df))
    with col_r:
        st.pyplot(plot_profit_by_category(df))
        st.pyplot(plot_discount_vs_profit(df))

    st.pyplot(plot_monthly_trend(df))

# ── Auto-Insights ─────────────────────────────────────────────────────────────
with tab_insights:
    st.markdown('<p class="dash-heading">AI-Generated Business Recommendations</p>', unsafe_allow_html=True)
    st.caption("Click below to have the AI analyse key metrics and surface actionable recommendations.")

    if st.button("✨  Generate Insights", use_container_width=True):
        with st.spinner("Analysing data…"):
            insights = generate_auto_insights(df, llm)
        st.session_state["insights"] = insights

    if "insights" in st.session_state:
        st.markdown(f'<div class="insight-box">{st.session_state["insights"]}</div>', unsafe_allow_html=True)
