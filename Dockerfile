# Create virtual environment
RUN python -m venv /opt/venv

# Use the virtual environment's pip directly
RUN /opt/venv/bin/pip install --upgrade pip
RUN /opt/venv/bin/pip install -r requirements.txt

# Ensure path is set for runtime
ENV PATH="/opt/venv/bin:$PATH"

CMD ["python", "bot.py"]
