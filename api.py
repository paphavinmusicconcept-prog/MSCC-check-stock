# ============================================================
# api.py — Local API รันบนคอมที่ร้าน
# รับ SKU จากบอท → ดึงสต็อกจาก MySQL → ส่งกลับ
# ============================================================

from flask import Flask, request, jsonify
import mysql.connector
from stock_cleaning import normalize_product

app = Flask(__name__)

# ── ตั้งค่าการเชื่อมต่อ MySQL ──────────────────────────────
DB_CONFIG = {
    "host":     "localhost",   # ปกติไม่ต้องเปลี่ยน
    "port":     3306,          # port MySQL (ค่าเริ่มต้น)
    "user":     "root",        # ชื่อผู้ใช้ MySQL ของร้าน
    "password": "รหัสผ่าน",    # รหัสผ่าน MySQL
    "database": "express_db",  # ชื่อฐานข้อมูล Express
}

# ── ชื่อตารางและคอลัมน์ใน MySQL ───────────────────────────
TABLE   = "products"     # ชื่อตารางสินค้า (แก้ให้ตรง)
COL_SKU = "sku"          # คอลัมน์ SKU
COL_NAME = "name"        # คอลัมน์ชื่อสินค้า
COL_QTY  = "quantity"    # คอลัมน์จำนวนคงเหลือ
COL_UNIT = None          # ถ้ามีคอลัมน์หน่วย ให้ใส่ชื่อคอลัมน์ เช่น "unit"
COL_WAREHOUSE = None     # ถ้ามีคอลัมน์คลัง ให้ใส่ชื่อคอลัมน์ เช่น "warehouse"

# ── Endpoint รับ request จากบอท ────────────────────────────
@app.route("/stock", methods=["GET"])
def get_stock():
    sku = request.args.get("sku", "").strip()

    if not sku:
        return jsonify({"error": "ไม่ได้ส่ง SKU มา"}), 400

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        select_columns = [
            f"{COL_NAME} AS raw_name",
            f"{COL_SKU} AS raw_sku",
            f"{COL_QTY} AS raw_qty",
        ]
        if COL_UNIT:
            select_columns.append(f"{COL_UNIT} AS raw_unit")
        if COL_WAREHOUSE:
            select_columns.append(f"{COL_WAREHOUSE} AS raw_warehouse")

        sql = (
            f"SELECT {', '.join(select_columns)} "
            f"FROM {TABLE} WHERE {COL_SKU} = %s LIMIT 1"
        )
        cursor.execute(sql, (sku,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row:
            product = normalize_product(
                row.get("raw_sku"),
                row.get("raw_name"),
                row.get("raw_qty"),
                row.get("raw_unit"),
                row.get("raw_warehouse"),
            )
            product["quantity"] = product["qty"]  # backward compatible field
            return jsonify({"found": True, "data": product})
        else:
            return jsonify({"found": False})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("Local API พร้อมแล้ว รอรับ request ที่ port 5000")
    app.run(host="0.0.0.0", port=5000)
