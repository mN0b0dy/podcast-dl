import eyed3
from eyed3.id3.frames import ImageFrame
from pathlib import Path
from mutagen.mp3 import MP3

DEBUG=0

def tagmp3(file, title=None, front_img=None, track_id=None, cmt=None):
    if DEBUG:
        print('---- TAG MP3 -----')

    desc_cache = {}
    '''
    audiofile = eyed3.load(file)
    if (audiofile.tag == None):
        audiofile.initTag()
    
    for img in audiofile.tag.images:
        suf = img.mime_type.split("/")[1]
        tempf = Path(file).with_suffix('').name
        tempout = f"/tmp/{tempf}_{img.picture_type}.{suf}"
        if DEBUG:
            print(img.picture_type)
            print(img.mime_type)
            print(img.description)
        
        audiofile.tag.images.remove(img.description)

        desc_cache[img.picture_type] = img.description
        if DEBUG:
            with open(tempout, 'wb') as fp:
                fp.write(img.image_data)
            print(f'OLD {img.picture_type} COVER: {tempout}')
    '''
    # clear all metadata
    # 1) fuck vlc art cache: ~/.cache/vlc/art/
    # 2) fuck eyed3 can't clear tags properly...
    try:
        mp3 = MP3(file)
        mp3.delete()
        mp3.save()
    except Exception as err:
        print(f"ERROR {str(err)}")
    audiofile = eyed3.load(file)
    if (audiofile.tag == None):
        audiofile.initTag()

    if front_img:
        if DEBUG:
            print(f"NEW FRONT_COVER -> {front_img}")
        _type = desc_cache.get(ImageFrame.FRONT_COVER)
        if _type:
            audiofile.tag.images.set(ImageFrame.FRONT_COVER, open(front_img,'rb').read(), b'image/jpeg', _type)
        else:
            audiofile.tag.images.set(ImageFrame.FRONT_COVER, open(front_img,'rb').read(), b'image/jpeg')
    # don't do back cover image that; overrides front cover....
    if track_id:
        audiofile.tag.track_num = track_id
    if cmt:
        audiofile.tag.comments.set(cmt)
    audiofile.tag.title = title
    
    audiofile.tag.save()

    if DEBUG:
        print('----- TAG MP3: DONE -----')

# EOF
'''
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError, ID3, TALB, TPE1, TPE2, TCON, TYER, TRCK, TIT2, APIC, TPOS

ID3_TITLE = "TIT2"
ID3_SONG_ARTIST = "TPE1"
ID3_ALBUM = "TALB"
ID3_ALBUM_ARTIST = "TPE2"
ID3_TRACK_NO = "TRCK"
ID3_RELEASE_YEAR = "TYER"
ID3_CONTENT_TYPE = "TCON"
ID3_COMMENT = "COMM"
ID3_TIMESTAP = "TDRC"
ID3_PICTURE = "APIC"

def tagmp3(...): # using mutagen
    # also cool: https://github.com/interborough/mp3-metadata-autofiller/blob/main/autofiller.py
    # frame for mutagen: https://github.com/quodlibet/mutagen/blob/main/mutagen/id3/_id3v1.py#L116
    try:
        mp3 = MP3(file)
    except ID3NoHeaderError:
        mp3 = mutagen.File(file, easy=True)
        mp3.add_tags()
    print(f'Title: {mp3["TIT2"]}')
    print(f'Song Artist: {mp3["TPE1"]}')
    print(f'Album: {mp3["TALB"]}')
    print(f'Album Artist: {mp3[ID3_ALBUM_ARTIST]}')
    print(f'Track no.: {mp3[ID3_TRACK_NO]}')
    print(f'Content Type: {mp3[ID3_CONTENT_TYPE]}')
    print(f'Comment: {mp3[ID3_COMMENT]}')
    print(f'Timestamp: {mp3[ID3_TIMESTAMP]}')
    id3 = ID3(file)
    id3.save(v2_version=3)
    pic = APIC(
        encoding=3,
        mime='image/jpeg'
        type=3, # 3 is for the cover image
        desc=u'Episode Artwork',
        data=open('example.png').read()
    )
    
    # clear all tags
    try:
        mp3 = MP3(file)
        mp3.delete()
        mp3.save()
    except Exception as err:
        print(f"ERROR {str(err)}")

'''
