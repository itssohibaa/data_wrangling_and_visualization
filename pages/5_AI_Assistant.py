import streamlit as st

st.title("🤖 AI Data Assistant")

st.markdown("Ask questions about your dataset.")

# Check if data exists
if "df" not in st.session_state or st.session_state.df is None:
    st.warning("⚠️ Please upload a dataset first in the Upload page.")
else:
    df = st.session_state.df

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    question = st.text_input("Ask something about your data:")

    if question:
        # VERY SIMPLE logic (no real AI yet)
        if "columns" in question.lower():
            st.write("Columns:", list(df.columns))

        elif "rows" in question.lower():
            st.write("Number of rows:", df.shape[0])

        elif "summary" in question.lower():
            st.write(df.describe())

        else:
            st.info("I understand basic questions like: columns, rows, summary.")
