Usage:
```
./podcastdl.py <podcast>.xml
```

Directory structure:
```
<podcast>/ 
|- mp3/
|--- {ep_index}_{ep_title}_{fmtdate}_audio.mp3 (+ show image attached)
|- imgs/
|--- main_image.jpg (podcast image)
|--- {ep_index}_{ep_title}_{fmtdate}_image.jpg (XX episode image)
|- txt/
|--- main_description.txt
|--- {ep_index}_{ep_title}_{fmtdate}_description.txt
|- www/
|--- index.html
|--- js/
|------ mp3-player.js
```

Serve:
```
./gen_website.py <podcast>
```
Maybe use something simple like customized [dropcast](https://github.com/amiechen/codrops-dropcast) to generate your website.

Thanks to:  
[kissgyorgy](https://github.com/kissgyorgy/simple-podcast-dl/blob/master/podcast_dl/podcast_dl.py)
