# Migrate last database mantaining the users and experiments
import sqlite3
from shutil import copyfile
from datetime import datetime
import os

current_db_path = './ubumlaas/data.sqlite'
last_db_path = './data_base.sqlite'

current_db = sqlite3.connect(current_db_path)
last_db = sqlite3.connect(last_db_path)


def get_table_names(db):
    cursor = db.cursor()
    result = cursor.execute(
                        "SELECT name FROM sqlite_master \
                        WHERE type='table'")\
                   .fetchall()
    cursor.close()
    return set(map(lambda x: x[0], result))


def get_index_of_primary_key(db, table):
    info = get_table_info(db, table)
    indexes = []
    pk_names = []
    loop_index = 0
    for _, name, _, _, _, pk in info:
        if pk == 1:
            indexes.append(loop_index)
            pk_names.append(name)
        loop_index += 1

    return pk_names, indexes


def remove_tables(db, tables):
    cursor = db.cursor()
    for t in tables:
        cursor.execute("DROP TABLE "+t)
    cursor.close()


def get_table_info(db, table):
    return db.cursor().execute("PRAGMA table_info('" + table + "')").fetchall()


def add_tables(db, tables):
    cursor = db.cursor()
    for t in tables:
        sql_command = "CREATE TABLE " + t + " ( "
        loop_index = 0
        for _, name, _type, _null, _default, pk in tables[t]:
            appendix = ""
            if pk == 1:
                appendix += "PRIMARY KEY"
            elif _null == 1:
                appendix += "NOT NULL"
            if _default is not None:
                appendix += " DEFAULT "+_default
            sql_command += name + " " + _type + " " + appendix

            loop_index += 1
            if(loop_index < len(tables[t])):
                sql_command += ","
        sql_command += ");"
        cursor.execute(sql_command)
    cursor.close()


def get_column_information(table, column):
    table_info = get_table_info(last_db, table)
    foreign_key_info = last_db.cursor().execute("PRAGMA foreign_key_list('" + table + "')").fetchall()
    _, _, _type, _null, _default, _ = next(filter(lambda x: x[1] == column, table_info))
    try:
        foreign_key_data = next(filter(lambda x: x[3] == column, foreign_key_info))
    except StopIteration:
        foreign_key_data = None
    column_information = " " + _type
    if _null != 0:
        column_information += " NOT NULL"
    if _default is not None:
        column_information += " DEFAULT "+_default
    if foreign_key_data is not None:
        column_information += " REFERENCES `"+foreign_key_data[2]+"`(`"+foreign_key_data[4]+"`)"
    return column_information


def add_columns(db, table, columns):
    cursor = db.cursor()
    for c in columns:
        column_information = get_column_information(table, c)
        cursor.execute("ALTER TABLE "+table+" ADD COLUMN "+c+" "+column_information)
    cursor.close()


def drop_columns(db, table, columns):
    cursor = db.cursor()
    for c in columns:
        cursor.execute("ALTER TABLE "+table+" DROP "+c)
    cursor.close()


def change_columns_type(db, table, columns):
    cursor = db.cursor()
    for c in columns:
        cursor.execute("ALTER TABLE "+table+" ALTER COLUMN "+c+" "+columns[c])
    cursor.close()


def update_all_columns():
    # In this call last_db and current_db must have the same tables
    last_tables = get_table_names(last_db)
    for table in last_tables:
        columns_last = {k: v for k, v in map(lambda x: (x[1], x[2]), get_table_info(last_db, table))}
        columns_current = {k: v for k, v in map(lambda x: (x[1], x[2]), get_table_info(current_db, table))}
        columns_to_add = {}
        # columns_to_remove = []
        # columns_to_modify = {}
        for name in columns_last:
            current_column_type = columns_current.get(name, None)
            if current_column_type is None:
                columns_to_add[name] = columns_last[name]
            """elif current_column_type != columns_last[name]:
                columns_to_modify[name] = columns_last[name]"""
        """for name in columns_current:
            last_column_type = columns_last.get(name, None)
            if last_column_type is None:
                columns_to_remove.append(name)"""
        add_columns(current_db, table, columns_to_add)
        # change_columns_type(current_db, table, columns_to_modify)
        # drop_columns(current_db, table, columns_to_remove)


def get_line(db, table, condition):
    cursor = db.cursor()
    result = cursor.execute("SELECT * FROM "+ table +" WHERE "+condition).fetchone()
    cursor.close()
    return result


def insert(db, table, values):
    cursor = db.cursor()
    query = "INSERT INTO " + table + " VALUES("
    query += "?"
    for v in values[1:]:
        query += ",?"
    query += ")"
    cursor.execute(query, values)
    cursor.close()


def update(db, table, keys, values, where):
    cursor = db.cursor()
    query = "UPDATE " + table + " SET "
    query += str(keys[0]) + " = ?"
    for k, v in zip(keys[1:], values[1:]):
        query += "," + str(k) + " = ?"
    query += " WHERE "+where
    cursor.execute(query, values)
    cursor.close()


def insert_and_update_information():
    last_tables = get_table_names(last_db)
    cursor_last = last_db.cursor()
    cursor_current = current_db.cursor()
    for table in last_tables:
        columns_last = [k for k in map(lambda x: x[1], get_table_info(last_db, table))]
        content_last = cursor_last.execute("SELECT * FROM "+table).fetchall()
        pk_names, indexes = get_index_of_primary_key(last_db, table)
        for line in content_last:
            key = []
            for i in indexes:
                key.append(line[i])
            condition = str(pk_names[0])+" = '"+str(key[0])+"'"
            for j in range(0, len(pk_names[1:])):
                condition += " AND " + str(pk_names[j+1])+" = '"+str(key[j+1])+"'"
            row = get_line(current_db, table, condition)
            if row is None:
                insert(current_db, table, line)
            elif tuple(row) != tuple(line):
                update(current_db, table, columns_last, line, condition)

    cursor_current.close()
    cursor_last.close()


def backup():
    if not os.path.exists("./backups/"):
        os.makedirs("./backups/")
    copyfile(current_db_path, "./backups/db-"+datetime.now().strftime("%d-%m-%Y--%H-%M-%S")+".sqlite")


if __name__ == "__main__":
    backup()
    current_tables = get_table_names(current_db)
    last_tables = get_table_names(last_db)
    tables_to_remove = current_tables.difference(last_tables)
    tables_to_add = last_tables.difference(current_tables)

    remove_tables(current_db, tables_to_remove)
    tables_information = dict()
    for t in tables_to_add:
        tables_information[t] = get_table_info(last_db, t)
    add_tables(current_db, tables_information)

    update_all_columns()
    insert_and_update_information()

current_db.commit()
current_db.close()
last_db.close()