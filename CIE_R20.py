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
  - Each selected question gets **1 to 5 marks**, unselected ones are left **blank**

---

✅ **Instructions**:
1. Upload an Excel (`.xlsx`) or CSV (`.csv`) file with a column named **`Total Marks`**
2. App will compute marks distribution
3. You can download the result as an Excel file
""")

uploaded_file = st.file_uploader("📁 Upload marks file", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # Read the uploaded file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Remove any unnamed columns (e.g., index columns)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        # Validate the required column
        if 'Total Marks' not in df.columns:
            st.error("❌ The uploaded file must contain a column named 'Total Marks'.")
        else:
            part_a_list = []
            part_b_distributions = []

            for total in df['Total Marks']:
                total = int(round(total))

                # Assign Part A marks between 1 and 5 (not exceeding total)
                part_a = random.randint(1, min(5, total))
                part_a_list.append(part_a)

                remaining = total - part_a
                q_marks = [''] * 5

                if remaining > 0:
                    selected_qs = random.sample(range(5), 3)
                    # Try generating a valid random distribution that fits within remaining marks
                    for _ in range(100):
                        trial = [random.randint(1, 5) for _ in range(3)]
                        if sum(trial) <= remaining:
                            for i, idx in enumerate(selected_qs):
                                q_marks[idx] = trial[i]
                            break

                part_b_distributions.append(q_marks)

            # Assign new columns to DataFrame
            df['Part A'] = part_a_list
            part_b_df = pd.DataFrame(part_b_distributions, columns=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
            df = pd.concat([df, part_b_df], axis=1)

            # Display result
            st.success("✅ Marks successfully distributed!")
            st.dataframe(df)

            # Prepare downloadable Excel file
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
