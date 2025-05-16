import streamlit as st
import pandas as pd
import random
from io import BytesIO

st.set_page_config(page_title="CIE R20 Marks Divider", layout="centered")
st.title("📊 CIE R20 Marks Divider App")

st.markdown("""
This app divides **Total Marks (out of 40)** into:
- **Part A**: Random value from 1 to 5
- **Part B**: Remaining marks (max 15) distributed among any 3 out of 5 questions (Q1–Q5)

---

✅ **Instructions**:
1. Upload an Excel (`.xlsx`) or CSV (`.csv`) file with a column named **`Total Marks`**
2. App will compute marks distribution
3. You can download the result as an Excel file
""")

uploaded_file = st.file_uploader("📁 Upload marks file", type=["csv", "xlsx"])

def distribute_marks(total):
    if total < 1:
        return 0, ['']*5
    for _ in range(1000):  # Retry attempts for valid combinations
        part_a = random.randint(1, min(5, total))
        remaining = total - part_a

        if remaining < 3 or remaining > 15:
            continue

        indices = random.sample(range(5), 3)
        q_marks = [''] * 5
        success = False

        for _ in range(100):  # Try to find a valid distribution for Part B
            marks = [random.randint(1, 5) for _ in range(3)]
            if sum(marks) == remaining:
                for i, idx in enumerate(indices):
                    q_marks[idx] = marks[i]
                success = True
                break

        if success:
            return part_a, q_marks
    return 0, ['']*5  # Fallback

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        if 'Total Marks' not in df.columns:
            st.error("❌ The uploaded file must contain a column named 'Total Marks'.")
        else:
            df = df[['Total Marks']].copy()
            part_a_list = []
            part_b_list = []

            for total in df['Total Marks']:
                total = int(round(total))
                part_a, q_marks = distribute_marks(total)
                part_a_list.append(part_a)
                part_b_list.append(q_marks)

            df['Part A'] = part_a_list
            q_df = pd.DataFrame(part_b_list, columns=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
            df = pd.concat([df, q_df], axis=1)

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
