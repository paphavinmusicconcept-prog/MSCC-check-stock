import re


_UNIT_PATTERN = (
    "ตัว|ใบ|อัน|ชิ้น|ชุด|เส้น|เครื่อง|กล่อง|ตู้|ผืน|หลอด"
)


def clean_text(value):
    return (
        str(value if value is not None else "")
        .replace("\u00a0", " ")
        .replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
    )


def clean_text_compact(value):
    return re.sub(r"\s+", " ", clean_text(value)).strip()


def clean_product_name(value):
    name = clean_text_compact(value)

    # Remove leaked CSV tail: 16";;;;;;2"ใบ or 16",,,,,,2,"ใบ.
    # The optional quote immediately after the real product size is preserved.
    name = re.sub(
        rf"([^\s,;])([\"']?)[,;]{{2,}}\s*\d+\s*[\"']?\s*,?\s*[\"']?\s*(?:{_UNIT_PATTERN})\s*$",
        r"\1\2",
        name,
        flags=re.IGNORECASE,
    )

    # Remove a quantity/unit suffix if it was already separated from the name.
    name = re.sub(
        rf"\s+\d+\s*[\"']?\s*(?:{_UNIT_PATTERN})\s*$",
        "",
        name,
        flags=re.IGNORECASE,
    )

    name = re.sub(r"[;,]+$", "", name).strip()
    name = re.sub(r'"{2,}', '"', name)

    return name.strip()


def to_number(value):
    cleaned = re.sub(r"[^\d.-]", "", str(value if value is not None else ""))
    try:
        return float(cleaned) if cleaned else 0
    except ValueError:
        return 0


def normalize_product(raw_sku, raw_name, raw_qty, raw_unit=None, raw_warehouse=None):
    qty = to_number(raw_qty)
    if qty.is_integer():
        qty = int(qty)

    return {
        "sku": clean_text_compact(raw_sku),
        "name": clean_product_name(raw_name),
        "qty": qty,
        "unit": clean_text_compact(raw_unit or "ตัว"),
        "warehouse": clean_text_compact(raw_warehouse),
    }
