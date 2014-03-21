from flask import Flask, request
import redis
from models.blacklist_cache import BlacklistCache
from models.caching_steps import StepsCache

app = Flask(__name__)
app.config.from_object('settings')

def get_redis_client():
    return redis.StrictRedis(host='localhost', port=6379, db=0)

@app.route("/router")
def outgoing_message_router():
    return "Hello, World!"

@app.route("/update_script_steps")
def update_script_steps():
    client = get_redis_client()
    steps_cache = StepsCache(client,
                             app.config["REGISTRATION_STEPS_API_USERNAME"],
                             app.config["REGISTRATION_STEPS_API_PASSWORD"],
                             app.config["REGISTRATION_STEPS_API_URL"])
    steps_cache.delete_script_steps_data()
    steps_cache.add_script_steps_data()
    return "Steps script in cache successfully updated"

@app.route("/add_to_blacklist", methods=['POST'])
def add_to_blacklist():
    "curl -i -X POST -d 'text=example_text' http://127.0.0.1:5000/add_to_blacklist"
    if request.form['text']:
        client = get_redis_client()
        blacklist_cache = BlacklistCache(client)
        blacklist_cache.add_to_blacklist(request.form['text'])
        return "Successfully added to blacklist"
    else:
        return "None text found"

if __name__ == "__main__":
    app.run()
