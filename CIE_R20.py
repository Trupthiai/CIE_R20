import streamlit as st
import pandas as pd
import random
from io import BytesIO

st.set_page_config(page_title="CIE R20 Marks Divider", layout="centered")
st.title("📊 CIE R20 Marks Divider App")

st.markdown("""
This app divides **Total Marks (out of 40)** into:
- **Part A**: Random value between 1 to 5
- **Part B**: Remaining marks (max 35), distributed among any 3 out of 5 questions (Q1–Q5)
  - Each selected question gets **1 to 5 marks**
  - Remaining 2 questions are **blank**

---

✅ **Instructions**:
1. Upload an Excel (`.xlsx`) or CSV (`.csv`) file with a column named **`Total Marks`**
2. App will compute marks distribution
3. Download the result as an Excel file
""")

def valid_distribution(total_sum, num_qs=3, max_mark=5):
    """Generate a list of `num_qs` integers (1 to max_mark) that sum to `total_sum`."""
    attempts = 0
    while attempts < 10000:  # more attempts for rare cases
        trial = [random.randint(1, max_mark) for _ in range(num_qs)]
        if sum(trial) == total_sum:
            return trial
        attempts += 1
    return None

uploaded_file = st.file_uploader("📁 Upload marks file", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # Load file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Remove unnamed columns if any
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        if 'Total Marks' not in df.columns:
            st.error("❌ The uploaded file must contain a column named 'Total Marks'.")
        else:
            part_a_list = []
            part_b_distributions = []

            for total in df['Total Marks']:
                total = int(round(total))
                # Part A: 1 to 5 or total if total < 1 (just in case)
                part_a = random.randint(1, min(5, total)) if total >= 1 else 0
                part_a_list.append(part_a)

                remaining = total - part_a
                remaining = min(remaining, 35)  # cap Part B max to 35
                q_marks = [''] * 5

                if remaining > 0:
                    selected_qs = random.sample(range(5), 3)
                    distribution = valid_distribution(remaining, 3, 5)
                    if distribution:
                        for i, idx in enumerate(selected_qs):
                            q_marks[idx] = distribution[i]
                    else:
                        # If no valid distribution found, assign blanks
                        q_marks = [''] * 5

                part_b_distributions.append(q_marks)

            df['Part A'] = part_a_list
            part_b_df = pd.DataFrame(part_b_distributions, columns=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
            df = pd.concat([df, part_b_df], axis=1)

            # Check sum to verify correctness
            df['Part B Total'] = part_b_df.apply(lambda r: sum(x if isinstance(x, int) else 0 for x in r), axis=1)
            df['Total Check'] = df['Part A'] + df['Part B Total']

            st.success("✅ Marks successfully distributed!")
            st.dataframe(df)

            # Download button
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
