"""
Demo interactiva: experimento A/B del cartel de promoción en góndola.

Corre con: streamlit run app/streamlit_app.py

Requiere haber corrido antes el notebook 01 (o generar el dataset con
`python src/generate_data.py` y correr ese notebook) para tener
data/processed/metricas_diarias.csv.

Tiene dos secciones: un dashboard de resultados del experimento ya corrido, y
una calculadora reutilizable de tamaño de muestra para futuros experimentos.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats
from statsmodels.stats.power import TTestIndPower

st.set_page_config(page_title="Experimento A/B — cartel de promoción", layout="wide")

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
METRICAS_PATH = BASE_DIR / "data" / "processed" / "metricas_diarias.csv"


@st.cache_data
def cargar_metricas():
    return pd.read_csv(METRICAS_PATH, parse_dates=["fecha"])


if not METRICAS_PATH.exists():
    st.error(
        "No se encontró data/processed/metricas_diarias.csv. "
        "Corré antes el notebook 01_eda.ipynb "
        "(o `python src/generate_data.py` y luego ese notebook)."
    )
    st.stop()


st.title("Experimento A/B — cartel de promoción en góndola")
st.caption(
    "Dataset 100% sintético. Cadena mayorista con 4 sucursales; se testea un "
    "cartel nuevo (variante B) contra el actual (variante A), randomizado por "
    "día y bloqueado por día de semana."
)

tab_resultados, tab_calculadora = st.tabs(["Resultados del experimento", "Calculadora de tamaño de muestra"])

# ---------------------------------------------------------------------------
# TAB 1: Resultados del experimento
# ---------------------------------------------------------------------------
with tab_resultados:
    metricas = cargar_metricas()

    sucursales_disponibles = sorted(metricas["sucursal"].unique())
    sucursales_sel = st.multiselect(
        "Sucursales a incluir", sucursales_disponibles, default=sucursales_disponibles
    )

    datos = metricas[metricas["sucursal"].isin(sucursales_sel)]
    conv_A = datos.loc[datos["variante"] == "A", "conversion_dia"]
    conv_B = datos.loc[datos["variante"] == "B", "conversion_dia"]
    ticket_A = datos.loc[datos["variante"] == "A", "ticket_promedio_dia"].dropna()
    ticket_B = datos.loc[datos["variante"] == "B", "ticket_promedio_dia"].dropna()

    if len(conv_A) > 1 and len(conv_B) > 1:
        t_conv, p_conv = stats.ttest_ind(conv_B, conv_A, equal_var=False)
        t_ticket, p_ticket = stats.ttest_ind(ticket_B, ticket_A, equal_var=False)
        diff_conv = conv_B.mean() - conv_A.mean()
        diff_ticket = ticket_B.mean() - ticket_A.mean()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Conversión A", f"{conv_A.mean():.1%}")
        col2.metric("Conversión B", f"{conv_B.mean():.1%}", f"{diff_conv*100:+.2f} pp")
        col3.metric("Ticket promedio A", f"${ticket_A.mean():,.0f}")
        col4.metric("Ticket promedio B", f"${ticket_B.mean():,.0f}", f"{diff_ticket/ticket_A.mean()*100:+.1f}%")

        col_a, col_b = st.columns(2)
        with col_a:
            veredicto = "significativa ✅" if p_conv < 0.05 else "no significativa"
            st.info(f"**Conversión:** diferencia {veredicto} (p = {p_conv:.2e}, alpha = 0.05)")
        with col_b:
            veredicto = "significativa ✅" if p_ticket < 0.05 else "no significativa"
            st.info(f"**Ticket promedio:** diferencia {veredicto} (p = {p_ticket:.2e}, alpha = 0.05)")

        st.divider()

        col_izq, col_der = st.columns(2)
        with col_izq:
            st.subheader("Conversión diaria por variante")
            fig_conv = px.box(datos, x="variante", y="conversion_dia", color="variante", points="all")
            fig_conv.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_conv, width='stretch')

        with col_der:
            st.subheader("Ticket promedio diario por variante")
            fig_ticket = px.box(datos, x="variante", y="ticket_promedio_dia", color="variante", points="all")
            fig_ticket.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_ticket, width='stretch')

        st.subheader("Tendencia diaria (promedio entre sucursales seleccionadas)")
        tendencia = datos.groupby(["fecha", "variante"])["conversion_dia"].mean().reset_index()
        fig_tendencia = px.line(
            tendencia, x="fecha", y="conversion_dia", color="variante",
            markers=True,
        )
        fig_tendencia.update_layout(height=400)
        st.plotly_chart(fig_tendencia, width='stretch')

        st.subheader("Efecto por sucursal")
        efecto_sucursal = (
            datos.groupby(["sucursal", "variante"])["conversion_dia"].mean().unstack()
        )
        if "A" in efecto_sucursal.columns and "B" in efecto_sucursal.columns:
            efecto_sucursal["diferencia_pp"] = (efecto_sucursal["B"] - efecto_sucursal["A"]) * 100
            fig_sucursal = px.bar(
                efecto_sucursal.reset_index(), x="diferencia_pp", y="sucursal", orientation="h",
                color="diferencia_pp", color_continuous_scale="RdYlGn",
            )
            fig_sucursal.update_layout(height=350, coloraxis_showscale=False)
            st.plotly_chart(fig_sucursal, width='stretch')
    else:
        st.warning("Seleccioná al menos una sucursal con datos de ambas variantes.")

# ---------------------------------------------------------------------------
# TAB 2: Calculadora de tamaño de muestra
# ---------------------------------------------------------------------------
with tab_calculadora:
    st.markdown(
        """
        Calculadora reutilizable para decidir, **antes** de lanzar un
        experimento nuevo, cuántos días de datos por variante hacen falta.
        Usa el mismo enfoque del `notebooks/02_tamano_muestra.ipynb`: la
        unidad de análisis es el día (no el visitante individual), porque en
        este tipo de experimento la variante se asigna por día.
        """
    )

    col_izq, col_der = st.columns(2)

    with col_izq:
        st.subheader("Parámetros")
        tasa_base = st.slider("Tasa de conversión base (variante A)", 0.05, 0.50, 0.18, 0.01)
        mde_pp = st.slider("Efecto mínimo a detectar (puntos porcentuales)", 0.01, 0.10, 0.04, 0.005)
        sd_diaria = st.slider("Desvío estándar diario de la conversión (histórico)", 0.01, 0.15, 0.057, 0.001)
        alpha = st.slider("Alpha (probabilidad de falso positivo)", 0.01, 0.10, 0.05, 0.01)
        poder = st.slider("Poder deseado (1 - probabilidad de falso negativo)", 0.70, 0.95, 0.80, 0.05)

    with col_der:
        st.subheader("Resultado")
        cohens_d = mde_pp / sd_diaria
        analisis = TTestIndPower()
        dias_necesarios = analisis.solve_power(effect_size=cohens_d, alpha=alpha, power=poder, ratio=1.0)

        st.metric("Días necesarios por variante", f"{dias_necesarios:.0f}")
        st.caption(f"Cohen's d equivalente: {cohens_d:.3f}")
        st.caption(f"Duración total estimada (ambas variantes en paralelo): ~{dias_necesarios:.0f} días")

        mdes = np.linspace(0.01, 0.10, 30)
        dias_por_mde = [
            analisis.solve_power(effect_size=m / sd_diaria, alpha=alpha, power=poder, ratio=1.0)
            for m in mdes
        ]
        fig_sensibilidad = go.Figure()
        fig_sensibilidad.add_trace(go.Scatter(x=mdes * 100, y=dias_por_mde, mode="lines+markers"))
        fig_sensibilidad.add_vline(x=mde_pp * 100, line_dash="dash", line_color="crimson")
        fig_sensibilidad.update_layout(
            xaxis_title="MDE (puntos porcentuales)", yaxis_title="Días necesarios por variante",
            height=350, title="Sensibilidad: efecto más chico -> más días necesarios",
        )
        st.plotly_chart(fig_sensibilidad, width='stretch')

    with st.expander("¿Por qué se calcula a nivel día y no a nivel visitante?"):
        st.markdown(
            """
            Porque la variante del cartel se asigna una vez por día (no se
            puede mostrar una variante distinta a cada visitante individual
            dentro del mismo día). Los visitantes de un mismo día comparten el
            mismo tratamiento y contexto, así que no son observaciones
            independientes entre sí. Calcular el tamaño de muestra a nivel
            visitante subestima gravemente el esfuerzo real del experimento.
            Ver `docs/guia_tecnica_conceptos.md` para el detalle completo.
            """
        )
