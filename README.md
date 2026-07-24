# Mando Integral de Preparación ante Emergencias — Kallpa Industrial S.A.C.

Dashboard educativo en Streamlit para identificar e interpretar los elementos de un tablero de
gestión de crisis y emergencias, sobre un caso ficticio pero realista: una corporación peruana con
6 sedes en distintas regiones del país, cada una con un perfil de riesgo propio.

## Qué hace

- **Índice Global de Preparación Corporativa (IGPC):** indicador ponderado (0–100) que consolida
  Tiempos de Respuesta, Cobertura de Brigadas y Operatividad de Infraestructura. Los pesos son
  ajustables con sliders en la barra lateral, para que el usuario vea cómo cambia el índice según
  qué componente se priorice.
- **Semáforo de desempeño por sede:** clasifica cada sede en Adecuado / Observado / Crítico según
  su métrica más débil (no el promedio), con detalle por métrica y ficha individual por sede.
- **Brecha presupuestal y CAPEX de mitigación:** compara presupuesto asignado vs. CAPEX requerido
  por sede, con un proyecto de mitigación específico (automatización de alarma, renovación de red
  ACI, etc.) y un índice de urgencia que combina la brecha con el nivel de preparación.
- **Tres escenarios** en la barra lateral: situación actual, proyección con CAPEX aprobado (mejora
  todas las sedes) y un escenario de estrés — inundación en Piura (degrada solo esa sede), para
  observar cómo un incidente localizado afecta al índice corporativo.
- **Glosario y guía de interpretación** en un panel expandible, con preguntas orientadoras para
  discusión en clase.

## Cómo correrlo en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Cómo desplegarlo (Streamlit Community Cloud)

1. Sube esta carpeta a un repositorio de GitHub.
2. En [share.streamlit.io](https://share.streamlit.io), conecta el repositorio y selecciona
   `app.py` como archivo principal.
3. No requiere secretos ni base de datos: todos los datos del caso están embebidos en `app.py`
   (diccionarios `SEDES_INFO` y `METRICAS`).

## Personalizar el caso

- Para cambiar sedes, riesgos o cifras: edita los diccionarios `SEDES_INFO` y `METRICAS` al inicio
  de `app.py`. Cada sede tiene tres tuplas de datos (`actual`, `capex`, `estres`).
- Los umbrales del semáforo están en `semaforo_metrica()`.
- La fórmula del IGPC y su normalización de tiempos están en `score_tiempo()` y en el cálculo de
  `df["IGPC"]`.
