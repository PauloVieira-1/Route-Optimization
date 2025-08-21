# data_handler.py
import sqlite3
from typing import Dict, List, Any, Optional

class DataHandler:
    def __init__(self, database_path: str):
        """
        Initialize the DataHandler object.
        :param database_path: Path to the sqlite database that we will be using.
        """
        self.connection = sqlite3.connect(database_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
    
    def close(self):
        """Close the connection to the database."""
        self.connection.close()

    def create_table(self, table_name: str, columns: Dict[str, str]) -> None:
        """
        Create a table with given columns.
        Example: {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"}
        """
        col_str = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({col_str});"
        self.cursor.execute(query)
        self.connection.commit()
 
    def delete_table(self, table_name: str) -> None:
        """Delete the given table."""
        query = f"DROP TABLE IF EXISTS {table_name};"
        self.cursor.execute(query)
        self.connection.commit()
    
    def insert_with_columns(self, table_name: str, columns: List[str], values: List[Any]) -> None:
        """
        Insert row by specifying only certain columns.
        Example: insert_with_columns("scenarios", ["Name"], ["Scenario A"])
        """
        col_str = ", ".join(columns)
        val_str = ", ".join(["?"] * len(values))
        query = f"INSERT INTO {table_name} ({col_str}) VALUES ({val_str});"
        self.cursor.execute(query, values)
        self.connection.commit()

    def insert(self, table_name: str, values: List[Any]) -> None:
        """
        Insert row with values for all columns.
        WARNING: If a column is AUTOINCREMENT, you should pass None for it.
        """
        col_str = ", ".join(["?"] * len(values))
        query = f"INSERT INTO {table_name} VALUES ({col_str});"
        self.cursor.execute(query, values)  
        self.connection.commit()

    def get_all(self, table_name: str) -> List[List[Any]]:
        """Get all rows from a table."""
        query = f"SELECT * FROM {table_name};"
        return list(self.cursor.execute(query))

    def get_by_id(self, table_name: str, id_column: str, id_value: Any) -> Optional[List[Any]]:
        """Get a single row by ID."""
        query = f"SELECT * FROM {table_name} WHERE {id_column}=?;"
        self.cursor.execute(query, (id_value,))
        return self.cursor.fetchone()

    def delete_by_id(self, table_name: str, id_column: str, id_value: Any) -> None:
        """Delete a row by ID."""
        query = f"DELETE FROM {table_name} WHERE {id_column}=?;"
        self.cursor.execute(query, (id_value,))
        self.connection.commit()

    def print_table(self, table_name: str) -> None:
        """Pretty print the given table."""
        print("\n")
        # Get headers
        query_header = f"PRAGMA table_info({table_name});"
        headers = [col[1] for col in self.cursor.execute(query_header)]

        # Get all rows
        query = f"SELECT * FROM {table_name};"
        rows = list(self.cursor.execute(query))

        # Determine column widths
        col_widths = [len(header) for header in headers]
        for row in rows:
            for i, item in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(item)))

        # Print table title
        total_width = sum(col_widths) + 3 * (len(col_widths) - 1)
        print("=" * total_width)
        print(f"TABLE: {table_name.upper()}".center(total_width))
        print("=" * total_width)

        # Print headers
        header_row = " | ".join(header.ljust(col_widths[i]) for i, header in enumerate(headers))
        print(header_row)
        print("-" * total_width)

        # Print rows
        for row in rows:
            row_str = " | ".join(str(item).ljust(col_widths[i]) for i, item in enumerate(row))
            print(row_str)

        print("=" * total_width + "\n")

    def run(self):
        print("DB is opened")
