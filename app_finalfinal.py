import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Cargar variables de entorno
load_dotenv()

# Obtener API Key de forma segura
apiKey = os.environ.get('OPENAI_API_KEY')

# Verificación de la API Key
if not apiKey:
    st.error("""
    ❌ No se encontró OPENAI_API_KEY. Por favor:
    1. Crea un archivo .env con OPENAI_API_KEY=tu_key_real
    2. O usa los secrets de Streamlit
    """)
    st.stop()

st.write("🔐 API Key cargada:", apiKey is not None)
client = OpenAI(api_key=apiKey)

# Base de conocimiento para análisis de conformidad
CONFORMITY_CRITERIA = {
    "positivo": [
        "satisfecho", "contento", "feliz", "excelente", "bueno", "rápido", "fácil", 
        "útil", "eficiente", "amable", "atento", "resolvió", "solución", "recomiendo",
        "competitivo", "instantáneo", "claro", "sin problemas", "siempre", "me encanta"
    ],
    "negativo": [
        "pésimo", "malo", "lento", "difícil", "inútil", "ineficiente", "grosero",
        "nunca", "problema", "reclamo", "queja", "error", "falla", "no funciona",
        "demora", "espera", "confuso", "complicado", "alto costo", "caro", "tasa alta"
    ]
}

