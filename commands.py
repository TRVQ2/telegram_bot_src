import requests
from lxml import etree
import lxml.html
import re


def parse_page(url) -> list:
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return
    except requests.exceptions.RequestException as e:
        return

    return lxml.html.document_fromstring(r.text)


# https://lyrsense.com/blackmores_night/wind_in_the_willows ===================
def lyrsense_prepare_url(band, song):
    if band is None or len(band) == 0 or song is None or len(song) == 0:
        return
    band = '_'.join(band.lower().replace("'", "").split())
    song = '_'.join(song.lower().replace("'", "").split())
    return f"https://lyrsense.com/{band}/{song}"


def lyrsense_page_to_text(band, song):
    tree = parse_page(lyrsense_prepare_url(band, song))
    if tree is None:
        return None

    lyric_ru_name = tree.xpath('//*[@id="ru_title"]/text()')
    lyric_fr_name = tree.xpath('//*[@id="fr_title"]/text()')

    return str(lyric_ru_name) + '\n\n' + \
        ''.join(
            '\n' if i.text is None else i.text + ' '
            for i in tree.xpath('//*[@id="ru_text"]')[0]
        ) + '\n=====\n' + \
        str(lyric_fr_name) + '\n\n' + \
        ''.join(
            '\n' if i.text is None else i.text + ' '
            for i in tree.xpath('//*[@id="fr_text"]')[0]
        )


# Musinfo specific methods ====================================================
def musinfo_prepare_url(band, song):
    if band is None or len(band) == 0 or song is None or len(song) == 0:
        return
    band = '-'.join(band.lower().split())
    song = '-'.join(song.lower().split())
    return f"https://ru.musinfo.net/lyrics/{band}/{song}"


def musinfo_page_to_text(band, song):
    tree = parse_page(musinfo_prepare_url(band, song))
    if tree is None:
        return None

    return '\n'.join(
        '' if i.text is None else i.text
        for i in tree.xpath('//*[@id="lyric-dst"]')[0]
    ) + '\n=====\n' + '\n'.join(
        '' if i.text is None else i.text
        for i in tree.xpath('//*[@id="lyric-src"]')[0]
    )


def musinfo_page_to_text2(band, song):
    tree = parse_page(musinfo_prepare_url(band, song))
    if tree is None:
        return None

    lyric_src_name = tree.xpath('//*[@id="lyric-dst"]/div[1]/text()')
    lyric_src = tree.xpath('//*[@id="lyric-dst"]/div[@class="line"]/text()')
    lyric_dst_name = tree.xpath('//*[@id="lyric-src"]/div[1]/text()')
    lyric_dst = tree.xpath('//*[@id="lyric-src"]/div[@class="line"]/text()')
    return str(lyric_src_name) + '\n\n' + \
        '\n'.join(lyric_src) + "\n=====\n" + \
        str(lyric_dst_name) + '\n\n' + \
        '\n'.join(lyric_dst)
# Musinfo specific methods ====================================================


def get_lyrics(path):  # expected input format 'Band|Song'
    if path is None or len(path) < 1:
        return supported_commands['/lyrics']['usage']
    items = path.strip().split('|')
    if len(items) == 1:
        return 'Wrong request: Song is not specified. ' + \
            supported_commands['/lyrics']['usage']
    result = ''
    # print(f"Searching band: {items[0]}, song: {items[1]}...")
    for i in supported_commands['/lyrics']['api_list']:
        result = i(items[0], items[1])
        if result is not None:
            break
        # else:
        #     print("Haven't found the song")
    return result


supported_commands = {
    '/lyrics': {
        'desc': 'To find lyrics and translation',
        'usage': 'Use /lyrics Band|Song',
        'commands': [],
        'call': get_lyrics,
        'api_list': [lyrsense_page_to_text, musinfo_page_to_text]
    }
}


def process_message(message):
    if message is None:
        return
    answer = None
    message = message.strip()
    list = message.split(' ', 1)
    if list[0] in supported_commands:
        call = supported_commands[list[0]]['call']
        answer = call(message.replace(list[0], ''))
    elif list[0] in ('/start', '/help', '/commands'):
        answer = '\n'.join(
            f"{i}\t- {supported_commands[i]['desc']}" +
            f". {supported_commands[i]['usage']}"
            for i in supported_commands
        )
    return answer


def main():
    '''text = None
    print(process_message(text))
    text = ''
    print(process_message(text))
    text = '/lyrics'
    print(process_message(text))
    text = '/lyrics Metallica'
    print(process_message(text))'''
    text = '/lyrics Metallica|Nothing Else Matters'
    print(process_message(text))


if __name__ == "__main__":
    main()
