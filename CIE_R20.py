import streamlit as st
import pandas as pd
import random
from io import BytesIO
from itertools import product, permutations

st.set_page_config(page_title="CIE R20 Marks Divider", layout="centered")
st.title("📊 CIE R20 Marks Divider App")

st.markdown("""
This app divides **Total Marks (out of 40)** into:
- **Part A**: 1 to 5 marks
- **Part B**: Remaining marks (max 15), distributed among **3 of 5 questions (Q1–Q5)** with 1 to 5 marks each.

---

✅ **Instructions**:
1. Upload an Excel (`.xlsx`) or CSV (`.csv`) file with a column named **`Total Marks`**
2. App will compute marks distribution
3. Download the result as an Excel file
""")

def generate_valid_combination(total_b):
    combinations = [
        (i, j, k) for i in range(1, 6)
        for j in range(1, 6)
        for k in range(1, 6)
        if i + j + k == total_b
    ]
    return random.choice(combinations) if combinations else None

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
            part_b_rows = []

            for total in df['Total Marks']:
                total = int(round(total))

                # Part A between 1 and 5, but should leave at least 3 for Part B (1 mark per Q × 3)
                if total < 4:
                    part_a = total
                    part_b = [None] * 5
                else:
                    part_a = random.randint(1, min(5, total - 3))
                    part_b_total = total - part_a
                    valid_combo = generate_valid_combination(part_b_total)

                    if valid_combo:
                        q_indices = random.sample(range(5), 3)
                        part_b = [None] * 5
                        for i, val in zip(q_indices, valid_combo):
                            part_b[i] = val
                    else:
                        part_b = [None] * 5

                part_a_list.append(part_a)
                part_b_rows.append(part_b)

            df['Part A'] = part_a_list
            df[['Q1', 'Q2', 'Q3', 'Q4', 'Q5']] = pd.DataFrame(part_b_rows, index=df.index)

            # Calculate total from Part A and Part B
            df['Total Calculated'] = df['Part A'].fillna(0) + df[['Q1', 'Q2', 'Q3', 'Q4', 'Q5']].fillna(0).sum(axis=1)

            st.success("✅ Marks successfully distributed!")
            st.dataframe(df)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Distributed Marks')
            output.seek(0)

            st.download_button(
                label="⬇️ Download Result as Excel (.xlsx)",
                data=output,
                file_name="CIE_R20_Distributed_Marks.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.info("Please upload a `.csv` or `.xlsx` file to begin.")
