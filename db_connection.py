# db_connection.py
import mysql.connector
import streamlit as st


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # 🔹 change this
        database="capstone_db"
    )


def run_query(query, params=None, fetch=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    if fetch:
        result = cursor.fetchall()
    else:
        result = None
    conn.commit()
    cursor.close()
    conn.close()
    return result
