#!/usr/bin/env python3
"""Print out a discography of an artist."""
from time import sleep
import discogs_api


def main():
    d = discogs_api.Client('ExampleApplication/1.0')
    artist = d.artist(input('artist id: '))
    print('#', artist.name)
    months = {
        '01': 'Jan',
        '02': 'Feb',
        '03': 'Mar',
        '04': 'Apr',
        '05': 'May',
        '06': 'Jun',
        '07': 'Jul',
        '08': 'Aug',
        '09': 'Sep',
        '10': 'Oct',
        '11': 'Nov',
        '12': 'Dec',
    }
    year = None
    for release in artist.releases:
        if isinstance(release, discogs_api.Master):
            release = d.release(release.versions[0].id)
        date = release.released.split('-')
        if year != date[0]:
            year = date[0]
            print()
            print('##', year)
            print()
        print(release.title, '-', months[date[1]], date[2])
        sleep(10)


if __name__ == '__main__':
    main()
