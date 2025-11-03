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

# UI en Streamlit
st.title("🎙️ Convertidor de Audio a Texto con Análisis de Conformidad")

st.markdown("""
### Instrucciones:
1. Sube un archivo de audio (MP3, WAV, M4A, etc.)
2. El sistema transcribirá el audio a texto
3. Analizará el nivel de conformidad del cliente
4. Podrás copiar el texto resultante
""")

# Función para analizar conformidad
def analizar_conformidad(texto):
    """Analiza el nivel de conformidad del comentario usando OpenAI"""
    
    prompt = f"""
    Analiza el siguiente comentario de un cliente sobre un servicio bancario y determina el porcentaje de conformidad (0-100%).
    Considera: satisfacción, quejas, elogios, problemas mencionados y tono general.

    Comentario: "{texto}"

    Responde SOLO con el porcentaje numérico sin símbolo % y una breve explicación de una línea separada por "|".
    Ejemplo: "85|El cliente expresa satisfacción general pero con una sugerencia menor"
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un analista de experiencia del cliente especializado en servicios bancarios."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.3
        )
        
        resultado = response.choices[0].message.content.strip()
        if "|" in resultado:
            porcentaje, explicacion = resultado.split("|", 1)
            return int(porcentaje), explicacion
        else:
            return 50, "No se pudo determinar claramente la conformidad"
            
    except Exception as e:
        st.error(f"Error en el análisis: {str(e)}")
        return 50, "Error en el análisis"

# Función para determinar color según conformidad
def obtener_color_conformidad(porcentaje):
    if porcentaje >= 80:
        return "🟢"  # Verde - Alta conformidad
    elif porcentaje >= 60:
        return "🟡"  # Amarillo - Conformidad media
    else:
        return "🔴"  # Rojo - Baja conformidad

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

# Botón para transcribir audio
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
                
                # Analizar conformidad
                porcentaje, explicacion = analizar_conformidad(transcription)
                
                # Limpiar archivo temporal
                os.remove(temp_audio_path)
            
            # Mostrar resultados
            st.success("✅ Transcripción y análisis completados!")
            
            # Mostrar métrica de conformidad
            color = obtener_color_conformidad(porcentaje)
            st.subheader(f"{color} Nivel de Conformidad: {porcentaje}%")
            
            # Barra de progreso visual
            st.progress(porcentaje / 100)
            
            # Explicación del análisis
            st.info(f"**Análisis:** {explicacion}")
            
            # Área de texto para mostrar y copiar el resultado
            st.subheader("📝 Texto Transcrito:")
            st.text_area(
                "Texto extraído del audio:",
                value=transcription,
                height=200,
                key="transcription_output"
            )
            
            # Botón para copiar al portapapeles
            if st.button("📋 Copiar Texto"):
                st.code(transcription, language="text")
                st.success("Texto copiado al portapapeles!")
            
            # Estadísticas
            st.subheader("📊 Estadísticas:")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Caracteres", len(transcription))
            with col2:
                st.metric("Palabras", len(transcription.split()))
            with col3:
                st.metric("Conformidad", f"{porcentaje}%")
            with col4:
                st.metric("Nivel", color)
                
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
    | "La atención en ventanilla fue rápida y el personal muy amable." | 100% |
    | "El cajero automático no funcionaba y no había personal de apoyo." | 65% |
    | "Pude abrir mi cuenta digital sin problemas, todo el proceso fue claro." | 98% |
    | "Mi solicitud de crédito se demoró más de una semana sin explicación." | 70% |
    | "El asesor me explicó muy bien las condiciones del préstamo, excelente servicio." | 95% |
    | "El sistema del aplicativo móvil se cae constantemente." | 68% |
    | "Me resolvieron mi reclamo en menos de 24 horas, estoy satisfecho." | 92% |
    | "No me informaron correctamente los costos de mantenimiento de cuenta." | 72% |
    """)

# Información adicional
with st.expander("ℹ️ Información sobre el Análisis de Conformidad"):
    st.markdown("""
    **Escala de Conformidad:**
    
    🟢 **80-100%: Alta Conformidad**
    - Clientes satisfechos y leales
    - Comentarios positivos predominantes
    - Probable recomendación a otros
    
    🟡 **60-79%: Conformidad Media** 
    - Clientes con experiencias mixtas
    - Algunos aspectos positivos, otros a mejorar
    - Riesgo de pérdida si no se mejoran puntos débiles
    
    🔴 **0-59%: Baja Conformidad**
    - Clientes insatisfechos
    - Problemas significativos en el servicio
    - Alto riesgo de abandono
    
    **Factores considerados en el análisis:**
    - Tono del comentario (positivo/negativo/neutral)
    - Problemas específicos mencionados
    - Soluciones o aspectos positivos destacados
    - Emociones expresadas
    - Expectativas cumplidas o no cumplidas
    """)

# Pie de página
st.markdown("---")
st.caption("Powered by OpenAI Whisper & GPT APIs | Análisis de Experiencia del Cliente")