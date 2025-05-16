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
- **Assignment**: Random marks between 16 to 20

---

✅ **Instructions**:
1. Upload an Excel (`.xlsx`) or CSV (`.csv`) file with a column named **`Total Marks`**
2. App will compute marks distribution
3. Download the result as an Excel file
""")

uploaded_file = st.file_uploader("📁 Upload marks file", type=["csv", "xlsx"])

def distribute_marks(total_sum, num_questions=3, min_mark=1, max_mark=5):
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

        for mark in range(min_mark, max_mark + 1):
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
            assignment_marks = []

            for total in df['Total Marks']:
                total = int(round(total))
                total = min(total, 40)  # Cap total at 40

                # Part A between 0 and 5 but not more than total
                part_a = random.randint(0, min(5, total))
                remaining = total - part_a
                remaining = min(remaining, 15)

                q_marks = [''] * 5

                if remaining == 0:
                    # all remaining zero marks
                    pass
                elif remaining < 3:
                    # If remaining less than 3, just assign 1 mark to as many questions as remaining
                    selected_qs = random.sample(range(5), remaining)
                    for idx in selected_qs:
                        q_marks[idx] = 1
                    part_a = total - remaining  # Adjust part_a so sum matches total
                else:
                    # Distribute remaining exactly among 3 questions 1-5 marks each
                    selected_qs = random.sample(range(5), 3)
                    distribution = distribute_marks(remaining, 3, 1, 5)
                    if distribution:
                        for i, idx in enumerate(selected_qs):
                            q_marks[idx] = distribution[i]
                    else:
                        # fallback - assign 1 mark each
                        for i, idx in enumerate(selected_qs):
                            q_marks[idx] = 1
                        part_a = total - 3

                part_a_list.append(part_a)
                part_b_distributions.append(q_marks)
                assignment_marks.append(random.randint(16, 20))

            df['Part A'] = part_a_list
            part_b_df = pd.DataFrame(part_b_distributions, columns=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
            df = pd.concat([df, part_b_df], axis=1)

            # Calculate Part B total
            df['Part B Total'] = part_b_df.apply(lambda row: sum([x if isinstance(x, int) else 0 for x in row]), axis=1)
            df['Assignment'] = assignment_marks
            df['Total Check'] = df['Part A'] + df['Part B Total']

            # Rearrange columns to put Total Check after Assignment and remove Part B Total from display
            cols = list(df.columns)
            cols.remove('Part B Total')
            cols.remove('Total Check')
            cols.remove('Assignment')
            new_order = cols[:]
            new_order.insert(len(cols), 'Assignment')
            new_order.insert(len(cols)+1, 'Total Check')
            df = df[new_order]

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
