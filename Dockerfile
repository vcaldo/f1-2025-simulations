# Usa imagem oficial Python slim
FROM python:3.12-slim

# Define diretório de trabalho
WORKDIR /app

# Copia requirements e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código e assets
COPY app.py .
COPY f1_simulator.py .
COPY cenarios_empate.csv .
COPY assets/ ./assets/
COPY .streamlit/ ./.streamlit/

# Expõe porta do Streamlit
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando para iniciar o Streamlit
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
