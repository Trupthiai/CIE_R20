            df['Part B Total'] = part_b_df.apply(lambda row: sum([x if isinstance(x, int) else 0 for x in row]), axis=1)
            df['Assignment'] = assignment_marks
            df['Total Check'] = df['Part A'] + df['Part B Total']

            # Rearrange columns to put Total Check after Assignment
            cols = list(df.columns)
            cols.remove('Total Check')
            cols.remove('Assignment')
            new_order = cols[:]
            # Insert Assignment and Total Check after original columns except them
            new_order.insert(len(cols), 'Assignment')
            new_order.insert(len(cols)+1, 'Total Check')
            df = df[new_order]
