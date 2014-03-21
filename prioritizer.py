from flask import Flask, request
import redis
from models.blacklist_cache import BlacklistCache
from models.caching_steps import StepsCache
from models.priority import Priority
from models.registration_message_filter import RegistrationMessageFilter

app = Flask(__name__)
app.config.from_object('settings')

app.config["DEBUG"] = True

def get_redis_client():
    return redis.StrictRedis(host='localhost', port=6379, db=0)


def get_steps_cache_instance():
    steps_cache = StepsCache(get_redis_client(),
                             app.config["REGISTRATION_STEPS_API_USERNAME"],
                             app.config["REGISTRATION_STEPS_API_PASSWORD"],
                             app.config["REGISTRATION_STEPS_API_URL"],
                             app.config["STEPS_CACHE_KEY_NAME"])
    return steps_cache


@app.route("/router", methods=['GET'])
def outgoing_message_router():
    message_filter = RegistrationMessageFilter(get_steps_cache_instance(),
                                               request.args.get('text', None))
    if message_filter.prioritize() == Priority.HIGH:
        return "High Priority"
    else:
        return "Low Priority"


@app.route("/update_script_steps")
def update_script_steps():
    steps_cache = get_steps_cache_instance()
    steps_cache.delete_script_steps_data()
    steps_cache.add_script_steps_data()
    return "Steps script in cache successfully updated"


@app.route("/add_to_blacklist", methods=['POST'])
def add_to_blacklist():
    "curl -i -X POST -d 'text=example_text' http://127.0.0.1:5000/add_to_blacklist"
    if request.form['text']:
        client = get_redis_client()
        blacklist_cache = BlacklistCache(client, app.config["BLACKLIST_CACHE_KEY_NAME"])
        blacklist_cache.add_to_blacklist(request.form['text'])
        return "Successfully added to blacklist"
    else:
        return "None text found"

if __name__ == "__main__":
    app.run()
