import multiprocessing
from core.app import App

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")
    App().start()
