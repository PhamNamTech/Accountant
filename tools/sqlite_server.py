"""
Pure Python SQLite MCP Server cho dự án Accountant
Thay thế hoàn toàn mcp-server-sqlite (Node.js/npx) bằng Python thuần:
1. KHÔNG cần quyền Administrator (chạy bằng Python User level).
2. KHÔNG cần kết nối GitHub hay npm registry.
3. KHÔNG cần cài đặt Node.js hay C++ compiler.
4. Tốc độ khởi động tức thì, tương thích 100% với file ketoan.db.
"""

import os
import sqlite3
from typing import Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sqlite-ketoan")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "database", "ketoan.db")


def _get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool(name="query")
def query(query: str, params: list | None = None) -> list[dict]:
    """
    Thực thi câu lệnh SQL SELECT và trả về danh sách các bản ghi dạng dictionary.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params or [])
        rows = [dict(row) for row in cur.fetchall()]
        return rows
    finally:
        conn.close()


@mcp.tool(name="execute")
def execute(query: str, params: list | None = None) -> dict:
    """
    Thực thi câu lệnh SQL ghi (INSERT, UPDATE, DELETE, CREATE, DROP...) và trả về số dòng bị ảnh hưởng.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params or [])
        conn.commit()
        return {
            "status": "success",
            "rows_affected": cur.rowcount,
            "last_row_id": cur.lastrowid
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
    finally:
        conn.close()


@mcp.tool(name="list-tables")
def list_tables() -> list[str]:
    """
    Liệt kê tất cả các bảng hiện có trong cơ sở dữ liệu SQLite ketoan.db.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()


@mcp.tool(name="describe-table")
def describe_table(table_name: str) -> list[dict]:
    """
    Mô tả cấu trúc cột, kiểu dữ liệu, khóa chính của một bảng chỉ định.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({table_name})")
        cols = []
        for r in cur.fetchall():
            cols.append({
                "cid": r[0],
                "name": r[1],
                "type": r[2],
                "notnull": bool(r[3]),
                "default_value": r[4],
                "pk": bool(r[5])
            })
        return cols
    finally:
        conn.close()


@mcp.tool(name="insert-record")
def insert_record(table_name: str, record: dict) -> dict:
    """
    Chèn một bản ghi mới vào bảng chỉ định.
    """
    if not record:
        return {"error": "Record trống"}
    conn = _get_connection()
    try:
        keys = list(record.keys())
        placeholders = ", ".join(["?"] * len(keys))
        columns = ", ".join(keys)
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cur = conn.cursor()
        cur.execute(sql, list(record.values()))
        conn.commit()
        return {"status": "success", "last_row_id": cur.lastrowid}
    except Exception as e:
        return {"status": "error", "error": str(e)}
    finally:
        conn.close()


@mcp.tool(name="update-record")
def update_record(table_name: str, record: dict, where_clause: str, where_params: list | None = None) -> dict:
    """
    Cập nhật các bản ghi trong bảng thỏa mãn điều kiện where_clause.
    """
    if not record:
        return {"error": "Record trống"}
    conn = _get_connection()
    try:
        set_expr = ", ".join([f"{k} = ?" for k in record.keys()])
        sql = f"UPDATE {table_name} SET {set_expr} WHERE {where_clause}"
        params = list(record.values()) + (where_params or [])
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return {"status": "success", "rows_affected": cur.rowcount}
    except Exception as e:
        return {"status": "error", "error": str(e)}
    finally:
        conn.close()


@mcp.tool(name="delete-record")
def delete_record(table_name: str, where_clause: str, where_params: list | None = None) -> dict:
    """
    Xóa các bản ghi trong bảng thỏa mãn điều kiện where_clause.
    """
    conn = _get_connection()
    try:
        sql = f"DELETE FROM {table_name} WHERE {where_clause}"
        cur = conn.cursor()
        cur.execute(sql, where_params or [])
        conn.commit()
        return {"status": "success", "rows_affected": cur.rowcount}
    except Exception as e:
        return {"status": "error", "error": str(e)}
    finally:
        conn.close()


@mcp.tool(name="transaction")
def transaction(statements: list[dict]) -> dict:
    """
    Thực thi một chuỗi các câu lệnh SQL trong một transaction duy nhất (Atomic Commit/Rollback).
    statements: [{'query': '...', 'params': [...]}, ...]
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        for stmt in statements:
            q = stmt.get("query", "")
            p = stmt.get("params", [])
            cur.execute(q, p)
        conn.commit()
        return {"status": "success", "executed_count": len(statements)}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "error": str(e), "message": "Transaction đã được Rollback an toàn"}
    finally:
        conn.close()


if __name__ == "__main__":
    mcp.run()
