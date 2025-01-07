import pandas as pd
import os
import json
import streamlit as st
import matplotlib.pyplot as plt

class CSVExcelModifier:
    def __init__(self):
        self.log = []  # To record progress of modifications

    def log_action(self, action):
        self.log.append(action)

    def remove_duplicates(self, df):
        initial_count = len(df)
        df_cleaned = df.drop_duplicates()
        final_count = len(df_cleaned)

        self.log_action({
            "action": "remove_duplicates",
            "details": f"Removed {initial_count - final_count} duplicate rows."
        })
        return df_cleaned

    def apply_rules(self, df, rules):
        try:
            for rule in rules:
                column, condition, value = rule["column"], rule["condition"], rule["value"]
                if condition == "greater_than":
                    df = df[df[column] > value]
                elif condition == "less_than":
                    df = df[df[column] < value]
                elif condition == "equals":
                    df = df[df[column] == value]

            self.log_action({
                "action": "apply_rules",
                "details": f"Applied rules: {rules}. Remaining rows: {len(df)}"
            })
            return df
        except Exception as e:
            st.error(f"Error applying rules: {e}")
            return df

    def add_or_delete_rows(self, df, operations):
        try:
            for operation in operations:
                action, row_data = operation["action"], operation.get("row_data")
                if action == "add":
                    df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
                elif action == "delete":
                    index_to_delete = operation.get("index")
                    if index_to_delete is not None and 0 <= index_to_delete < len(df):
                        df = df.drop(index_to_delete)

            self.log_action({
                "action": "add_or_delete_rows",
                "details": f"Performed operations: {operations}. Final rows: {len(df)}"
            })
            return df
        except Exception as e:
            st.error(f"Error performing operations: {e}")
            return df

    def remove_empty_rows(self, df):
        initial_count = len(df)
        df_cleaned = df.dropna()
        final_count = len(df_cleaned)

        self.log_action({
            "action": "remove_empty_rows",
            "details": f"Removed {initial_count - final_count} empty rows."
        })
        return df_cleaned

    def sort_data(self, df, column, ascending=True):
        try:
            df_sorted = df.sort_values(by=column, ascending=ascending)
            self.log_action({
                "action": "sort_data",
                "details": f"Sorted data by {column} in {'ascending' if ascending else 'descending'} order."
            })
            return df_sorted
        except Exception as e:
            st.error(f"Error sorting data: {e}")
            return df

    def rename_columns(self, df, column_mapping):
        try:
            df_renamed = df.rename(columns=column_mapping)
            self.log_action({
                "action": "rename_columns",
                "details": f"Renamed columns: {column_mapping}."
            })
            return df_renamed
        except Exception as e:
            st.error(f"Error renaming columns: {e}")
            return df

    def fill_missing_values(self, df, method="ffill", value=None):
        try:
            if method == "ffill":
                df_filled = df.fillna(method="ffill")
            elif method == "bfill":
                df_filled = df.fillna(method="bfill")
            elif method == "value" and value is not None:
                df_filled = df.fillna(value)
            else:
                df_filled = df
            
            self.log_action({
                "action": "fill_missing_values",
                "details": f"Filled missing values using {method} method."
            })
            return df_filled
        except Exception as e:
            st.error(f"Error filling missing values: {e}")
            return df

    def create_chart(self, df, chart_type, x_column, y_column=None):
        try:
            plt.figure(figsize=(10, 6))

            if chart_type == "Bar Chart":
                if y_column:
                    plt.bar(df[x_column], df[y_column], color='skyblue')
                    plt.ylabel(y_column)
                else:
                    df[x_column].value_counts().plot(kind='bar', color='skyblue')
                    plt.ylabel("Count")
                plt.xlabel(x_column)
                plt.title(f"Bar Chart: {x_column} vs {y_column if y_column else 'Count'}")

            elif chart_type == "Line Chart" and y_column:
                plt.plot(df[x_column], df[y_column], marker='o', linestyle='-', color='orange')
                plt.xlabel(x_column)
                plt.ylabel(y_column)
                plt.title(f"Line Chart: {x_column} vs {y_column}")

            elif chart_type == "Pie Chart":
                df[x_column].value_counts().plot(kind='pie', autopct='%1.1f%%', startangle=90, cmap='tab10')
                plt.ylabel('')
                plt.title(f"Pie Chart: {x_column}")

            else:
                st.error("Invalid chart type or missing column(s). Please check your inputs.")

            st.pyplot(plt)

            self.log_action({
                "action": "create_chart",
                "details": f"Created {chart_type} using {x_column} {f'and {y_column}' if y_column else ''}."
            })
        except Exception as e:
            st.error(f"Error creating chart: {e}")

    def save_log(self):
        return self.log

