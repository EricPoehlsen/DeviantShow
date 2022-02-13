# DeviantShow
***by Eric Pöhlsen***  

This program let's you watch DeviantArt.com galleries and favourites collections as slideshow.
There has been a similar feature on DeviantArt, called SitBack that was implemented in Flash. 
This slideshow feature has been discontinued by DeviantArt, unfortunatly, as I'd like to mention.

SitBack was a rather rudimentary slideshow solution. It only allowed sequential viewing.
And it always started at the beginning of the gallery. But that was still better than no slideshow feature at all. 
 
Please note that neither am I, nor is this software, in any way affiliated or endorsed by DeviantArt.com.

## Starting the program
There are two ways to run this program, run the **Python Script** or use the **Windows executable**.
Please refer to the respective section below for further information. 

### Python script
This program is implemented using Python and should run on Python 3.4+.

Just execute `python ds.py`

#### Required libraries
Beside the standard library you will need the following libraries: 
* **Pillow (PIL)**  
    https://pypi.python.org/pypi/Pillow
* **requests**  
    https://pypi.python.org/pypi/requests
* **lxml**  
    https://pypi.python.org/pypi/lxml

### Command-line arguments
There are several command-line arguments that can be used while invoking the program.

`--interval ##`  
    The initial display interval in seconds
  
`-- limit ##`  
    The maximum number of RSS chunks to load. 
    
`--path PATH-TO-FILES`  
    Where to look for files and store the downloads
    
`--nsfw`  
    Flag to allow displaying mature content

`--no-credits`  
    Don't show image title and author (and current image number). 
    
Command-line arguments take precedence over the internal defaults and the `config.ini`.

### Config file
The internal default configuration can be overwritten by using a `config.ini` in the progam directory.
You can create the default config file by pressing **c** on the keyboard. 
This will not overwrite an existing config file. 
 
## Using the program 
### Opening a gallery
Copy and paste a gallery or favorites URL from your browser into the URL bar of DeviantShow.
They should look like `http://user.deviantart.com/gallery/12345678/Name` or 
`http://user.deviantart.com/favourites/12345678/Name`. 
Of course you can access the main gallery / favourites of a user as well.
Please not the Section *'handling huge galleries'*.  

You can additionally just add a search term into the entry-field. 

Click **Play** or press **Enter** to load the gallery data and start your slideshow
 
#### Playlist modes
There are three modes *sequential*, *backwards* and *random*.

You can use the mode-button in the toolbar or the following keys:  
**F5** - sequential  
**F6** - backwards  
**F7** - random

Switching the mode is only possible if a playlist is loaded. 

You can use the arrow keys **←left** and **right→** to move through the playlist. 
Switching to random mode will shuffle the playlist - obviously. 
Once shuffled the order will remain the same until you switch the mode again.

#### Speed of the slideshow
You can easily change the speed of the slideshow by setting the display time. 
Just change the entry field at the right of the toolbar - the value is given in seconds. 

You can additionally use the **↓down**-key to reduce the display time by one second or the **↑up**-key to increase it.

Note that this will take effect with the next image that is loaded. 
 
Minimum interval is 3 seconds.

You can *pause* and *unpause* the slideshow at any time by using the **spacebar**.
 
#### Fullscreen mode
Use **F11** to toggle the fullscreen-mode. 

Please note that the current screen will not be rerendered when resizing the program.
The change will effect the next loaded image.  

#### Visit the deviation page
Simply double-click the image (or somewhere on the canvas) to open a webbrowser that will take you to the deviation page.

#### Handling huge galleries
Some galleries and favourites collections are massive, with hundreds of entries. The RSS feed, 
used to construct your playlist is limited to 60 entries. 
Per default DeviantShow will get a maximum of three chunks from the RSS feed. 
So collections with up to 180 entries will be shown easily. 

To access larger collections there are two ways: 

