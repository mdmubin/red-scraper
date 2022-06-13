import os
import praw
import shutil
import requests

from subprocess import run


def download_content(post: str, outDir: str = '', filetype: str = 'i') -> None:
    def __download(url, f):
        r = requests.get(url, stream=True)
        if r.status_code == 200:  # OK
            with open(f, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        else:
            raise requests.HTTPError(f'HTTP Response : {r.status_code}')

    _ = post.title  # get rid of lazy obj
    outDir = (outDir + '/') if outDir[-1] != '/' else outDir

    if filetype == 'i':
        url = post.url
        filename = url.split('/')[-1]
        print(url)
        __download(url, (outDir + filename))
    elif filetype == 'v':
        v_url = post.media['reddit_video']['fallback_url'].split('?')[0]
        # get audio url from fallback url
        a_url = v_url.split('/')
        a_url.pop()
        a_url.append('DASH_audio.mp4')
        a_url = '/'.join(a_url)

        a_tmp = outDir + '_tmp_audio.mp4'
        v_tmp = outDir + '_tmp_video.mp4'

        __download(a_url, a_tmp)
        __download(v_url, v_tmp)

        # ffmpeg stitch audio & video
        run(f"ffmpeg -i {v_tmp} -i {a_tmp} -c copy {outDir + '/' + post.id + '.mp4'}")
        # cleanup tmp audio file
        os.remove(a_tmp)
        os.remove(v_tmp)
    else:
        raise ValueError('Variable `filetype` is expected to be any one of '
                         '"i" for images, "g" for gifs or "v" for videos')


if __name__ == '__main__':
    reddit = praw.Reddit('RED_SCRAPER', user_agent='WIN10:red-scraper:v0.1.0')

    # A League of Legends meme. thought it was funny :P
    s = reddit.submission(id='vaqdw5')
    download_content(s, 'out/', 'v')

    # A cool looking wallpaper from r/Wallpaper
    s = reddit.submission(id='vapi19')
    download_content(s, 'out/', 'i')
