"""
MANDO INTEGRAL DE PREPARACIÓN ANTE EMERGENCIAS
Dashboard educativo (BI) para identificar e interpretar los elementos de un
tablero de gestión de crisis corporativo, en un caso realista peruano
multi-sede: Corporación Kallpa Industrial S.A.C.

Streamlit 1.38.0 · Pandas 2.2.2 · Plotly 5.24.1
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ══════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Mando Integral de Emergencias | Kallpa Industrial",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY, STEEL, AMBER = "#1F3864", "#2E5266", "#B45F06"
GREEN, YELLOW, RED = "#2E7D46", "#C9971C", "#B3261E"
BG, CARD = "#0E1A24", "#132029"

st.markdown(f"""
<style>
    .stApp {{ background-color: {BG}; color: #E8ECEF; }}
    section[data-testid="stSidebar"] {{ background-color: #0A141C; border-right: 1px solid {NAVY}; }}
    h1, h2, h3 {{ color: #E8ECEF !important; }}
    .kx-header {{
        background: linear-gradient(90deg, {BG} 0%, {NAVY} 100%);
        padding: 22px 26px; border-radius: 10px; margin-bottom: 18px;
        border-left: 4px solid {AMBER};
    }}
    .kx-header h1 {{ margin: 0; font-size: 25px; }}
    .kx-header p {{ margin: 4px 0 0 0; color: #9FB3C0; font-size: 14px; }}
    .kx-card {{
        background-color: {CARD}; border: 1px solid #223140; border-radius: 10px;
        padding: 16px 18px; margin-bottom: 12px;
    }}
    .kx-chip {{
        display: inline-block; padding: 3px 11px; border-radius: 12px;
        font-size: 12px; font-weight: 700; color: #0E1A24;
    }}
    .stTabs [data-baseweb="tab"] {{ color: #9FB3C0; }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# DATOS — Corporación Kallpa Industrial S.A.C. (caso ficticio)
# ══════════════════════════════════════════════════════════════════
# Cada sede tiene tres lecturas: 'actual', 'capex' (proyección si se aprueba
# el CAPEX priorizado) y 'estres' (escenario de estrés: solo cambia la sede
# afectada por el incidente, el resto queda igual que 'actual').

SEDES_INFO = {
    "Lima-Callao": {
        "sector": "Planta industrial y terminal logístico portuario",
        "riesgo_principal": "Sismo de gran magnitud + tsunami en franja costera",
        "aforo": 850,
    },
    "Trujillo": {
        "sector": "Planta agroindustrial y centro de distribución norte",
        "riesgo_principal": "Colapso estructural por lluvias intensas (El Niño costero)",
        "aforo": 420,
    },
    "Chiclayo": {
        "sector": "Centro de distribución regional",
        "riesgo_principal": "Inundación por desborde de canales y quebradas",
        "aforo": 260,
    },
    "Piura": {
        "sector": "Planta agroindustrial y almacenes",
        "riesgo_principal": "Inundación recurrente por lluvias intensas (El Niño costero)",
        "aforo": 310,
    },
    "Arequipa": {
        "sector": "Planta minero-metalúrgica",
        "riesgo_principal": "Sismo + actividad del complejo volcánico (caída de ceniza)",
        "aforo": 540,
    },
    "Cusco": {
        "sector": "Sede corporativa y operación turístico-hotelera",
        "riesgo_principal": "Sismo en zona altoandina + alta afluencia de visitantes",
        "aforo": 190,
    },
}

METRICAS = {
    "Lima-Callao":   {"actual": (7.5, 88, 91, 180, 260, "Automatización de alarma + refuerzo de vías de evacuación portuarias"),
                       "capex":  (5.0, 96, 98, 260, 260, "—"),
                       "estres": (7.5, 88, 91, 180, 260, "—")},
    "Trujillo":      {"actual": (9.5, 74, 68, 90,  210, "Renovación de red ACI y refuerzo estructural sismorresistente"),
                       "capex":  (6.0, 90, 92, 210, 210, "—"),
                       "estres": (9.5, 74, 68, 90,  210, "—")},
    "Chiclayo":      {"actual": (8.8, 82, 84, 70,  95,  "Renovación de bombas de achique y sistema de alerta temprana"),
                       "capex":  (6.5, 93, 94, 95,  95,  "—"),
                       "estres": (8.8, 82, 84, 70,  95,  "—")},
    "Piura":         {"actual": (10.5, 70, 65, 60,  175, "Automatización de alarma + elevación de red ACI ante inundación"),
                       "capex":  (6.5, 91, 92, 175, 175, "—"),
                       "estres": (19.0, 38, 30, 60,  175, "—")},
    "Arequipa":       {"actual": (6.8, 92, 90, 140, 150, "Sistema de detección de caída de ceniza en tomas de aire"),
                       "capex":  (5.5, 97, 96, 150, 150, "—"),
                       "estres": (6.8, 92, 90, 140, 150, "—")},
    "Cusco":         {"actual": (8.2, 85, 87, 60,  70,  "Señalización multilingüe y refuerzo de brigadas turísticas"),
                       "capex":  (6.0, 94, 95, 70,  70,  "—"),
                       "estres": (8.2, 85, 87, 60,  70,  "—")},
}

ESCENARIOS = {
    "Situación actual (línea base)": "actual",
    "Proyección con CAPEX priorizado aprobado": "capex",
    "Escenario de estrés — inundación en Piura": "estres",
}


def score_tiempo(min_):
    """Convierte minutos de respuesta a un puntaje 0-100 (objetivo: 5 min)."""
    return max(0, min(100, 100 - max(0, min_ - 5) * 10))


def build_dataframe(escenario_key):
    rows = []
    for sede, info in SEDES_INFO.items():
        tiempo, cobertura, infra, presup, capex_req, proyecto = METRICAS[sede][escenario_key]
        rows.append({
            "Sede": sede,
            "Sector": info["sector"],
            "Riesgo principal": info["riesgo_principal"],
            "Aforo": info["aforo"],
            "Tiempo de respuesta (min)": tiempo,
            "Cobertura de brigadas (%)": cobertura,
            "Operatividad de infraestructura (%)": infra,
            "Presupuesto asignado (S/ miles)": presup,
            "CAPEX requerido (S/ miles)": capex_req,
            "Proyecto de mitigación": proyecto,
            "Score tiempo": score_tiempo(tiempo),
        })
    return pd.DataFrame(rows)


def semaforo_metrica(valor, tipo):
    """tipo: 'tiempo' (menor mejor) o 'pct' (mayor mejor) -> color"""
    if tipo == "tiempo":
        if valor <= 8: return GREEN
        if valor <= 12: return YELLOW
        return RED
    else:
        if valor >= 90: return GREEN
        if valor >= 75: return YELLOW
        return RED


def semaforo_sede(row):
    """El estado de la sede es el peor (eslabón más débil) de sus 3 métricas."""
    colores = [
        semaforo_metrica(row["Tiempo de respuesta (min)"], "tiempo"),
        semaforo_metrica(row["Cobertura de brigadas (%)"], "pct"),
        semaforo_metrica(row["Operatividad de infraestructura (%)"], "pct"),
    ]
    if RED in colores: return "Crítico", RED
    if YELLOW in colores: return "Observado", YELLOW
    return "Adecuado", GREEN


# ══════════════════════════════════════════════════════════════════
# SIDEBAR — ESCENARIO Y PESOS DEL IGPC
# ══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### 🧭 Kallpa Industrial")
    st.caption("Dashboard educativo de mando integral")
    st.divider()

    escenario_label = st.radio("Escenario", list(ESCENARIOS.keys()))
    escenario_key = ESCENARIOS[escenario_label]

    st.divider()
    st.markdown("**Pesos del IGPC**")
    st.caption("Ajusta el peso de cada componente y observa cómo cambia el índice consolidado.")
    w_tiempo = st.slider("Tiempos de Respuesta", 0, 100, 40)
    w_cobertura = st.slider("Cobertura de Brigadas", 0, 100, 30)
    w_infra = st.slider("Operatividad de Infraestructura", 0, 100, 30)
    total_w = max(w_tiempo + w_cobertura + w_infra, 1)
    w1, w2, w3 = w_tiempo / total_w, w_cobertura / total_w, w_infra / total_w
    st.caption(f"Normalizados: Tiempos {w1:.0%} · Cobertura {w2:.0%} · Infraestructura {w3:.0%}")

    st.divider()
    ponderar_por_aforo = st.checkbox("Ponderar el IGPC corporativo por aforo de cada sede", value=True)

# ══════════════════════════════════════════════════════════════════
# DATOS DEL ESCENARIO SELECCIONADO
# ══════════════════════════════════════════════════════════════════

df = build_dataframe(escenario_key)
df["IGPC"] = (w1 * df["Score tiempo"] + w2 * df["Cobertura de brigadas (%)"] + w3 * df["Operatividad de infraestructura (%)"]).round(1)
df["Estado"], df["Color"] = zip(*df.apply(semaforo_sede, axis=1))
df["Brecha CAPEX (S/ miles)"] = df["CAPEX requerido (S/ miles)"] - df["Presupuesto asignado (S/ miles)"]
df["Índice de urgencia"] = (df["Brecha CAPEX (S/ miles)"] * (100 - df["IGPC"]) / 100).round(0)

if ponderar_por_aforo:
    igpc_corporativo = (df["IGPC"] * df["Aforo"]).sum() / df["Aforo"].sum()
else:
    igpc_corporativo = df["IGPC"].mean()

# ══════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════

st.markdown(f"""
<div class="kx-header">
  <h1>Mando Integral de Preparación ante Emergencias</h1>
  <p>Corporación Kallpa Industrial S.A.C. · 6 sedes en el Perú · {escenario_label}</p>
</div>
""", unsafe_allow_html=True)

with st.expander("📖 Glosario y guía de interpretación del tablero", expanded=False):
    st.markdown("""
**IGPC (Índice Global de Preparación Corporativa):** indicador ponderado de 0 a 100 que consolida tres
componentes operativos. No mide si hubo una emergencia, sino qué tan lista está la organización para
responder a una.

**Semáforo por sede:** el estado de cada sede lo determina su **peor** métrica, no el promedio — así como
una cadena se rompe por su eslabón más débil, una sede con excelente cobertura de brigadas pero
infraestructura desactualizada sigue siendo una sede crítica.

**Red ACI:** red de agua contra incendio (rociadores, gabinetes, bombas). Su "operatividad" mide qué
porcentaje de esos sistemas están realmente funcionales, no instalados.

**CAPEX de mitigación:** inversión de capital (no gasto operativo) destinada a reducir un riesgo
estructural o tecnológico específico — se justifica por la reducción de riesgo a la continuidad del
negocio, no por cumplimiento normativo aislado.

**Brecha presupuestal:** diferencia entre lo que la sede necesita invertir (CAPEX requerido) y lo que
tiene asignado. Una brecha grande en una sede con IGPC bajo es más urgente que la misma brecha en una
sede que ya está en verde.

**Preguntas para interpretar el tablero, no solo leerlo:**
- ¿Qué sede tiene el IGPC más bajo, y es por tiempos, cobertura o infraestructura?
- Si el IGPC corporativo se pondera por aforo, ¿qué sede tiene más influencia sobre el número final?
- ¿La sede con mayor brecha presupuestal es también la más urgente? ¿Por qué el índice de urgencia no es igual a la brecha?
""")

# ══════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════

tab1, tab2, tab3 = st.tabs([
    "1 · Índice Global de Preparación (IGPC)",
    "2 · Semáforo por Sedes",
    "3 · Brecha Presupuestal y CAPEX",
])

# ---------------------------------------------------------------
# TAB 1 — IGPC
# ---------------------------------------------------------------
with tab1:
    col1, col2 = st.columns([1, 2])

    with col1:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=igpc_corporativo,
            number={"suffix": " / 100", "font": {"color": "#E8ECEF", "size": 42}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#9FB3C0"},
                "bar": {"color": NAVY},
                "steps": [
                    {"range": [0, 60], "color": RED},
                    {"range": [60, 80], "color": YELLOW},
                    {"range": [80, 100], "color": GREEN},
                ],
                "threshold": {"line": {"color": "#E8ECEF", "width": 3}, "thickness": 0.8, "value": 80},
            },
        ))
        fig_gauge.update_layout(
            paper_bgcolor=BG, font_color="#E8ECEF", height=280,
            margin=dict(l=20, r=20, t=30, b=10),
            title=dict(text="IGPC Corporativo", font=dict(size=15, color="#9FB3C0")),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.caption(
            f"Ponderado por aforo · fórmula: IGPC = {w1:.0%}·Tiempos + {w2:.0%}·Cobertura + {w3:.0%}·Infraestructura"
            if ponderar_por_aforo else
            f"Promedio simple entre sedes · fórmula: IGPC = {w1:.0%}·Tiempos + {w2:.0%}·Cobertura + {w3:.0%}·Infraestructura"
        )

    with col2:
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=df["Sede"], y=df["Score tiempo"], name="Tiempos de respuesta",
            marker_color="#7FB3D5",
        ))
        fig_bar.add_trace(go.Bar(
            x=df["Sede"], y=df["Cobertura de brigadas (%)"], name="Cobertura de brigadas",
            marker_color=AMBER,
        ))
        fig_bar.add_trace(go.Bar(
            x=df["Sede"], y=df["Operatividad de infraestructura (%)"], name="Operatividad de infraestructura",
            marker_color="#1D6A6A",
        ))
        fig_bar.update_layout(
            barmode="group", plot_bgcolor=BG, paper_bgcolor=BG, font_color="#E8ECEF",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            margin=dict(l=10, r=10, t=40, b=10), height=280,
            yaxis_title="Puntaje (0-100)",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("##### IGPC por sede")
    tabla_igpc = df[["Sede", "IGPC", "Estado"]].sort_values("IGPC")
    st.dataframe(
        tabla_igpc, use_container_width=True, hide_index=True,
        column_config={"IGPC": st.column_config.ProgressColumn("IGPC", min_value=0, max_value=100, format="%.1f")},
    )

# ---------------------------------------------------------------
# TAB 2 — SEMÁFORO
# ---------------------------------------------------------------
with tab2:
    criticas = df[df["Estado"] == "Crítico"]["Sede"].tolist()
    if criticas:
        st.markdown(
            f'<div class="kx-card">🔴 <b>Sedes críticas este periodo:</b> {", ".join(criticas)}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="kx-card">🟢 Ninguna sede en estado crítico en este escenario.</div>', unsafe_allow_html=True)

    fig_sem = go.Figure(go.Bar(
        x=df.sort_values("IGPC")["IGPC"],
        y=df.sort_values("IGPC")["Sede"],
        orientation="h",
        marker_color=df.sort_values("IGPC")["Color"],
        text=df.sort_values("IGPC")["Estado"],
        textposition="outside",
    ))
    fig_sem.update_layout(
        plot_bgcolor=BG, paper_bgcolor=BG, font_color="#E8ECEF",
        xaxis_title="IGPC", margin=dict(l=10, r=60, t=20, b=10), height=320,
    )
    st.plotly_chart(fig_sem, use_container_width=True)

    st.markdown("##### Detalle por métrica")
    detalle = df[[
        "Sede", "Tiempo de respuesta (min)", "Cobertura de brigadas (%)",
        "Operatividad de infraestructura (%)", "Estado",
    ]].copy()

    def resaltar(row):
        c_t = semaforo_metrica(row["Tiempo de respuesta (min)"], "tiempo")
        c_c = semaforo_metrica(row["Cobertura de brigadas (%)"], "pct")
        c_i = semaforo_metrica(row["Operatividad de infraestructura (%)"], "pct")
        return [
            "", f"background-color:{c_t}55", f"background-color:{c_c}55",
            f"background-color:{c_i}55", "",
        ]

    st.dataframe(detalle.style.apply(resaltar, axis=1), use_container_width=True, hide_index=True)

    st.markdown("##### Ficha de sede")
    sede_sel = st.selectbox("Selecciona una sede para ver su ficha completa", df["Sede"].tolist())
    fila = df[df["Sede"] == sede_sel].iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("IGPC", f"{fila['IGPC']:.1f}", fila["Estado"])
    c2.metric("Tiempo de respuesta", f"{fila['Tiempo de respuesta (min)']:.1f} min")
    c3.metric("Aforo", f"{int(fila['Aforo'])} personas")
    st.markdown(f"**Sector:** {fila['Sector']}")
    st.markdown(f"**Riesgo principal:** {fila['Riesgo principal']}")

# ---------------------------------------------------------------
# TAB 3 — BRECHA PRESUPUESTAL Y CAPEX
# ---------------------------------------------------------------
with tab3:
    fig_capex = go.Figure()
    fig_capex.add_trace(go.Bar(
        x=df["Sede"], y=df["Presupuesto asignado (S/ miles)"], name="Presupuesto asignado",
        marker_color="#2E5266",
    ))
    fig_capex.add_trace(go.Bar(
        x=df["Sede"], y=df["CAPEX requerido (S/ miles)"], name="CAPEX requerido",
        marker_color=AMBER,
    ))
    fig_capex.update_layout(
        barmode="group", plot_bgcolor=BG, paper_bgcolor=BG, font_color="#E8ECEF",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=10, r=10, t=40, b=10), height=320,
        yaxis_title="S/ miles",
    )
    st.plotly_chart(fig_capex, use_container_width=True)

    st.markdown("##### Priorización de inversión")
    st.caption("El índice de urgencia combina la brecha presupuestal con el nivel de preparación: una brecha grande en una sede ya crítica pesa más que la misma brecha en una sede en verde.")
    prioridad = df[[
        "Sede", "Presupuesto asignado (S/ miles)", "CAPEX requerido (S/ miles)",
        "Brecha CAPEX (S/ miles)", "Índice de urgencia", "Proyecto de mitigación",
    ]].sort_values("Índice de urgencia", ascending=False)
    st.dataframe(
        prioridad, use_container_width=True, hide_index=True,
        column_config={
            "Índice de urgencia": st.column_config.ProgressColumn(
                "Índice de urgencia", min_value=0,
                max_value=max(1, int(prioridad["Índice de urgencia"].max())), format="%d",
            ),
        },
    )

    total_brecha = df["Brecha CAPEX (S/ miles)"].sum()
    total_asignado = df["Presupuesto asignado (S/ miles)"].sum()
    total_requerido = df["CAPEX requerido (S/ miles)"].sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("Presupuesto total asignado", f"S/ {total_asignado:,.0f} mil")
    c2.metric("CAPEX total requerido", f"S/ {total_requerido:,.0f} mil")
    c3.metric("Brecha total", f"S/ {total_brecha:,.0f} mil", delta=f"-{total_brecha:,.0f}" if total_brecha > 0 else "0", delta_color="inverse")

    if escenario_key != "capex":
        top_sede = prioridad.iloc[0]
        st.markdown(f"""
<div class="kx-card">
<b>Lectura sugerida:</b> en este escenario, <b>{top_sede['Sede']}</b> concentra el mayor índice de urgencia
—su brecha de S/ {top_sede['Brecha CAPEX (S/ miles)']:,.0f} mil pesa más porque su IGPC ya está por debajo
del umbral adecuado. El proyecto propuesto es: <i>{top_sede['Proyecto de mitigación']}</i>.
Cambia al escenario "Proyección con CAPEX priorizado aprobado" en la barra lateral para ver cómo se
mueve el IGPC de esa sede si se aprueba la inversión.
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div class="kx-card">
<b>Lectura sugerida:</b> con el CAPEX priorizado aprobado, la brecha se cierra en todas las sedes y el
IGPC corporativo sube de forma consistente. Compara este número con el de "Situación actual" para
cuantificar el retorno del programa de inversión en términos de preparación, no solo de cumplimiento.
</div>
""", unsafe_allow_html=True)
