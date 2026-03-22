FROM python:3.13-slim
WORKDIR /app
RUN pip install --no-cache-dir streamlit
COPY demo.py board.json ./
COPY results/ results/
COPY luthien_policies/ luthien_policies/
EXPOSE 8501
CMD ["streamlit", "run", "demo.py", "--server.headless", "true", "--server.port", "8501", "--server.address", "0.0.0.0"]
