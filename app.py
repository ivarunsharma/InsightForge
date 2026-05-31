import os
import streamlit as st
import pandas as pd
from src.data_cleaner import load_and_clean
from src.document_loader import load_all_documents, chunk_documents
from src.rag_pipeline import build_vectorstore, load_vectorstore, build_rag_chain, get_llm
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
)
st.title("📊 InsightForge — AI Business Intelligence Assistant")

CHROMA_DIR = "chroma_db"


@st.cache_resource(show_spinner="Initializing InsightForge...")
def initialize():
    df = load_and_clean()

    if not os.path.exists(CHROMA_DIR) or not os.listdir(CHROMA_DIR):
        docs = load_all_documents()
        chunks = chunk_documents(docs)
        vs = build_vectorstore(chunks)
    else:
        vs = load_vectorstore()

    llm = get_llm()
    rag_chain = build_rag_chain(vs)
    pandas_agent = build_pandas_agent(llm)
    return df, llm, rag_chain, pandas_agent, vs


df, llm, rag_chain, pandas_agent, vs = initialize()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Data Summary")
    col1, col2 = st.columns(2)
    col1.metric("Rows",       f"{len(df):,}")
    col1.metric("Regions",    df["Region"].nunique())
    col2.metric("Categories", df["Category"].nunique())
    col2.metric("Customers",  df["Customer Name"].nunique())

    st.metric("Indexed Chunks", vs._collection.count())

    st.divider()
    st.header("Charts")
    chart_choice = st.selectbox("Select chart", [
        "Sales by Region",
        "Profit by Category",
        "Monthly Trend",
        "Top Sub-Categories",
        "Discount vs Profit",
    ])
    chart_map = {
        "Sales by Region":    lambda: plot_sales_by_region(df),
        "Profit by Category": lambda: plot_profit_by_category(df),
        "Monthly Trend":      lambda: plot_monthly_trend(df),
        "Top Sub-Categories": lambda: plot_top_subcategories(df),
        "Discount vs Profit": lambda: plot_discount_vs_profit(df),
    }
    st.pyplot(chart_map[chart_choice]())

    st.divider()
    if st.button("Generate Auto-Insights"):
        with st.spinner("Generating insights..."):
            insights = generate_auto_insights(df, llm)
        st.session_state["insights"] = insights

    if "insights" in st.session_state:
        st.markdown(st.session_state["insights"])

# ── Chat ──────────────────────────────────────────────────────────────────────
st.header("Ask a Question")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("meta"):
            with st.expander("Details"):
                st.caption(f"Route: **{msg['meta']['route']}**")
                st.caption(f"Sources: {', '.join(msg['meta']['sources'])}")

if question := st.chat_input("Ask about sales, profit, regions, board meetings..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = answer(question, pandas_agent, rag_chain)
        st.markdown(result["answer"])
        with st.expander("Details"):
            st.caption(f"Route: **{result['route']}**")
            st.caption(f"Sources: {', '.join(result['sources'])}")

    st.session_state.messages.append({
        "role":    "assistant",
        "content": result["answer"],
        "meta":    {"route": result["route"], "sources": result["sources"]},
    })
