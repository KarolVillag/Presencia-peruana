from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns
import io, base64
from googletrans import Translator
translator = Translator()

app = Flask(__name__)

# --- Datos del restaurante ---
menu_df = pd.DataFrame({
    "plato": ["Papa Rellena", "Tequeños", "Wantán", "Boliyuca de Queso"],
    "precio": [12, 15, 10, 14]
})

ventas = pd.DataFrame({
    "plato": ["Papa Rellena", "Tequeños", "Wantán", "Papa Rellena", "Tequeños"],
    "cantidad": [40, 35, 25, 30, 20]
})

# --- Opiniones de clientes ---
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

opiniones_df = pd.DataFrame({
    "opinion": [
        "La papa rellena estuvo deliciosa!",
        "Los tequeños muy ricos, me encantaron",
        "Me encantó el wantán, excelente sabor",
        "El servicio fue rápido y amable",
        "Muy buena atención, volveré pronto",
        "Excelente comida, todo fresco y sabroso"
    ]
})

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    opcion = data.get("opcion")

    if opcion == "1":  # Menú
        menu_items = menu_df.to_dict(orient="records")
        menu_texto = "🍽️ NUESTRO MENÚ DE HOY:<br>" + "<br>".join(
            [f"• {item['plato']} = S/.{item['precio']}" for item in menu_items]
        )
        return jsonify({"respuesta": menu_texto + "<br><br>"})

    elif opcion == "2":  # Recomendación
        X = np.array(ventas.groupby("plato")["cantidad"].sum()).reshape(-1,1)
        kmeans = KMeans(n_clusters=2, random_state=42).fit(X)
        platos = ventas["plato"].unique()
        cluster_labels = dict(zip(platos, kmeans.labels_))
        cluster_sums = {i: X[kmeans.labels_==i].sum() for i in range(2)}
        best_cluster = max(cluster_sums, key=cluster_sums.get)
        recomendado = [plato for plato, cl in cluster_labels.items() if cl == best_cluster]

        return jsonify({"respuesta": f"📢 TE RECOMENDAMOS PROBAR:<br>• {', '.join(recomendado)}<br><br>"})

    elif opcion == "3":  # Opiniones
        global opiniones_df

        def clasificar_sentimiento(texto):
            traducido = translator.translate(texto, src="es", dest="en").text
            score = sia.polarity_scores(traducido)["compound"]
            if score >= 0.05:
                return "positivo"
            elif score <= -0.05:
                return "negativo"
            else:
                return "neutro"

        opiniones_df["sentimiento"] = opiniones_df["opinion"].apply(clasificar_sentimiento)

        positivos = (opiniones_df["sentimiento"] == "positivo").sum()
        total = len(opiniones_df)

        if total == 0:
            return jsonify({"respuesta": "Aún no hay opiniones registradas.<br><br>"})

        porcentaje = (positivos / total) * 100
        resumen = "En general los clientes están satisfechos." if porcentaje > 50 else "Varios clientes señalaron aspectos a mejorar."

        return jsonify({
            "respuesta": f"📍 OPINIONES DE LOS CLIENTES:<br>"
                        f"• {porcentaje:.1f}% de reseñas fueron positivas.<br>"
                        f"• {resumen}<br><br>"
        })

    elif opcion == "4":  # Estadísticas
        df = ventas.groupby("plato")["cantidad"].sum().reset_index()
        plato_top = df.loc[df["cantidad"].idxmax()]

        img = io.BytesIO()
        sns.barplot(x="plato", y="cantidad", data=df)
        plt.title("Ventas totales por plato")
        plt.savefig(img, format="png")
        plt.close()
        img.seek(0)
        img_base64 = base64.b64encode(img.getvalue()).decode()

        mensaje = (
            f"📊 ESTADÍSTICAS DE VENTAS:<br>"
            f"• El plato más vendido es {plato_top['plato']} con {plato_top['cantidad']} pedidos.<br>"
            f"• Aquí te mostramos un resumen visual:<br><br>"
        )

        return jsonify({"respuesta": mensaje, "imagen": f"data:image/png;base64,{img_base64}"})

    elif opcion == "5":  # Promoción
        X = [[12],[15],[10],[14]]
        y = ["Promo bebida","Promo postre","Promo entrada","Promo bebida"]
        clf = DecisionTreeClassifier().fit(X, y)
        promo = clf.predict([[13]])[0]
        return jsonify({"respuesta": f"🚨 PROMOCIÓN ESPECIAL: • {promo}<br><br>"})

    else:
        return jsonify({"respuesta": "Opción no válida"})

if __name__ == "__main__":
    app.run()