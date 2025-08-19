import sqlite3
from typing import Dict, List

class DataHandler:
    def __init__(self, database_path: str):
        """
        Initialize the DataHandler object.
        :param database_path: Path to the sqlite database that we will be using.
        """
        self.connection = sqlite3.connect(database_path)
        self.cursor = self.connection.cursor()
    
    def close(self):
        """
        Close the connection to the database.
        This should be called when you're done with the object.
        """
        self.connection.close() # Remeber to close the connection when done

    def create_table(self, table_name: str, columns: Dict[str, str]) -> None:
        """
        Create a table with given columns.
        Example columns: {"id": "INTEGER PRIMARY KEY", "name": "TEXT", "age": "INTEGER"}
        """
        col_str = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({col_str});"
        self.cursor.execute(query)
        self.connection.commit()
 
    def delete_table(self, table_name: str) -> None:
        """
        Delete the given table.
        :param table_name: Name of the table to delete
        """
        query = f"DROP TABLE IF EXISTS {table_name};"
        self.cursor.execute(query)
        self.connection.commit()
    
    def insert(self, table_name: str, values: List[str]) -> None:
        """
        Insert the given values into the specified table.
        :param table_name: Name of the table to insert into
        :param values: List of values to insert. The length of this list must match the number of columns in the table.
        """
        col_str = ", ".join(["?"] * len(values))
        query = f"INSERT INTO {table_name} VALUES ({col_str});"
        self.cursor.execute(query, values)  
        self.connection.commit()

    def print_table(self, table_name: str) -> None:
        """
        Pretty print the given table.
        :param table_name: Name of the table to print.
        """
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
