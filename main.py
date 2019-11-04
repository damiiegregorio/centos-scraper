from requests import get
import csv
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from datetime import datetime


def get_url(base_url):
    try:
        with closing(get(base_url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(base_url, str(e)))
        return None


def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    print(e)


def get_parent_url():
    """Getting parent directories"""

    base_url = 'http://mirror.rise.ph/centos/7/'
    response = get_url(base_url)

    if response is not None:
        soup = BeautifulSoup(response, 'html.parser')
        table = soup.find_all('tr')
        for tr in table:
            if tr.td is None:
                continue
            elif tr.td.img['alt'] == '[PARENTDIR]':
                continue
            else:
                recursive(tr, base_url)

    # Raise an exception if we failed to get any data from the url
#     raise Exception('Error retrieving contents at {}'.format(base_url))


def recursive(urls, new_url):
    """Recursive files"""
    link = urls.a.text
    if link.endswith('/'):
        new_url += link
        response = get_url(new_url)

        if response is not None:
            soup = BeautifulSoup(response, 'html.parser')
            table = soup.find_all('tr')
            for tr in table:
                if tr.td is None:
                    continue
                elif tr.td.img['alt'] == '[PARENTDIR]':
                    continue
                else:
                    recursive(tr, new_url)
    else:
        url = "{}{}".format(new_url, link)
        filename = link
        size = urls.text.split('  ')[1]

        files = [url, filename, size]
        csv_file(files)


# def date_formatter():
#     today = datetime.now().strftime("-%Y-%m-%d-%H-%M")
#     date_today = "output" + today
#     return date_today


def csv_file(files):
#     date_today = date_formatter()

    with open("output.csv", 'a+', encoding='utf-8', newline='') as output_file:
        writer = csv.writer(output_file, lineterminator='\r')
        writer.writerow(files)


def main():
    print('Getting the files....')
    get_parent_url()


if __name__ == '__main__':
    main()
