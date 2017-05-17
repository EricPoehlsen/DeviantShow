# DeviantShow
***by Eric Pöhlsen***

This program is a *web-scraper* that let's you watch DeviantArt.com galleries and fevourites collections as slideshow.
Until 2016 DeviantArt.com featured a flash based slideshow on its website called sitback. 
Some time in fall 2016 this feature was gone, unfortunatly, as I'd like to mention. 
To be honest, that slideshow was not really good, there was no random slideshow for example.
But that is still better than no slideshow feature at all. 

## Usage
Start the program, paste a DeviantArt.com gallery URL into the address bar and press "Play".
If you have an active internet connection, your slideshow should start after a few moments.
You can also just enter a search string into the box and hit play.
 
#### Speed of the slideshow
You can easily change the speed of the slideshow by setting the display time. 
Just change the entry field at the right of the toolbar - the value is given in seconds. 

Note that this will take effect with the next image that is loaded 

#### Fullscreen mode
Use F11 to toggle the fullscreen-mode. 

#### Sequential, Random, Backwards
You can easily switch between this three Modes by using the 'Mode: ' Button

#### Handling huge galleries
Some galleries and favourites collections are massive, with hundrets of entries. The RSS feed, 
used to construct your playlist is limited to ~60 entries. 
Per default DeviantShow will get a maximum of three chunks from the RSS feed. 
So collections with up to ~180 entries will be shown easily. 
To access larger collections there are two ways. 

**Recommended:**  
Just add '?offset=##' to your search. If you specify ?offset=20 it will start with the 20th entry.
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
I will not specify a license. This software is to be regarded as "Open Source" and "Public Domain". 
Use it however you like. I'd only like to point out that just changing the authors name in the 
'about' dialog is not what I envision as fair use of open source software.
 
This license applies to this software only, not to the content you are able to access with it. 
All artwork you can view with this program is copyrighted and licensed as specified by its respective owners. 

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
I honestly hope not. In my personal opinion using this tool is not violating the DeviantArt Terms of Service.
The RSS feed is provided as a publicly available service. The images will only be downloaded as needed, not in bulk.
If you do not delete the contents of the downloads folder, the images should be only downloaded once.
This program also does not hide it's requests to the Server in any way. 
It identifies itself as *DeviantShow RSS Reader* and *DeviantShow ImageLoader* respectively.  

#### Isn't this like using an AdBlocker?
Yes, it does the same thing as an AdBlocker, you will not see ads. 
So if you'd like to support DeviantArt financially and use this -
consider getting a DeviantArt Core Membership.

#### This software is great I'd like to pay you some money?
Seriously?! Okay go ahead 

#### This program is a piece of crap and ...
No one forces you to use it. If you don't like it, don't use it.

#### Can you make a slideshow for ***.com
Short answer, I probably won't. But have a look at the Source of this program and feel free to make one yourself. 