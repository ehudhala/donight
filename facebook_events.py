import facebook


class Event:
    def __repr__(self):
        return repr(self.__dict__)


class FacebookEventScraper:
    """docs at https://developers.facebook.com/docs/graph-api/reference/event/"""

    def __init__(self, access_token):
        self.__graph = facebook.GraphAPI(access_token, version='2.5')

    def scrape(self, event_id):
        event_dict = self.__graph.get_object(
            event_id,
            fields="place,name,description,start_time,end_time,ticket_uri,can_guests_invite")

        event = Event()
        event.description = event_dict.get("description")
        event.title = event_dict.get("name")
        event.place_name = event_dict.get("place", {}).get("name")  # coordinates and id also available
        event.start_time = event_dict.get("start_time")
        event.end_time = event_dict.get("end_time")
        event.uri = "https://www.facebook.com/events/" + event_dict.get("id")
        event.ticket_uri = event_dict.get("ticket_uri")
        event.can_guests_invite = event_dict.get("can_guests_invite")  # TODO what if false?
        return event


if __name__ == '__main__':
    s = FacebookEventScraper(
        "CAACEdEose0cBAHFBqSBzSJcaagDRQn1SGppamlkDZAc9WBP1Hzey9ZBtZBZAkZBhAZBPy3DeK0jIyQTOyEWPUeE6zhl0tlagD1vEgrWjRirIofupfYJgXosf2P19dZAxZCrZCT1jeqCGIU0Cuk0quYoGAHiH8b4UsX9qFVVS1jKfwTjsArMQfeFml2pz9ICFnDPgnqHPG0SxAxAZDZD")
    event = s.scrape('526840047493451')  # access token has no permissions
    print(event)
    event = s.scrape('425519877629394')  # access token has no permissions
    print(event)
