import streamlit as st
import pandas as pd
import random
from io import BytesIO

st.set_page_config(page_title="CIE R20 Marks Divider", layout="centered")
st.title("📊 CIE R20 Marks Divider App")

st.markdown("""
This app divides **Total Marks (out of 40)** into:
- **Part A**: 1 to 5 marks
- **Part B**: Remaining marks (max 15), distributed among **any 3 of 5 questions** (Q1–Q5), 1 to 5 marks each.

---

✅ **Instructions**:
1. Upload an Excel (`.xlsx`) or CSV (`.csv`) file with a column named **`Total Marks`**
2. App will compute marks distribution
3. You can download the result as an Excel file
""")

def generate_part_b_marks(total_b):
    # Generate all possible 3-number combinations between 1 and 5 that sum to total_b
    options = []
    for i in range(1, 6):
        for j in range(1, 6):
            for k in range(1, 6):
                if i + j + k == total_b:
                    options.append([i, j, k])
    if not options:
        return [None] * 5
    chosen = random.choice(options)
    q_indices = random.sample(range(5), 3)
    marks = [None] * 5
    for idx, val in zip(q_indices, chosen):
        marks[idx] = val
    return marks

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
            part_b_list = []

            for total in df['Total Marks']:
                total = int(round(total))
                if total < 4:
                    # Minimum 1 for Part A and at least 3 for Part B (1+1+1)
                    part_a = max(1, total)
                    q_marks = [None] * 5
                else:
                    part_a = random.randint(1, min(5, total - 3))
                    remaining = total - part_a
                    q_marks = generate_part_b_marks(remaining)

                part_a_list.append(part_a)
                part_b_list.append(q_marks)

            df['Part A'] = part_a_list
            part_b_df = pd.DataFrame(part_b_list, columns=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
            df = pd.concat([df, part_b_df], axis=1)

            df['Total Check'] = df['Part A'].fillna(0) + part_b_df.fillna(0).sum(axis=1)

            st.success("✅ Marks successfully distributed!")
            st.dataframe(df)

            # Save to Excel in memory
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
