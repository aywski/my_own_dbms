import json
from flask import Flask, request, jsonify
from var_types import DataType

app = Flask(__name__)
app.json.sort_keys = False

def read_db():
    try:
        with open('db.json', 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def write_db(db):
    with open('db.json', 'w') as f:
        json.dump(db, f, indent=4)

@app.route('/tables', methods=['GET'])
def get_tables():
    db = read_db()
    return jsonify(list(db.keys()))

@app.route('/create_table', methods=['POST'])
def create_table():
    data = request.json
    print(f"Получен запрос на создание таблицы: {data}")  # Лог для отладки
    table_name = data.get('table_name')
    fields = data.get('fields')

    if not table_name or not fields:
        return jsonify({"error": "Некорректные данные"}), 400

    db = read_db()
    if table_name in db:
        return jsonify({"error": "Таблица уже существует"}), 400

    db[table_name] = {"fields": fields, "records": []}
    write_db(db)

    print(f"Таблица {table_name} создана с полями {fields}")  # Лог успешного создания
    return jsonify({"success": f"Таблица {table_name} создана"}), 200

@app.route('/delete_table/<table_name>', methods=['DELETE'])
def delete_table(table_name):
    db = read_db()
    if table_name not in db:
        return jsonify({"error": "Таблица не найдена"}), 404

    del db[table_name]
    write_db(db)
    return jsonify({"success": f"Таблица {table_name} удалена"}), 200

@app.route('/table_fields/<table_name>', methods=['GET'])
def get_table_fields(table_name):
    db = read_db()
    if table_name in db:
        return jsonify(db[table_name]["fields"])
    else:
        return jsonify({"error": "Таблица не найдена"}), 404

# add record to the table
@app.route('/add_record/<table_name>', methods=['POST'])
def add_record(table_name):
    data = request.json
    print(f"Получен запрос на добавление записи: {data}")  # Лог для отладки

    db = read_db()
    if table_name not in db:
        return jsonify({"error": "Таблица не найдена"}), 404

    fields = db[table_name]["fields"]
    record = {}

    # record validating
    for field_name, field_type in fields:
        value = data.get(field_name)
        if DataType(value, field_type).check_field_type():
            pass
        else:
            return jsonify({"error": "Error"}), 400
        record[field_name] = value

    db[table_name]["records"].append(record)
    write_db(db)
    return jsonify({"success": f"Record is added {table_name}"}), 200

@app.route('/records/<table_name>', methods=['GET'])
def get_records(table_name):
    db = read_db()
    if table_name in db:
        return jsonify(db[table_name]["records"])
    else:
        return jsonify({"error": "Table not found"}), 404

@app.route('/delete_record/<table_name>', methods=['DELETE'])
def delete_record(table_name):
    data = request.json
    db = read_db()
    if table_name not in db:
        return jsonify({"error": "Table not found"}), 404

    records = db[table_name]["records"]
    if data in records:
        records.remove(data)
        write_db(db)
        return jsonify({"success": "Запись удалена"}), 200
    else:
        return jsonify({"error": "Запись не найдена"}), 404


if __name__ == '__main__':
    app.run(debug=True)
