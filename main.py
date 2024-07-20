#!/usr/bin/env python3
"""Print out a discography of an artist."""
from datetime import datetime
from time import sleep
import discogs_api


def main():
    user_token = input('user token (optional): ').strip()
    client = discogs_api.Client('ExampleApplication/1.0', user_token=user_token)
    if user_token:
        try:
            print('Hello', client.identity().username + '!')
        except discogs_api.exceptions.HTTPError:
            print('Unknown user id!')
            return
    artist_id = input('artist id: ').strip()
    try:
        artist = client.artist(artist_id)
        print('Artist:', artist.name)
    except discogs_api.exceptions.HTTPError:
        print('Unkown artist!')
        return
    releases = get_releases(client, artist, bool(user_token))
    releases.sort(key=lambda r: r[1])
    print_releases(artist.name, releases)


def print_releases(artist, releases):
    months = [
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
    ]
    print('#', artist.name)
    print()
    print('##', f'[Discography]({artist.url})')
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


def escape_markdown(text):
    for c in ('\\', '[', '*', '_', '^', '#', ''):
        text = text.replace(c, '\\' + c)
    return text


def format_date(date):
    return f'*{months[date[1]]} {date[2]}*'


def get_releases(client, artist, has_user_token):
    delay = 3 if has_user_token else 10
    releases = []
    for i, release in enumerate(artist.releases, start=1):
        print(i, '/', len(artist.releases))
        if isinstance(release, discogs_api.Master):
            release = client.release(release.versions[0].id)
        title = release.title
        print(release.released)
        date = get_date(release.released)
        releases.append((title, date))
        sleep(delay)
    return releases


def get_date(raw_date):
    date = list(map(int, raw_date.split('-')))
    date += [0] * (3 - len(date))
    date = map(lambda n: 1 if n == 0 else n, date)
    date = datetime(*date)
    return date


if __name__ == '__main__':
    main()
