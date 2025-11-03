# 🧠 IA Generativa LLM – Proyecto “Terrenitos”

## 📌 Descripción  
Proyecto que aplica **IA Generativa** y **modelos LLM** para analizar conversaciones del call center y **predecir el grado de conformidad del cliente**, combinando datos estructurados (pagos, facturación) y no estructurados (llamadas).

## 🎯 Objetivo  
Identificar clientes en riesgo de abandono y recomendar **estrategias de retención personalizadas**, diferenciadas en:
- 💰 **Beneficios económicos**
- 🎁 **Beneficios adicionales**

## ⚙️ Solución  
Se utiliza un modelo **OpenAI LLM** con **embeddings en Python** para evaluar el tono y la conformidad en las conversaciones.  
Los resultados se integran con la información de pagos y facturación para generar una **Matriz de Priorización de Clientes** que guía las acciones del equipo de retención.

## 🧩 Flujo General
```plaintext
CRM (llamadas) + ERP (pagos)
        ↓
Embeddings OpenAI → Grado de conformidad
        ↓
Matriz de priorización de clientes
```

🚀 Impacto

🔍 Mejora la comprensión del cliente.

🧠 Automatiza el análisis de satisfacción.

📈 Optimiza la retención y decisiones estratégicas.
