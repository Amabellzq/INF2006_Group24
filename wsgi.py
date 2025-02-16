import logging

from webapp import create_app

app = create_app()
# ✅ Enable Debug Level Logging
logging.basicConfig(
    level=logging.DEBUG,  # Log everything (DEBUG, INFO, WARNING, ERROR)
    format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),  # Logs to console
        logging.FileHandler("flask_app.log")  # Logs to file
    ]
)

app.logger.info("✅ Flask app started with DEBUG logging.")
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)