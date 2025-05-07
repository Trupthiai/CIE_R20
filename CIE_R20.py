import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="CIE R20 Marks Divider", layout="centered")
st.title("📊 CIE R20 Marks Divider App")

st.markdown("""
This app divides **Total Marks (out of 20)** into:
- **Part A**: Random value from 0 to 5
- **Part B**: Remaining marks (max 15) distributed randomly among 3 out of 5 questions (Q1–Q5)

---

✅ **Instructions**:
1. Upload an Excel (`.xlsx`) or CSV (`.csv`) file with a column named **`Total Marks`**
2. Get Part A and Part B (`Q1–Q5`) distributions
3. Download the output file as `.csv`
""")

uploaded_file = st.file_uploader("📁 Upload marks file", type=["csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        if 'Total Marks' not in df.columns:
            st.error("❌ The uploaded file must contain a column named 'Total Marks'.")
        else:
            part_a_list = []
            part_b_distributions = []

            for total in df['Total Marks']:
                total = int(round(total))
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

            st.success("✅ Marks successfully distributed!")
            st.dataframe(df)

            csv_output = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download Result as CSV",
                data=csv_output,
                file_name="CIE_R20_Distributed_Marks.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.info("Please upload a `.csv` or `.xlsx` file to begin.")
