import streamlit as st
from openai import OpenAI  # Importación cambiada
import pandas as pd
from PyPDF2 import PdfReader
import os

# Configuración inicial - REEMPLAZA CON TU API KEY
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
 # Sintaxis nueva

# 1. Validación de estudiantes
def validar_estudiante(codigo):
    try:
        if not os.path.exists("estudiantes.xlsx"):
            st.error("❌ Archivo 'estudiantes.xlsx' no encontrado")
            return False
        
        df = pd.read_excel("estudiantes.xlsx")
        
        if 'codigo' not in df.columns:
            st.error("❌ Columna 'codigo' no encontrada en el Excel")
            return False
        
        codigos = df['codigo'].astype(str).values
        return codigo in codigos
    
    except Exception as e:
        st.error(f"❌ Error en validación: {str(e)}")
        return False

# 2. Procesar PDFs
def cargar_documentos():
    textos = []
    try:
        for archivo in os.listdir():
            if archivo.endswith(".pdf"):
                try:
                    with open(archivo, "rb") as f:
                        lector = PdfReader(f)
                        texto = ""
                        for pagina in lector.pages:
                            texto_pagina = pagina.extract_text()
                            if texto_pagina:
                                texto += texto_pagina + "\n"
                        textos.append(texto[:5000])
                except Exception as e:
                    st.error(f"❌ Error al leer {archivo}: {str(e)}")
        return "\n\n".join(textos)
    except Exception as e:
        st.error(f"❌ Error general al cargar documentos: {str(e)}")
        return ""

# 3. Función principal
def main():
    st.title("📚 Asistente Académico")
    
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
        st.session_state.knowledge = ""
    
    if not st.session_state.autenticado:
        codigo = st.text_input("Ingresa tu código de estudiante:", type="password")
        if st.button("Validar"):
            if validar_estudiante(codigo):
                st.session_state.autenticado = True
                st.session_state.knowledge = cargar_documentos()
            else:
                st.error("❌ Código inválido. Intenta nuevamente.")
        return

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = [{"role": "assistant", "content": "¡Hola! Soy tu asistente académico. ¿En qué puedo ayudarte?"}]

    for mensaje in st.session_state.mensajes:
        with st.chat_message(mensaje["role"]):
            st.markdown(mensaje["content"])

    if prompt := st.chat_input("Escribe tu pregunta:"):
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.spinner("Pensando..."):
            contexto = f"Documentos de referencia:\n{st.session_state.knowledge}\n\nPregunta: {prompt}"
            
            try:
                # SINTAXIS NUEVA DE OPENAI
                respuesta = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Eres un asistente universitario especializado en Sistemas de Información."},
                        {"role": "user", "content": contexto}
                    ],
                    temperature=0.7
                )
                respuesta_ia = respuesta.choices[0].message.content  # Acceso cambiado
            except Exception as e:
                respuesta_ia = f"⚠️ Error al conectar con OpenAI: {str(e)}"
        
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
        with st.chat_message("assistant"):
            st.markdown(respuesta_ia)

if __name__ == "__main__":
    main()
