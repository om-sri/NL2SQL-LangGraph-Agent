import sqlite3
import pandas as pd
import re

#function to sanitize table names by removing special characters and ensuring they start with a letter or underscore
def sanitize_table_name(filename: str) -> str:
    name = filename.replace(".csv", "")
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    if name[0].isdigit():
        name = "t_" + name
    return name.lower()

#function to load multiple CSV files into an in-memory SQLite database and 
# return the sqconnection and a dictionary of table names to dataframes
def load_csvs_to_sqlite(uploaded_files) -> tuple[sqlite3.Connection, dict]:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    tables = {}

    for file in uploaded_files:
        df = pd.read_csv(file)
        df.columns = [re.sub(r"[^a-zA-Z0-9_]", "_", col).lower() for col in df.columns]
        table_name = sanitize_table_name(file.name)
        df.to_sql(table_name, conn, index=False, if_exists="replace")
        tables[table_name] = df

    return conn, tables

#function to generate a string representation of the database schema, including table names, column names, types, and sample values
#Basically genearte schema info for the agent to understand the structure of the database and use it to generate SQL queries
def get_schema_string(conn: sqlite3.Connection, tables: dict) -> str:
    schema_parts = []
    cursor = conn.cursor()

    for table_name, df in tables.items():
        row_count = len(df)
        schema_parts.append(f"Table: {table_name} ({row_count:,} rows)")

        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            sample_vals = df[col_name].dropna().unique()[:3].tolist()
            sample_str = ", ".join([str(v) for v in sample_vals])
            schema_parts.append(f"  - {col_name}: {col_type} (e.g. {sample_str})")

        schema_parts.append("")

    return "\n".join(schema_parts)