from flask import Flask
from models.caching_steps import StepsCache

app = Flask(__name__)


@app.route("/router")
def outgoing_message_router():
    steps_cache = StepsCache()
    return "Hello, World!"


if __name__ == "__main__":

    app.run()
