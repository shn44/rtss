from flask import Flask, render_template, request, jsonify, session
import os
import json
from collections import defaultdict

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave_secreta_padrao")


class RouteOptimizer:
    def __init__(self):
        self.street_order = []
        self.deliveries = defaultdict(list)

    def set_street_order(self, streets):
        """Define a ordem pré-estabelecida das ruas"""
        self.street_order = [
            street.strip().upper() for street in streets if street.strip()
        ]

    def add_delivery(self, street, numbers):
        """Adiciona entregas para uma rua específica"""
        street_upper = street.strip().upper()
        if street_upper and numbers:
            # Converte números para inteiro e remove duplicatas
            unique_numbers = list(
                set([int(num) for num in numbers if str(num).strip()])
            )
            unique_numbers.sort()
            self.deliveries[street_upper] = unique_numbers

    def generate_optimized_route(self):
        """Gera a rota otimizada baseada na ordem pré-definida"""
        optimized_route = []

        # Segue a ordem pré-definida das ruas
        for street in self.street_order:
            if street in self.deliveries and self.deliveries[street]:
                numbers_str = ", ".join(map(str, self.deliveries[street]))
                optimized_route.append(f"{street}, {numbers_str}")

        # Adiciona ruas que não estão na ordem pré-definida (se houver)
        for street in self.deliveries:
            if street not in self.street_order and self.deliveries[street]:
                numbers_str = ", ".join(map(str, self.deliveries[street]))
                optimized_route.append(f"{street}, {numbers_str}")

        return optimized_route


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/save_streets", methods=["POST"])
def save_streets():
    try:
        streets_text = request.json.get("streets", "")
        streets = [
            street.strip() for street in streets_text.split(",") if street.strip()
        ]

        if "optimizer" not in session:
            session["optimizer"] = {}

        session["optimizer"]["street_order"] = streets
        session.modified = True

        return jsonify(
            {
                "status": "success",
                "message": "Ordem das ruas salva!",
                "streets": streets,
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/get_streets", methods=["GET"])
def get_streets():
    """Retorna a lista de ruas salvas"""
    try:
        street_order = session.get("optimizer", {}).get("street_order", [])
        return jsonify({"status": "success", "streets": street_order})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/generate_route", methods=["POST"])
def generate_route():
    try:
        deliveries_data = request.json.get("deliveries", [])

        # Recupera a ordem das ruas da sessão
        street_order = session.get("optimizer", {}).get("street_order", [])

        # Cria e configura o otimizador
        optimizer = RouteOptimizer()
        optimizer.set_street_order(street_order)

        # Adiciona as entregas
        for delivery in deliveries_data:
            street = delivery.get("street", "")
            numbers = delivery.get("numbers", [])
            if street and numbers:
                optimizer.add_delivery(street, numbers)

        # Gera a rota otimizada
        optimized_route = optimizer.generate_optimized_route()

        return jsonify(
            {
                "status": "success",
                "route": optimized_route,
                "streets_saved": len(street_order) > 0,
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
