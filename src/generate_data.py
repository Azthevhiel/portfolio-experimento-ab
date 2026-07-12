"""
Generador de dataset sintético: experimento A/B de un cartel de promoción en
góndola, en una cadena mayorista (mismo tipo de negocio que Maxiconsumo).

IMPORTANTE: dataset 100% sintético para fines de práctica analítica y
portafolio. No son datos reales de ninguna empresa ni cliente. Este repo es
autocontenido: no depende de los otros proyectos del portafolio.

Contexto simulado: se prueba un cartel de promoción nuevo (variante B) contra
el cartel actual (variante A) para la categoría "Bebidas y almacén", en 4
sucursales, durante 10 semanas. La variante mostrada cada día se asigna con
"block randomization": para cada sucursal y cada día de la semana, se sortea
qué mitad de las semanas (5 de 10) muestra cada variante -- así el día de la
semana (que afecta el tráfico) no puede desbalancear la comparación entre A y B.

Uso:
    python src/generate_data.py
Genera:
    data/raw/experimento_cartel.csv   (un registro por visitante)
"""

import numpy as np
import pandas as pd
from pathlib import Path

RANDOM_SEED = 34
rng = np.random.default_rng(RANDOM_SEED)

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

FECHA_INICIO = pd.Timestamp("2026-03-02")  # lunes
N_SEMANAS = 10
DIAS_ABIERTO = [0, 1, 2, 3, 4, 5]  # lunes(0) a sábado(5); domingo(6) cerrado
NOMBRES_DIA = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado"}

CATEGORIA_PROMOCIONADA = "Bebidas y almacén"

SUCURSAL_PARAMS = {
    "Centro": {"visitas_media": 140, "conversion_base": 0.16, "ticket_medio": 42000},
    "Norte":  {"visitas_media": 95,  "conversion_base": 0.19, "ticket_medio": 47000},
    "Oeste":  {"visitas_media": 110, "conversion_base": 0.15, "ticket_medio": 39000},
    "Sur":    {"visitas_media": 80,  "conversion_base": 0.21, "ticket_medio": 51000},
}

# Lunes y viernes tienen más tráfico (reposición de stock semanal de los
# comercios clientes); el sábado es el día de menor tráfico mayorista.
DOW_TRAFFIC_MULT = {0: 1.15, 1: 1.05, 2: 1.0, 3: 0.95, 4: 1.10, 5: 0.75}

# Efecto real inyectado del cartel nuevo (variante B) -- esto es lo que el
# experimento tiene que poder detectar.
EFECTO_CONVERSION_B = 0.04   # +4 puntos porcentuales de conversión
EFECTO_TICKET_B = 0.08       # +8% relativo en el ticket promedio de quienes compran

# ---------------------------------------------------------------------------
# 1. Asignación de variante por sucursal / día de semana / semana
#    (block randomization: 5 semanas con A y 5 con B para cada combinación
#    sucursal x día de semana, para que el día de semana no confunda el
#    resultado del experimento)
# ---------------------------------------------------------------------------
asignacion = {}
for sucursal in SUCURSAL_PARAMS:
    for dow in DIAS_ABIERTO:
        variantes = ["A"] * (N_SEMANAS // 2) + ["B"] * (N_SEMANAS // 2)
        rng.shuffle(variantes)
        for semana_idx, variante in enumerate(variantes):
            asignacion[(sucursal, dow, semana_idx)] = variante

# ---------------------------------------------------------------------------
# 2. Simulación de visitantes día a día
# ---------------------------------------------------------------------------
registros = []
visitante_id = 1

for semana_idx in range(N_SEMANAS):
    for dow in DIAS_ABIERTO:
        fecha = FECHA_INICIO + pd.Timedelta(weeks=semana_idx, days=dow)
        for sucursal, params in SUCURSAL_PARAMS.items():
            variante = asignacion[(sucursal, dow, semana_idx)]

            visitas_esperadas = params["visitas_media"] * DOW_TRAFFIC_MULT[dow]
            n_visitantes = rng.poisson(visitas_esperadas)

            # ruido propio del día (además del binomial), para que la
            # variabilidad día a día sea realista y no artificialmente baja
            ruido_dia = rng.normal(0, 0.03)

            p_conversion = params["conversion_base"] + ruido_dia
            if variante == "B":
                p_conversion += EFECTO_CONVERSION_B
            p_conversion = min(max(p_conversion, 0.01), 0.85)

            ticket_medio_dia = params["ticket_medio"]
            if variante == "B":
                ticket_medio_dia *= (1 + EFECTO_TICKET_B)

            compras = rng.random(n_visitantes) < p_conversion

            for compro in compras:
                monto = np.nan
                if compro:
                    monto = max(3000, rng.normal(ticket_medio_dia, ticket_medio_dia * 0.35))
                    monto = round(float(monto), 2)
                registros.append({
                    "visitante_id": f"VIS{visitante_id:07d}",
                    "fecha": fecha,
                    "dia_semana": NOMBRES_DIA[dow],
                    "semana": semana_idx + 1,
                    "sucursal": sucursal,
                    "variante": variante,
                    "categoria": CATEGORIA_PROMOCIONADA,
                    "compro": bool(compro),
                    "monto_ars": monto,
                })
                visitante_id += 1

df = pd.DataFrame(registros).sort_values(["fecha", "sucursal", "visitante_id"]).reset_index(drop=True)
df.to_csv(DATA_DIR / "experimento_cartel.csv", index=False)

print("Registros (visitantes):", len(df))
print("Rango de fechas:", df["fecha"].min().date(), "a", df["fecha"].max().date())
print("\nVisitantes por variante:")
print(df["variante"].value_counts())
print("\nConversión general por variante:")
print(df.groupby("variante")["compro"].mean().round(3))
print("\nTicket promedio (solo compradores) por variante:")
print(df[df["compro"]].groupby("variante")["monto_ars"].mean().round(0))
