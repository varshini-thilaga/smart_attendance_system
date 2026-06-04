import sqlite3

def status():
    connect = sqlite3.connect("Face-DataBase")
    try:
        cursor = connect.execute("SELECT trained_at FROM TrainLog LIMIT 1")
        row = cursor.fetchone()
        connect.close()
        if row:
            return row[0]
        return "Model not trained yet."
    except:
        connect.close()
        return "Model not trained yet."