# Streamlit UI
def main():
    st.title("CSV/Excel Modifier Tool")
    st.write("Welcome to the CSV/Excel Modifier! Upload your file and choose an operation.")

    modifier = CSVExcelModifier()

    uploaded_file = st.file_uploader("Upload a CSV/Excel file", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.write("### Uploaded File:", df)

            operation = st.selectbox("Choose an operation", [
                "Remove Duplicates", 
                "Apply Rules", 
                "Add/Delete Rows", 
                "Remove Empty Rows", 
                "Sort Data", 
                "Rename Columns", 
                "Fill Missing Values", 
                "Create Chart"
            ])

            if operation == "Remove Duplicates":
                if st.button("Run Operation"):
                    df = modifier.remove_duplicates(df)
                    st.write("### Modified File:", df)

            elif operation == "Apply Rules":
                rules_input = st.text_area("Enter rules in JSON format (e.g., [{\"column\": \"Column1\", \"condition\": \"greater_than\", \"value\": 10}])")
                if st.button("Run Operation"):
                    try:
                        rules = json.loads(rules_input)
                        df = modifier.apply_rules(df, rules)
                        st.write("### Modified File:", df)
                    except Exception as e:
                        st.error(f"Error parsing rules: {e}")

            elif operation == "Add/Delete Rows":
                operations_input = st.text_area("Enter operations in JSON format (e.g., [{\"action\": \"add\", \"row_data\": {\"Column1\": 30, \"Column2\": \"F\", \"Column3\": 600}}, {\"action\": \"delete\", \"index\": 0}])")
                if st.button("Run Operation"):
                    try:
                        operations = json.loads(operations_input)
                        df = modifier.add_or_delete_rows(df, operations)
                        st.write("### Modified File:", df)
                    except Exception as e:
                        st.error(f"Error parsing operations: {e}")

            elif operation == "Remove Empty Rows":
                if st.button("Run Operation"):
                    df = modifier.remove_empty_rows(df)
                    st.write("### Modified File:", df)

            elif operation == "Sort Data":
                column_to_sort = st.text_input("Enter column name to sort by")
                ascending = st.radio("Sort Order", ("Ascending", "Descending")) == "Ascending"
                if st.button("Run Operation"):
                    df = modifier.sort_data(df, column_to_sort, ascending)
                    st.write("### Modified File:", df)

            elif operation == "Rename Columns":
                column_mapping_input = st.text_area("Enter column mapping in JSON format (e.g., {\"OldColumn\": \"NewColumn\"})")
                if st.button("Run Operation"):
                    try:
                        column_mapping = json.loads(column_mapping_input)
                        df = modifier.rename_columns(df, column_mapping)
                        st.write("### Modified File:", df)
                    except Exception as e:
                        st.error(f"Error parsing column mapping: {e}")

            elif operation == "Fill Missing Values":
                method = st.selectbox("Fill Method", ["ffill", "bfill", "value"])
                value = st.text_input("Fill Value (if applicable)", value="")
                if st.button("Run Operation"):
                    fill_value = None if not value else value
                    df = modifier.fill_missing_values(df, method, fill_value)
                    st.write("### Modified File:", df)

            elif operation == "Create Chart":
                chart_type = st.selectbox("Select chart type", ["Bar Chart", "Line Chart", "Pie Chart"])
                x_column = st.selectbox("Select column for X-axis", df.columns)
                y_column = None
                if chart_type in ["Bar Chart", "Line Chart"]:
                    y_column = st.selectbox("Select column for Y-axis (optional)", ["None"] + list(df.columns))
                    y_column = None if y_column == "None" else y_column

                if st.button("Generate Chart"):
                    modifier.create_chart(df, chart_type, x_column, y_column)

            if st.button("Download Modified File"):
                output_file = "modified_file.csv"
                st.download_button("Download", data=df.to_csv(index=False), file_name=output_file, mime="text/csv")

            st.write("### Modification Log:", modifier.save_log())
        except Exception as e:
            st.error(f"Error processing file: {e}")

if __name__ == "__main__":
    main()
