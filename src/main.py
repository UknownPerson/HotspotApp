from logging_setup import setup_logging


if __name__ == "__main__":
    setup_logging()
    from ui import run

    run()
