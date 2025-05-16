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

def valid_distribution(total_sum, num_qs=3, max_mark=5):
    """
    Distribute total_sum across num_qs questions, each 1 to max_mark.
    Uses proportional scaling and rounding to guarantee sum == total_sum.
    """
    if total_sum < num_qs or total_sum > num_qs * max_mark:
        # impossible to distribute
        return None

    base = [1] * num_qs
    total_sum -= num_qs  # subtract the base marks

    increments = [random.random() for _ in range(num_qs)]
    increments_sum = sum(increments)

    scaled = [ (inc / increments_sum) * total_sum for inc in increments]

    distribution = [base[i] + scaled[i] for i in range(num_qs)]
    distribution = [min(max_mark, round(x)) for x in distribution]

    diff = total_sum + num_qs - sum(distribution)
    while diff != 0:
        for i in range(num_qs):
            if diff == 0:
                break
            if diff > 0 and distribution[i] < max_mark:
                distribution[i] += 1
                diff -= 1
            elif diff < 0 and distribution[i] > 1:
                distribution[i] -= 1
                diff += 1

    return distribution

if uploaded_file:
    try:
        # Read the uploaded file
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
                total = min(total, 40)  # cap total marks at 40

                part_a = random.randint(0, min(5, total))
                part_a_list.append(part_a)

                remaining = total - part_a
                remaining = min(remaining, 15)  # Part B max 15

                q_marks = [''] * 5

                if remaining >= 3:  # minimum 1 mark in each of 3 questions
                    selected_qs = random.sample(range(5), 3)
                    distribution = valid_distribution(remaining, 3, 5)
                    if distribution:
                        for i, idx in enumerate(selected_qs):
                            q_marks[idx] = distribution[i]
                    else:
                        # fallback if distribution fails
                        for i, idx in enumerate(selected_qs):
                            q_marks[idx] = 1
                elif remaining > 0:
                    # If remaining less than 3, assign 1 mark each to that many questions randomly
                    count = remaining
                    selected_qs = random.sample(range(5), count)
                    for idx in selected_qs:
                        q_marks[idx] = 1

                part_b_distributions.append(q_marks)

            df['Part A'] = part_a_list
            part_b_df = pd.DataFrame(part_b_distributions, columns=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
            df = pd.concat([df, part_b_df], axis=1)

            # Verify total sum == input total marks
            df['Part B Total'] = part_b_df.apply(lambda row: sum([x if isinstance(x, int) else 0 for x in row]), axis=1)
            df['Total Check'] = df['Part A'] + df['Part B Total']

            # Show table
            st.success("✅ Marks successfully distributed!")
            st.dataframe(df)

            # Download as Excel
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
