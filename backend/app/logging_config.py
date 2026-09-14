import logging
import sys
import os

def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(f"{log_dir}/pipeline.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

setup_logging()
