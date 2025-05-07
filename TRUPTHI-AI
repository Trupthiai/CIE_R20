import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="CIE R20 Marks Divider", layout="centered")
st.title("📊 CIE R20 Marks Divider App")

st.markdown("""
This app divides `Total Marks` (out of 20) into:
- **Part A**: out of 5 marks (0–5)
- **Part B**: out of 15 marks, distributed across 3 randomly chosen questions out of 5 (`Q1`–`Q5`), each receiving 1–5 marks

---

**Instructions**:
1. Upload a CSV with a column named **`Total Marks`**.
2. View the result below.
3. Download the final sheet with `Part A` and `Q1–Q5` columns.
""")

# File upload
uploaded_file = st.file_uploader("📁 Upload CSV file (with 'Total Marks' column)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if 'Total Marks' not in df.columns:
        st.error("❌ Error: 'Total Marks' column not found in the uploaded file.")
    else:
        part_a_list = []
        part_b_distributions = []

        for total in df['Total Marks']:
            total = int(round(total))  # Handle decimals
            part_a = random.randint(0, min(5, total))
            part_a_list.append(part_a)

            remaining = total - part_a
            q_marks = [0] * 5

            if remaining > 0:
                selected_qs = random.sample(range(5), 3)
                available = min(15, remaining)

                for idx in selected_qs:
                    if available == 0:
                        break
                    mark = random.randint(1, min(5, available))
                    q_marks[idx] = mark
                    available -= mark

            part_b_distributions.append(q_marks)

        df['Part A'] = part_a_list
        df[['Q1', 'Q2', 'Q3', 'Q4', 'Q5']] = pd.DataFrame(part_b_distributions, index=df.index)

        st.success("✅ Marks distributed successfully!")
        st.dataframe(df)

        # Download
        result_csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download CSV",
            data=result_csv,
            file_name="CIE_R20_Marks_Distribution.csv",
            mime="text/csv"
        )
else:
    st.info("Please upload your CSV file to begin.")

