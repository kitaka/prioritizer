import re
import requests


def get_smsc_details(text, smsc_name):
    regex = "%s.*sent ([0-9]*)," % smsc_name
    return re.compile(regex).search(text).groups()[0]


def get_smsc_sent_values():
    kannel_status_page_url = "http://2.2.2.2:13000/status?password=mshaikh"
    response = requests.get(kannel_status_page_url)

    return get_smsc_details(response.text, "hi_smsc"), get_smsc_details(response.text, "lo_smsc")


def assert_url_priority(url, priority):
    initial_high, initial_low = get_smsc_sent_values()
    requests.get(url)
    current_high, current_low = get_smsc_sent_values()

    if priority == "high":
        assert int(current_high) > int(initial_high)

    if priority == "low":
        assert int(current_low) > int(initial_low)


def assert_low_priority(url):
    assert_url_priority(url, "low")


def assert_high_priority(url):
    assert_url_priority(url, "high")


assert_high_priority("http://2.2.2.2:5000/router?text=How+did+you+hear+about+U+REPORT?&receivers=256704008979")
assert_high_priority("http://2.2.2.2:5000/router?text=Hi&receivers=256704008979")