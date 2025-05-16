import streamlit as st
import pandas as pd
import random
from io import BytesIO

st.set_page_config(page_title="CIE R20 Marks Divider", layout="centered")
st.title("📊 CIE R20 Marks Divider App")

st.markdown("""
This app divides **Total Marks (out of 20)** into:
- **Part A**: Random value between 0 to 5
- **Part B**: Remaining marks (max 15), distributed among exactly 3 out of 5 questions (Q1–Q5)
  - Each selected question gets **1 to 5 marks**
  - Remaining 2 questions are **blank**

---

✅ **Instructions**:
1. Upload an Excel (`.xlsx`) or CSV (`.csv`) file with a column named **`Total Marks`**
2. The app will compute marks distribution ensuring total = Part A + Part B
3. Download the result as an Excel file
""")

uploaded_file = st.file_uploader("📁 Upload marks file", type=["csv", "xlsx"])

def generate_distribution(total, num_questions=3, max_mark=5, max_total=15):
    """
    Generate a list of `num_questions` integers each between 1 and max_mark inclusive,
    which sum exactly to `total`. Return None if no combination found after many tries.
    """
    attempts = 0
    while attempts < 10000:
        marks = [random.randint(1, max_mark) for _ in range(num_questions)]
        if sum(marks) == total:
            return marks
        attempts += 1
    return None

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Remove unnamed columns
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        if 'Total Marks' not in df.columns:
            st.error("❌ The uploaded file must contain a column named 'Total Marks'.")
        else:
            part_a_list = []
            part_b_list = []

            for total_marks in df['Total Marks']:
                total_marks = int(round(total_marks))
                # Limit total marks max 20
                total_marks = min(total_marks, 20)

                # Part A between 0 and 5 but <= total_marks
                part_a = random.randint(0, min(5, total_marks))
                part_a_list.append(part_a)

                remaining = total_marks - part_a
                remaining = min(remaining, 15)  # max Part B = 15

                # If remaining < 3 (since 3 questions with min 1 each), adjust part_a
                if remaining < 3 and total_marks >= 3:
                    part_a = total_marks - 3
                    part_a = min(part_a, 5)
                    part_a_list[-1] = part_a
                    remaining = total_marks - part_a

                # Generate distribution for 3 questions summing to remaining
                distribution = generate_distribution(remaining, 3, 5, 15)

                # If failed to generate, fallback - assign 1 mark each for 3 questions, rest to part A
                if distribution is None:
                    distribution = [1,1,1]
                    part_a = total_marks - 3
                    part_a = min(part_a,5)
                    part_a_list[-1] = part_a
                    remaining = total_marks - part_a

                q_marks = [''] * 5
                selected_indices = random.sample(range(5), 3)
                for i, idx in enumerate(selected_indices):
                    q_marks[idx] = distribution[i]

                part_b_list.append(q_marks)

            df['Part A'] = part_a_list
            part_b_df = pd.DataFrame(part_b_list, columns=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
            df = pd.concat([df, part_b_df], axis=1)

            # Show result
            st.success("✅ Marks successfully distributed!")
            st.dataframe(df)

            # Download
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