def analizar_conformidad(texto):
    """Analiza el nivel de conformidad del texto usando OpenAI"""
    try:
        prompt = f"""
        Analiza el siguiente comentario de un cliente bancario y determina el porcentaje de conformidad (0% a 100%).
        Considera el tono, sentimiento y contenido específico del mensaje.
        
        Comentario: "{texto}"
        
        Basado en esta escala de referencia:
        - 0-20%: Muy insatisfecho (quejas graves, maltrato, problemas no resueltos)
        - 21-40%: Insatisfecho (múltiples problemas, mala atención)
        - 41-60%: Neutral (críticas mixtas, algunos aspectos buenos y malos)
        - 61-80%: Satisfecho (buena experiencia con algunas áreas de mejora)
        - 81-100%: Muy satisfecho (excelente servicio, recomendación)
        
        Responde SOLO con el número del porcentaje sin explicaciones.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un analista de experiencia del cliente especializado en servicios bancarios."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.1
        )
        
        porcentaje = response.choices[0].message.content.strip().replace('%', '')
        return int(porcentaje)
    
    except Exception as e:
        st.error(f"Error en el análisis: {e}")
        return None

def obtener_color_conformidad(porcentaje):
    """Devuelve el color según el nivel de conformidad"""
    if porcentaje >= 80:
        return "🟢"  # Verde
    elif porcentaje >= 60:
        return "🟡"  # Amarillo
    elif porcentaje >= 40:
        return "🟠"  # Naranja
    else:
        return "🔴"  # Rojo

def obtener_categoria_conformidad(porcentaje):
    """Devuelve la categoría según el porcentaje"""
    if porcentaje >= 90:
        return "Excelente"
    elif porcentaje >= 75:
        return "Muy Bueno"
    elif porcentaje >= 60:
        return "Bueno"
    elif porcentaje >= 40:
        return "Regular"
    elif porcentaje >= 20:
        return "Malo"
    else:
        return "Muy Malo"

# UI en Streamlit
st.title("🎙️ Convertidor de Audio a Texto con Análisis de Conformidad")

st.markdown("""
### Instrucciones:
1. Sube un archivo de audio (MP3, WAV, M4A, etc.)
2. El sistema transcribirá el audio a texto
3. Analizará el nivel de conformidad del cliente
4. Podrás ver el resultado con métricas detalladas
""")

# Widget para subir archivo de audio
uploaded_file = st.file_uploader(
    "Sube tu archivo de audio:",
    type=['mp3', 'wav', 'm4a', 'mp4', 'mpeg', 'mpga', 'webm'],
    help="Formatos soportados: MP3, WAV, M4A, MP4, etc."
)

# Mostrar información del archivo subido
if uploaded_file is not None:
    st.audio(uploaded_file, format=f"audio/{uploaded_file.type.split('/')[-1]}")
    st.write(f"📁 **Archivo:** {uploaded_file.name}")
    st.write(f"📊 **Tamaño:** {uploaded_file.size / 1024:.2f} KB")

def obtener_interpretacion_conformidad(porcentaje):
    """Devuelve una interpretación del nivel de conformidad"""
    if porcentaje >= 90:
        return "Cliente muy satisfecho, probable promotor del servicio"
    elif porcentaje >= 75:
        return "Cliente satisfecho con experiencia positiva"
    elif porcentaje >= 60:
        return "Cliente generalmente satisfecho con algunas áreas de mejora"
    elif porcentaje >= 40:
        return "Experiencia neutral, cliente indiferente o con críticas mixtas"
    elif porcentaje >= 20:
        return "Cliente insatisfecho con problemas significativos"
    else:
        return "Cliente muy insatisfecho, riesgo de abandono"
    
# Botón para transcribir audio y analizar conformidad
if st.button("🎯 Transcribir y Analizar Conformidad"):
    if uploaded_file is not None:
        try:
            with st.spinner("🔄 Procesando audio y analizando conformidad..."):
                # Guardar archivo temporalmente
                temp_audio_path = f"temp_audio.{uploaded_file.type.split('/')[-1]}"
                with open(temp_audio_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Transcribir audio usando Whisper
                with open(temp_audio_path, "rb") as audio_file:
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text",
                        language="es"  # Especificar idioma español
                    )
                
                # Limpiar archivo temporal
                os.remove(temp_audio_path)
                
                # Analizar conformidad
                conformidad = analizar_conformidad(transcription)
            
            # Mostrar resultados
            st.success("✅ Transcripción y análisis completados!")
            
            # Sección de transcripción
            st.subheader("📝 Texto Transcrito:")
            st.text_area(
                "Texto extraído del audio:",
                value=transcription,
                height=200,
                key="transcription_output"
            )
            
            # Sección de análisis de conformidad
            st.subheader("📊 Análisis de Conformidad")
            
            if conformidad is not None:
                color = obtener_color_conformidad(conformidad)
                categoria = obtener_categoria_conformidad(conformidad)
                
                # Métricas principales
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Nivel de Conformidad", 
                        f"{conformidad}%",
                        delta=f"{categoria}",
                        delta_color="normal" if conformidad >= 60 else "inverse"
                    )
                with col2:
                    st.metric("Caracteres", len(transcription))
                with col3:
                    st.metric("Palabras", len(transcription.split()))
                
                # Barra de progreso visual
                st.progress(conformidad / 100)
                st.write(f"{color} **Categoría:** {categoria}")
                
                # Interpretación del resultado
                st.info(f"**Interpretación:** {obtener_interpretacion_conformidad(conformidad)}")
                
            else:
                st.warning("No se pudo analizar la conformidad del texto.")
            
            # Botón para copiar al portapapeles
            if st.button("📋 Copiar Texto Transcrito"):
                st.code(transcription, language="text")
                st.success("Texto copiado al portapapeles!")
                
        except Exception as e:
            st.error(f"❌ Error al procesar el audio: {str(e)}")
            st.info("💡 Asegúrate de que el archivo de audio sea válido y no esté corrupto.")
    
    else:
        st.warning("⚠️ Por favor, sube un archivo de audio primero.")


# Ejemplos de referencia
with st.expander("📋 Ejemplos de Referencia de Conformidad"):
    st.markdown("""
    | Comentario | % Conformidad |
    |-----------|---------------|
    | "Nunca recibí respuesta a mi reclamo, pésima atención." | 0% |
    | "Me cobraron comisiones sin previo aviso." | 10% |
    | "El personal fue grosero y no resolvió mi problema." | 15% |
    | "Esperé más de una hora y no me atendieron." | 20% |
    | "El cajero automático estaba fuera de servicio." | 30% |
    | "Me transfirieron varias veces sin darme solución." | 40% |
    | "El sistema del aplicativo se cae constantemente." | 50% |
    | "No me informaron correctamente los costos." | 55% |
    | "El trato fue poco cordial, deberían mejorar." | 60% |
    | "Mi solicitud se demoró sin explicación." | 65% |
    | "Algunos procesos son confusos, pero completé mi trámite." | 70% |
    | "Atención buena, aunque el tiempo de espera fue largo." | 75% |
    | "El asesor me explicó muy bien las condiciones." | 80% |
    | "Me resolvieron mi reclamo en menos de 24 horas." | 85% |
    | "Siempre encuentro disponibilidad de atención." | 88% |
    | "Me ofrecieron solución rápida cuando extravié mi tarjeta." | 90% |
    | "Tasas competitivas y asesores atentos." | 92% |
    | "El aplicativo es fácil de usar y transferencias instantáneas." | 95% |
    | "Abrir mi cuenta digital fue claro y sin problemas." | 98% |
    | "Atención rápida y personal muy amable." | 100% |
    """)

# Información adicional
with st.expander("ℹ️ Información sobre el Análisis"):
    st.markdown("""
    **Cómo funciona el análisis:**
    - 🤖 Usa GPT para analizar el sentimiento y contenido
    - 🎯 Especializado en servicios bancarios
    - 📊 Escala de 0% a 100% basada en experiencia del cliente
    - ⚡ Procesamiento en tiempo real
    
    **Interpretación de resultados:**
    - 🟢 81-100%: Cliente promotor (excelente experiencia)
    - 🟡 61-80%: Cliente satisfecho (buena experiencia)
    - 🟠 41-60%: Cliente neutral (experiencia mixta)
    - 🔴 0-40%: Cliente detractores (mala experiencia)
    """)

# Pie de página
st.markdown("---")
st.caption("Powered by OpenAI Whisper & GPT APIs | Análisis de Experiencia del Cliente")