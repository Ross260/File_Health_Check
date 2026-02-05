# Image légère de Python
FROM python:3.13-slim

# Répertoire de travail
WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code
COPY . .

# Port exposé (Streamlit utilise 8501 par défaut)
EXPOSE 8501

# Commande de lancement
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]