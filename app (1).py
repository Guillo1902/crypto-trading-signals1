import os
import json
import firebase_admin
from firebase_admin import credentials, db

# Leer las credenciales del entorno Streamlit Secrets
firebase_config = st.secrets["FIREBASE"]

# Parsear la clave privada correctamente (importante para mantener saltos de línea)
firebase_config["private_key"] = firebase_config["private_key"].replace("\\n", "\n")

# Inicializar Firebase (una sola vez)
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://grupo10-b7d3b-default-rtdb.firebaseio.com/"
    })

# Función para analizar historial de una criptomoneda
def analizar_historial(moneda_id):
    now = datetime.datetime.now()
    hace_una_hora = now - datetime.timedelta(hours=1)

    base_ref = db.reference("crypto_prices").child(moneda_id)
    historial = base_ref.child("historial").get()
    actual = base_ref.child("actual").get()

    if historial is None or actual is None:
        return None

    precios_filtrados = []
    for timestamp, datos in historial.items():
        try:
            ts = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            if ts >= hace_una_hora:
                precios_filtrados.append(datos["Price"])
        except:
            pass

    if not precios_filtrados:
        return None

    actual_price = actual.get("Price", 0)
    max_1h = max(precios_filtrados)
    min_1h = min(precios_filtrados)
    avg_1h = sum(precios_filtrados) / len(precios_filtrados)
    signal = "B" if actual_price > avg_1h else "S"

    return {
        "Crypto": moneda_id,
        "Actual Price": actual_price,
        "Highest 1H": round(max_1h, 6),
        "Lowest 1H": round(min_1h, 6),
        "AVG Price": round(avg_1h, 6),
        "Signal": signal
    }

# Lista de criptomonedas analizadas
cryptos = [
    'bitcoin', 'ethereum', 'binancecoin', 'usd-coin', 'ripple',
    'binance-peg-dogecoin', 'wrapped-solana', 'bridged-tether-fuse',
    'the-open-network', 'ada-the-dog'
]

# Interfaz de usuario con Streamlit
st.set_page_config(page_title="Crypto Trading Signals", layout="wide")
st.title("📊 Señales de Trading en Tiempo Real")
st.write("Análisis de criptomonedas con datos en vivo desde Firebase.")

resultados = []
for moneda in cryptos:
    r = analizar_historial(moneda)
    if r:
        resultados.append(r)

if resultados:
    df_resultados = pd.DataFrame(resultados)
    st.dataframe(df_resultados, use_container_width=True)
else:
    st.warning("No se pudo recuperar información desde Firebase.")
