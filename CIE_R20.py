import streamlit as st
import pandas as pd
import random
from io import BytesIO

st.set_page_config(page_title="CIE R20 Marks Divider", layout="centered")
st.title("📊 CIE R20 Marks Divider App")

st.markdown("""
This app divides **Total Marks (out of 40)** into:
- **Part A**: Random value between 0 to 5
- **Part B**: Remaining marks (max 15), distributed among any 3 out of 5 questions (Q1–Q5)
  - Each selected question gets **1 to 5 marks**
  - Remaining 2 questions are **blank**

---

✅ **Instructions**:
1. Upload an Excel (`.xlsx`) or CSV (`.csv`) file with a column named **`Total Marks`**
2. App will compute marks distribution
3. Download the result as an Excel file
""")

uploaded_file = st.file_uploader("📁 Upload marks file", type=["csv", "xlsx"])

def distribute_marks(total_sum, num_questions=3, min_mark=1, max_mark=5):
    """
    Distribute total_sum into num_questions parts each between min_mark and max_mark,
    sum exactly total_sum. Return None if impossible.
    """
    if total_sum < num_questions * min_mark or total_sum > num_questions * max_mark:
        return None

    result = []

    def backtrack(remaining, parts_left):
        if parts_left == 1:
            if min_mark <= remaining <= max_mark:
                result.append(remaining)
                return True
            else:
                return False

        for mark in range(min_mark, max_mark+1):
            if mark <= remaining:
                result.append(mark)
                if backtrack(remaining - mark, parts_left - 1):
                    return True
                result.pop()
        return False

    if backtrack(total_sum, num_questions):
        return result
    else:
        return None

if uploaded_file:
    try:
        # Load file and clean unnamed columns
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        if 'Total Marks' not in df.columns:
            st.error("❌ The uploaded file must contain a column named 'Total Marks'.")
        else:
            part_a_list = []
            part_b_distributions = []

            for total in df['Total Marks']:
                total = int(round(total))
                total = min(total, 40)  # Cap input total to 40 max

                # Part A: random between 0 and min(5, total)
                part_a = random.randint(0, min(5, total))

                # Remaining for Part B
                remaining = total - part_a
                remaining = min(remaining, 15)

                q_marks = [''] * 5

                if remaining == 0:
                    # No marks left for Part B
                    pass
                elif remaining < 3:
                    # Remaining less than min sum for 3 questions (3*1=3), assign 1 mark each to fewer questions
                    selected_qs = random.sample(range(5), remaining)
                    for idx in selected_qs:
                        q_marks[idx] = 1
                    # Adjust part_a to match total (total - sum(q_marks))
                    part_a = total - remaining
                else:
                    # Try to distribute remaining exactly into 3 questions
                    selected_qs = random.sample(range(5), 3)
                    distribution = distribute_marks(remaining, 3, 1, 5)
                    if distribution:
                        for i, idx in enumerate(selected_qs):
                            q_marks[idx] = distribution[i]
                    else:
                        # fallback: assign 1 mark each, adjust part A accordingly
                        for i, idx in enumerate(selected_qs):
                            q_marks[idx] = 1
                        part_a = total - 3

                part_a_list.append(part_a)
                part_b_distributions.append(q_marks)

            df['Part A'] = part_a_list
            part_b_df = pd.DataFrame(part_b_distributions, columns=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
            df = pd.concat([df, part_b_df], axis=1)

            df['Part B Total'] = part_b_df.apply(lambda row: sum([x if isinstance(x, int) else 0 for x in row]), axis=1)
            df['Total Check'] = df['Part A'] + df['Part B Total']

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
