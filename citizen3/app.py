from kafka import KafkaProducer, KafkaConsumer
import json
import sqlite3
import os
from threading import Thread
from flask import Flask, jsonify
from flask_cors import CORS
import time
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas


# Configuración
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
TOPIC = 'votes_topic'
CITIZEN_ID = int(os.getenv('CITIZEN_ID', 3))
DB_NAME = os.getenv('DB_NAME', 'votes.db')

# Inicializar base de datos
if not os.path.exists(DB_NAME):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE votes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  citizen_id INTEGER,
                  vote TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute("INSERT INTO votes (citizen_id, vote) VALUES (?, ?)", (CITIZEN_ID, "Initialized"))
    conn.commit()
    conn.close()

# Configurar Kafka
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

def consume_messages():
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='earliest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    for message in consumer:
        data = message.value
        print(f"Citizen {CITIZEN_ID} received: {data}")
        
        # Almacenar en DB
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO votes (citizen_id, vote) VALUES (?, ?)", 
                 (data['citizen_id'], data['message']))
        conn.commit()
        conn.close()

@app.route('/send/<message>', methods=['GET'])
def send_message(message):
    data = {
        'citizen_id': CITIZEN_ID,
        'message': message
    }
    producer.send(TOPIC, value=data)
    return jsonify({"status": "message sent", "content": data})

@app.route('/votes', methods=['GET'])
def get_votes():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM votes")
    votes = c.fetchall()
    conn.close()
    return jsonify(votes)

if __name__ == '__main__':
    # Iniciar consumidor en segundo plano
    Thread(target=consume_messages, daemon=True).start()
    
    # Iniciar servidor Flask
    app.run(host='0.0.0.0', port=5000)
