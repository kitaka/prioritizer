from flask import Flask
from models.caching_steps import StepsCache

app = Flask(__name__)
app.config.from_object('settings')


@app.route("/router")
def outgoing_message_router():
    return "Hello, World!"


@app.route("/update_script_steps")
def update_script_steps():
    steps_cache = StepsCache(app.config["REGISTRATION_STEPS_API_USERNAME"],
                             app.config["REGISTRATION_STEPS_API_PASSWORD"],
                             app.config["REGISTRATION_STEPS_API_URL"])
    client = steps_cache.get_redis_client()
    steps_cache.delete_script_steps_data(client)
    steps_cache.add_script_steps_data(client)
    return "Steps script in cache successfully updated"


if __name__ == "__main__":
    app.run()
