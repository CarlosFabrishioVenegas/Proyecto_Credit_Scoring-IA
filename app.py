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
st.title("🎙️ Convertidor de Audio a Texto con OpenAI")

st.markdown("""
### Instrucciones:
1. Sube un archivo de audio (MP3, WAV, M4A, etc.)
2. El sistema transcribirá el audio a texto
3. Podrás copiar el texto resultante
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

# Botón para transcribir audio
if st.button("🎯 Transcribir Audio a Texto"):
    if uploaded_file is not None:
        try:
            with st.spinner("🔄 Procesando audio... Esto puede tomar unos segundos"):
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
                        language="es"  # Opcional: especificar idioma
                    )
                
                # Limpiar archivo temporal
                os.remove(temp_audio_path)
            
            # Mostrar resultados
            st.success("✅ Transcripción completada!")
            
            # Área de texto para mostrar y copiar el resultado
            st.subheader("📝 Texto Transcrito:")
            st.text_area(
                "Texto extraído del audio:",
                value=transcription,
                height=300,
                key="transcription_output"
            )
            
            # Botón para copiar al portapapeles
            if st.button("📋 Copiar Texto"):
                st.code(transcription, language="text")
                st.success("Texto copiado al portapapeles!")
            
            # Estadísticas
            st.subheader("📊 Estadísticas:")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Caracteres", len(transcription))
            with col2:
                st.metric("Palabras", len(transcription.split()))
            with col3:
                st.metric("Líneas", len(transcription.split('\n')))
                
        except Exception as e:
            st.error(f"❌ Error al procesar el audio: {str(e)}")
            st.info("💡 Asegúrate de que el archivo de audio sea válido y no esté corrupto.")
    
    else:
        st.warning("⚠️ Por favor, sube un archivo de audio primero.")

# Información adicional
with st.expander("ℹ️ Información sobre la transcripción"):
    st.markdown("""
    **Características:**
    - ✅ Soporta múltiples formatos de audio
    - ✅ Reconocimiento automático de idioma
    - ✅ Alta precisión en la transcripción
    - ✅ Procesamiento rápido
    
    **Formatos soportados:** MP3, MP4, WAV, M4A, WEBM, etc.
    
    **Límites:** 
    - Archivos hasta 25 MB
    - Máximo 10 minutos de audio
    """)

# Pie de página
st.markdown("---")
st.caption("Powered by OpenAI Whisper API")