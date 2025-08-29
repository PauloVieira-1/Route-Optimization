# data_handler.py
import sqlite3

class DataHandler:
    def __init__(self, db_path):
        # Allow Flask multithreading
        self.connection = sqlite3.connect(db_path, check_same_thread=False)

    # -------------------
    # General methods
    # -------------------
    def get_all(self, table):
        cur = self.connection.cursor()
        cur.execute(f"SELECT * FROM {table}")
        results = cur.fetchall()
        cur.close()
        return results

    def get_all_by_scenario_id(self, table, scenario_id):
        cur = self.connection.cursor()
        cur.execute(f"SELECT * FROM {table} WHERE scenario_id=?", (scenario_id,))
        results = cur.fetchall()
        cur.close()
        return results

    def insert(self, table, values):
        cur = self.connection.cursor()
        placeholders = ",".join(["?"] * len(values))
        cur.execute(f"INSERT INTO {table} VALUES ({placeholders})", values)
        self.connection.commit()
        
        inserted_id = values[0] if values[0] is not None else cur.lastrowid
        
        cur.close()
        return inserted_id


    def delete_by_id(self, table, row_id, column="id"):
        cur = self.connection.cursor()
        cur.execute(f"DELETE FROM {table} WHERE {column}=?", (row_id,))
        self.connection.commit()
        cur.close()

    def update_by_id(self, table, row_id, column, value):
        cur = self.connection.cursor()
        cur.execute(f"UPDATE {table} SET {column}=? WHERE id=?", (value, row_id))
        self.connection.commit()
        cur.close()

    def get_by_id(self, table, row_id):
        cur = self.connection.cursor()
        cur.execute(f"SELECT * FROM {table} WHERE id=?", (row_id,))
        result = cur.fetchone()
        cur.close()
        return result

    # -------------------
    # Optional: Reset table
    # -------------------
    def clear_table(self, table):
        cur = self.connection.cursor()
        cur.execute(f"DELETE FROM {table}")
        self.connection.commit()
        cur.close()

    # -------------------
    # Close connection
    # -------------------
    def close(self):
        self.connection.close()