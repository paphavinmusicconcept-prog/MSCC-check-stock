# ============================================================
# api.py — Local API รันบนคอมที่ร้าน
# รับ SKU จากบอท → ดึงสต็อกจาก MySQL → ส่งกลับ
# ============================================================

from flask import Flask, request, jsonify
import mysql.connector

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

# ── Endpoint รับ request จากบอท ────────────────────────────
@app.route("/stock", methods=["GET"])
def get_stock():
    sku = request.args.get("sku", "").strip()

    if not sku:
        return jsonify({"error": "ไม่ได้ส่ง SKU มา"}), 400

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        sql = f"SELECT {COL_NAME}, {COL_SKU}, {COL_QTY} FROM {TABLE} WHERE {COL_SKU} = %s LIMIT 1"
        cursor.execute(sql, (sku,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if row:
            return jsonify({"found": True, "data": row})
        else:
            return jsonify({"found": False})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("Local API พร้อมแล้ว รอรับ request ที่ port 5000")
    app.run(host="0.0.0.0", port=5000)
