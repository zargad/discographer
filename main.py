#!/usr/bin/env python3
"""Print out a discography of an artist."""
from datetime import datetime
from time import sleep
import discogs_api


def main():
    client = discogs_api.Client('ExampleApplication/1.0')
    artist = client.artist(input('artist id: '))
    releases = get_releases(client, artist)
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
    return f'*{months[date[1]} {date[2]}*'


def get_releases(client, artist):
    releases = []
    for i, release in enumerate(artist.releases, start=1):
        print(i, '/', len(artist.releases))
        if isinstance(release, discogs_api.Master):
            release = client.release(release.versions[0].id)
        title = release.title
        print(release.released)
        date = get_date(release.released)
        releases.append((title, date))
        sleep(10)
    return releases


def get_date(raw_date):
    date = list(map(int, raw_date.split('-')))
    date += [0] * (3 - len(date))
    date = map(lambda n: 1 if n == 0 else n, date)
    date = datetime(*date)
    return date


if __name__ == '__main__':
    main()
