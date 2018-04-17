import json
from application_only_auth import Client

class Twitter():
    """Get last 100 tweets of an account"""

    client = ""

    def __init__(self):
        self.client = Client('XMWmonO1hiqZgooIhu8JgNUXQ', 'aHk4u50HCnHzWWFgCvFdXyYZeOow4oJ8co2z7B1jcubKd0JSym')

    def get(self, username, count = 100):
        timeline = self.client.request("https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=" + username + "&count=" + str(count))
        print(json.dumps(timeline, indent=4, sort_keys=True))

test = Twitter()
test.get('__amirmasoud__', 1)