**Recommended:**  
Just add `?offset=##` to your search. If you specify `?offset=20` it will start with the 21st entry.
Again it will load a maximum of three RSS chunks. 

**Possible, but not recommended:**  
Adjust the number of RSS chunks to load by specifying `--limit #` as command-line argument. 
Starting the program with `--limit 20` will load up to ~1200 entries. 
As you probably won't watch so many images in one session I highly advise against it. 

## License
#### Using the program:  
You may use this program for it's intended purpose - as Slideshow Viewer for DeviantArt.com.
Please respect the terms of service of DeviantArt.com. 
**Do not use this program to download excessive amounts of images!**

If you run this program with the `--nsfw`flag you certify that you are at least 18 years old.  

This software is provided 'as is' without any warranties.

#### Using the source-code:
I will not specify a license. This software is to be regarded as "Free" and "Open Source". 
Use it however you like. I'd only like to point out that just changing the authors name in the 
'about' dialog is not what I envision as fair use of open source software.
 
This license applies to this software only, not to the content you are able to access with it. 
All artwork you can view with this program is copyrighted and licensed as specified by its respective owners. 

#### Third party contents
This program comes bundled with the font *H.H. Samuel* by [Fernando Haro](http://www.defharo.com). 
The font is available under the SIL Open font license.  

## FAQ
Okay technically no one has asked any of those questions, yet. 
I decided to answer them proactively.
If you have a question that is not answered, let me know. 

#### Don't I have to login to DeviantArt?
No. It is not necessary to provide any login credentials for DeviantArt.com, you can use the service *anonymously*.

Please be aware that your usage of their service can and will probably be logged by DeviantArt.com and other entities,
based on your IP address.

#### So what about mature content?
Do not worry, you'll get all that dirty mature content you are looking for, even without logging in.
All you have to do is run the program with the command-line argument `--nsfw`. 

Please be aware that the content creators rate their images, so it is possible that images are indeed 
'mature content' but not marked accordingly. 

#### Is this an 'official' software?
No. I am not affiliated with DeviantArt.com in any way. 

#### How does it work?
DeviantArt.com provides an RSS feed for it's contents. 
The gallery url or search term you provide is used to request the 
appropriate RSS from which the image relevant URLs are than retrieved. 

#### Is the communication secure?
This program uses HTTPS encrypted requests to exchange data with the DeviantArt.com servers. 

#### Will I get into trouble using this tool?
If you use this tool as intended it is, so is my understanding, complient with the DeviantArt Terms of Services.
The RSS feed is provided as a publicly available service. The images will only be downloaded as needed, not in bulk.
If you do not delete the contents of the downloads folder, the images should be only downloaded once.
This saves bandwidth for you and for DeviantArt. This program also does not hide it's requests to the Server in any way. 
It identifies itself as *DeviantShow RSS Reader* and *DeviantShow ImageLoader* respectively.  

#### Isn't this like using an AdBlocker?
Yes, it does the same thing as an AdBlocker, you will not see ads when using the slideshow. 
So if you'd like to support DeviantArt financially and use this tool -
consider getting a DeviantArt Core Membership.

#### Can I use the fullscreen mode on a secondary screen?
At least on Windows 10 it works. Maximize the program on the intended screen,
hit F11 after.

#### This software is great I'd like to pay you some money?
Seriously?! 

#### This program is a piece of crap and ...
No one forces you to use it. If you don't like it, don't use it.

#### I stumbled accross a bug. 
Okay, please let me know:  
https://github.com/EricPoehlsen/DeviantShow/issues

#### Can you add ...?
The program does pretty much what I expected it to do. 
Feel free to request features using the same link as if you'd like to report a bug.

#### Can you make a slideshow for ***.com?
Short answer, I probably won't. I made this program for two reasons:
* I missed having a slideshow on DeviantArt.com
* I wanted to learn a few new things in Python

But have a look at the Source of this program and feel free to make one yourself.
