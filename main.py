#!/usr/bin/env python3
"""Print out a discography of an artist."""
from datetime import datetime
from time import sleep
from json.decoder import JSONDecodeError
import discogs_api


def main():
    user_token = input('user token (optional): ').strip()
    client = discogs_api.Client('ExampleApplication/1.0', user_token=user_token)
    if user_token:
        try:
            print('Hello', client.identity().username + '!')
        except (discogs_api.exceptions.HTTPError, JSONDecodeError):
            print('Unknown user id!')
            return
    artist_id = input('artist id: ').strip()
    try:
        artist = client.artist(artist_id)
        print('Artist:', artist.name)
    except (discogs_api.exceptions.HTTPError, JSONDecodeError):
        print('Unkown artist!')
        return
    releases = get_releases_details(client, artist, bool(user_token))
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


def get_releases_details(client, artist, has_user_token):
    delay = 3 if has_user_token else 10
    releases_details = []
    releases_count = len(artist.releases)
    failed_releases = []
    for i, release in enumerate(artist.releases, start=1):
        print(i, '/', releases_count)
        try:
            details = get_release_details(client, release, delay)
            releases_details.append(details)
        except (discogs_api.exceptions.HTTPError, JSONDecodeError):
            failed_releases.append(release)
            print('RATE LIMITED: FAILED GETTING', len(failed_releases), 'RELEASES DETAILS')
    while failed_releases:
        print(len(failed_releases), 'FAILED RELEASES')
        failed_releases_buffer = []
        for i, release in enumerate(failed_releases, start=1):
            print(i, '/', len(failed_releases))
            try:
                details = get_release_details(client, release, delay)
                releases_details.append(details)
            except (discogs_api.exceptions.HTTPError, JSONDecodeError):
                failed_releases_buffer.append(release)
                print('RATE LIMITED: FAILED GETTING', len(failed_releases), 'RELEASES DETAILS')
        failed_releases = failed_releases_buffer[:]
    return releases_details


def get_release_details(client, release, delay):
    if isinstance(release, discogs_api.Master):
        oldest_release = release.versions[0]
        sleep(delay)
        release_id = oldest_release.id
        sleep(delay)
        release = client.release(release_id)
        sleep(delay)
    title = release.title
    sleep(delay)
    date = get_date(release.released)
    sleep(delay)
    return (title, date)


def get_date(raw_date):
    date = '0' if raw_date is None else raw_date
    date = list(map(int, date.split('-')))
    date += [0] * (3 - len(date))
    date = map(lambda n: 1 if n == 0 else n, date)
    date = datetime(*date)
    return date


if __name__ == '__main__':
    main()
