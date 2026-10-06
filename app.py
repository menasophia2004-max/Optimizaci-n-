import streamlit as st
import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint

# Configuración de la página
st.set_page_config(page_title="Optimización de Publicidad", layout="wide")

st.title("🎯 Optimización de Presupuesto Publicitario")
st.write("""
Esta aplicación te permite ajustar los costos, beneficios y el presupuesto total 
para encontrar la combinación óptima de medios utilizando programación lineal entera mixta (MILP).
""")

# Barra lateral para el presupuesto
st.sidebar.header("⚙️ Configuración Global")
presupuesto = st.sidebar.number_input("Presupuesto Total Disponible (Millones)", min_value=1.0, max_value=100.0, value=9.0, step=0.5)

# Datos iniciales por defecto
medios = ["Televisión (TV)", "Radio (R)", "Redes Sociales (RS)", "Prensa (P)"]
costos_defecto = [8.0, 3.0, 4.0, 2.0]
beneficios_defecto = [14.0, 5.0, 7.0, 3.0]

st.header("📈 Parámetros de los Medios")

# Crear columnas para ingresar valores interactivamente
columnas = st.columns(4)
costos = []
beneficios = []

for i, medio in enumerate(medios):
    with columnas[i]:
        st.subheader(medio)
        costo = st.number_input(f"Costo ({medio})", min_value=0.0, value=costos_defecto[i], key=f"costo_{i}")
        beneficio = st.number_input(f"Beneficio ({medio})", min_value=0.0, value=beneficios_defecto[i], key=f"benef_{i}")
        costos.append(costo)
        beneficios.append(beneficio)

# Botón para ejecutar la optimización
if st.button("🚀 Ejecutar Optimización", type="primary"):
    
    # Coeficientes para milp (minimizamos -beneficios para maximizar)
    c = -np.array(beneficios)
    
    # Restricción de presupuesto: A * x <= presupuesto
    A = np.array([costos])
    ub = np.array([presupuesto])
    lb = np.array([-np.inf])
    restriccion_presupuesto = LinearConstraint(A, lb, ub)
    
    # Cotas binarias (0 <= x <= 1)
    bounds = Bounds(np.zeros(4), np.ones(4))
    
    # Variables enteras
    integrality = np.ones(4)
    
    # Resolver
    res = milp(c=c, constraints=restriccion_presupuesto, bounds=bounds, integrality=integrality)
    
    if res.success:
        valores = np.round(res.x).astype(int)
        
        st.success("¡Optimización completada con éxito!")
        
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.subheader("📢 Plan de Contratación Sugerido")
            for i, medio in enumerate(medios):
                estado = "✅ Contratar" if valores[i] == 1 else "❌ No contratar"
                st.write(f"**{medio}**: {estado}")
                
        with col_res2:
            st.subheader("📊 Resumen Métrico")
            costo_total = sum(valores[i] * costos[i] for i in range(4))
            utilidad_total = sum(valores[i] * beneficios[i] for i in range(4))
            
            st.metric(label="Utilidad Total Maximizada", value=f"{utilidad_total} pts")
            st.metric(label="Presupuesto Utilizado", value=f"{costo_total}M", delta=f"{presupuesto - costo_total:.1f}M restantes")
            
    else:
        st.error(f"No se pudo encontrar una solución óptima viable: {res.message}")
