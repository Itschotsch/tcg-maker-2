from argparse import ArgumentParser
from dotenv import load_dotenv
import logging
import os

from web import web_server

logger = logging.getLogger(__name__)

def main():
    load_dotenv()
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=log_level)

    parser = ArgumentParser()
    parser.add_argument("--port", type=int, help="Port to run the web server on")
    parser.add_argument("--host", type=str, help="Host to run the web server on")
    parser.add_argument("--reload", action="store_true", help="Enable hot reloading")
    args = parser.parse_args()

    # Default values
    host: str = "0.0.0.0"
    port: int = 8000

    # Values set in .env
    if os.getenv("HOST"):
        host = os.getenv("HOST")
    if os.getenv("PORT"):
        port = int(os.getenv("PORT"))
    
    # Values passed as arguments
    if args.host:
        host = args.host
    if args.port:
        port = args.port

    web_server.run(host=host, port=port, reload=args.reload)

if __name__ == "__main__":
    main()
