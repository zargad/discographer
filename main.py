#!/usr/bin/env python3
"""Print out a discography of an artist."""
import sys
from datetime import datetime
from time import sleep
from json.decoder import JSONDecodeError
import discogs_api


def main():
    user_token = input('user token (optional): ').strip()
    client = discogs_api.Client('ExampleApplication/1.0', user_token=user_token)
    if user_token:
        safe_get_request = SafeGetRequest(.15, 20)
        try:
            eprint('Hello', client.identity().username + '!')
        except (discogs_api.exceptions.HTTPError, JSONDecodeError):
            eprint('Unknown user id!')
            return
    else:
        safe_get_request = SafeGetRequest(1.5, 200)
    artist_id = input('artist id: ').strip()
    try:
        artist = client.artist(artist_id)
        eprint('Artist:', artist.name)
    except (discogs_api.exceptions.HTTPError, JSONDecodeError):
        eprint('Unkown artist!')
        return
    releases = get_releases_details(client, artist, safe_get_request)
    releases.sort(key=lambda r: r[1])
    print_releases(artist, releases, safe_get_request)


def print_releases(artist, releases, safe_get_request):
    """Print a markdown document from the release details."""

    name = safe_get_request(1000, lambda: artist.name)
    print('#', name)
    print()
    url = safe_get_request(1000, lambda: artist.url)
    print('##', f'[Discography]({url})')
    year = None
    for (title, date) in releases:
        if year != date.year:
            year = date.year
            print()
            print('###', year)
            print()
        title = escape_markdown(title)
        date = format_date(date)
        print(title, '-', date)


class SafeGetRequest:
    """Run the same request multiple times and adjust to rate limits."""

    def __init__(self, min_delay, max_delay):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.delay = (min_delay + max_delay) / 2

    def update_delay(self, success):
        ratio = 8/9
        if success:
            self.delay = self.delay * ratio + self.min_delay * (1 - ratio)
        else:
            self.delay = self.max_delay * ratio + self.delay * (1 - ratio)
        eprint(self.delay)

    def __call__(self, tries, request_function):
        for i in range(tries):
            eprint('try:', i, '/', tries)
            sleep(self.delay)
            try:
                result = request_function()
                eprint('SUCCESS')
                self.update_delay(True)
                return result
            except (discogs_api.exceptions.HTTPError, JSONDecodeError):
                eprint('FAIL')
                self.update_delay(False)
        raise discogs_api.exceptions.HTTPError



def escape_markdown(text):
    for c in ('\\', '[', '*', '_', '^', '#'):
        text = text.replace(c, '\\' + c)
    return text


def format_date(date):
    months = (
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Oct',
        'Nov',
        'Dec',
    )
    return f'*{months[date.month - 1]} {date.day}*'


def get_releases_details(client, artist, safe_get_request):
    """Get the title and dates of all releases from an artist."""

    releases_details = []
    releases_count = safe_get_request(1000, lambda: len(artist.releases))
    iterator = safe_get_request(1000, lambda: enumerate(artist.releases, start=1))
    while True:
        try:
            entry = safe_get_request(1000, lambda: next(iterator))
        except StopIteration:
            break
        i, release = entry
        eprint(i, '/', releases_count)
        details = get_release_details(client, release, safe_get_request)
        releases_details.append(details)
        eprint(*details)
    return releases_details


def get_release_details(client, release, safe_get_request):
    if isinstance(release, discogs_api.Master):
        oldest_release = safe_get_request(1000, lambda: release.versions[0])
        release_id = safe_get_request(1000, lambda: oldest_release.id)
        release = safe_get_request(1000, lambda: client.release(release_id))
    title = safe_get_request(1000, lambda: release.title)
    released = safe_get_request(1000, lambda: release.released)
    date = get_date(released)
    return (title, date)


def get_date(raw_date):
    date = '0' if raw_date is None else raw_date
    date = list(map(int, date.split('-')))
    date += [0] * (3 - len(date))
    date = map(lambda n: 1 if n == 0 else n, date)
    date = datetime(*date)
    return date


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if __name__ == '__main__':
    main()
