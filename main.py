import os
import time
import psycopg2
from flask import Flask
from app.routes import router
from app.database import init_db

app = Flask(__name__)
app.register_blueprint(router)


def wait_for_db(retries=15, delay=3):
    for i in range(retries):
        try:
            init_db()
            print("Banco de dados conectado e inicializado.")
            return
        except psycopg2.Error as e:
            print(f"Aguardando banco... tentativa {i + 1}/{retries}: {e}")
            time.sleep(delay)
    raise RuntimeError("Não foi possível conectar ao banco de dados.")


if __name__ == "__main__":
    wait_for_db()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
