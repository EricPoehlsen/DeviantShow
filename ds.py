import argparse
import configparser
import tkinter as tk
import tkinter.messagebox as tkmb
import requests
from urllib.request import Request, build_opener
import os.path
from lxml import etree as et
from PIL import ImageTk, Image, ImageDraw, ImageFont, ImageFilter,\
    PngImagePlugin, JpegImagePlugin, GifImagePlugin
import random
import webbrowser
import messages as M
from requests.certs import where as findcert

# those are needed by py2exe
import requests.packages.urllib3
import queue
import lxml._elementpath


class App(tk.Frame):
    """ The main slideshow app 
    
    Args:
        master (tk.Tk): The main Tk instance ... 
        
    """

    def __init__(self, master):
        super().__init__(master=master)
        self.width = 0
        self.height = 0
        self.fullscreen = False
        self.stored_geometry = ""
        self.gallery_url = ""
        self.image_data = []
        self.playlist = []
        self.current = 0
        self.gallery_limit = 0
        self.interval = 0
        self.mode = "sequential"
        self.interval_var = tk.StringVar()
        self.timer = None
        self.nsfw = False
        self.credits = True
        self.cert = findcert()  # set to "cacert.pem" for py2exe

        # now the config ...
        self.ini = configparser.ConfigParser()
        self.loadConfig()

        # building the interface ...
        self.config(background=self.ini["CONFIG"]["background"])
        self.columnconfigure(0, weight=100)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=100)

        # creating the menu bar
        self.menuframe = tk.Frame(self)
        url_label = tk.Label(
            self.menuframe,
            text=M.UI_URL,
        )
        url_label.pack(side=tk.LEFT)
        self.url_bar = tk.Entry(self.menuframe)
        self.url_bar.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        play_button = tk.Button(
            self.menuframe,
            text=M.UI_PLAY,
            command=self.fetchGallery
        )
        play_button.pack(side=tk.LEFT)

        self.mode_button = tk.Button(
            self.menuframe,
            text=M.UI_MODE_SEQ,
            command=self.nextMode
        )
        self.mode_button.pack(side=tk.LEFT)
        interval_label = tk.Label(
            self.menuframe,
            text=M.UI_TIMER,
            font="Arial 15"
        )
        interval_label.pack(side=tk.LEFT)
        self.interval_entry = tk.Entry(
            self.menuframe,
            width=4,
            textvariable=self.interval_var,
        )
        self.interval_entry.pack(side=tk.LEFT, fill=tk.Y)
        self.interval_var.set(str(self.interval // 1000))
        self.interval_var.trace("w", lambda n, e, m: self.intervalChanged())

        about_button = tk.Button(
            self.menuframe,
            text=M.UI_ABOUT,
            command=self.showAbout
        )
        about_button.pack(side=tk.LEFT)

        self.menuframe.grid(row=0, column=0, sticky=tk.NSEW)

        # this is the canvas
        self.img_canvas = tk.Canvas(
            self,
            width=300,
            height=300,
            background=self.ini["CONFIG"]["background"],
            borderwidth=0,
            highlightthickness=0
        )
        self.img_canvas.bind("<Double-Button-1>", self.visitDA)
        self.img_canvas.grid(row=1, column=0, sticky=tk.NSEW)

        # the main tk instance
        self.master = master
        self.master.title(M.UI_TITLE)

        # creating all key bindings ...
        self.master.bind("<Configure>", self.resize)
        self.master.bind("<Right>", self.showNext)
        self.master.bind("<Left>", self.showPrevious)
        self.master.bind("<Up>", self.setInterval)
        self.master.bind("<Down>", self.setInterval)
        self.master.bind("<space>", self.pause)
        self.master.bind("<Return>", self.fetchGallery)
        self.master.bind("<F5>", self.sequentialMode)
        self.master.bind("<F6>", self.reversedMode)
        self.master.bind("<F7>", self.randomMode)
        self.master.bind("<F11>", self.toggleFullScreen)
        self.master.bind("<F12>", self.panicMode)
        self.master.bind("<c>", self.exportConfig)

    def loadConfig(self):
        """ read config and assign to variables as necessary """

        # defaults
        self.ini["CONFIG"] = {
            "interval": "10",
            "credits": "true",
            "limit": "3",
            "nsfw": "false",
            "path": "downloads",
            "background": "#000000",
            "text_color": "#dddddd",
            "font_file": "fonts/hh_samuel.ttf",
            "font_size": "30"
        }

        # read local config
        self.ini.read(["config.ini"])

        self.nsfw = self.ini.getboolean("CONFIG", "nsfw")
        self.credits = self.ini.getboolean("CONFIG", "credits")
        self.gallery_limit = self.ini.getint("CONFIG", "limit")
        interval = self.ini.getint("CONFIG", "interval")
        self.interval = interval * 1000
        self.interval_var.set(str(interval))

    def fetchGallery(self, event=None):
        """ read the given url and get the appropriate rss """

        url = self.url_bar.get()
        # do not reload the same gallery
        if url == self.gallery_url:
            self.nextImage()
            return
        else:
            self.gallery_url = url

        # filter any domain not that is not DeviantArt
        if url.startswith("http") and "deviantart.com" not in url:
            error = tkmb.showerror(
                title=M.ERROR,
                message=M.ERR_INVALID_URL,
                master=self
            )
            self.image_data = []
            return

        arguments = ""
        if "?" in url:
            url, arguments = url.split("?")

        # handle a 'search'
        if not url.startswith("http"):
            search = url.replace(" ", "+")
            rss = M.RSS_BASE + search

        else:
            url = url.split("//")[-1]
            elements = url.split("/")
            user = elements[0].split(".")[0]
            variant = elements[1]
            if variant == "favourites":
                variant = "favby"
            rss = M.RSS_BASE + variant + ":" + user
            if len(elements) > 3:
                rss += "/" + elements[2]

        print(rss)

        # display statusinfo
        info = self.createInfoImage(text=M.UI_BUILD_GALLERY)
        self.img_canvas.create_image(0, 0, image=info, anchor=tk.NW)
        self.img_canvas.info = info
        self.update()

        # get the data and construct the playlist
        self.image_data = self.readGallery(rss, arguments)
        self.playlist = list(range(len(self.image_data)))

        # start slideshow
        self.nextImage()

    def readGallery(self, url, arguments=""):
        """ retrieves the image urls (and metadata) from the rss 

        Args: 
            url (str): the rss url to access
            arguments (str): additiona arguments (like offset)
        """

        headers = requests.utils.default_headers()
        headers.update({"User-Agent": M.UA_RSSLOADER})
        media_info = []

        offset = 0

        if arguments:
            arg_list = arguments.split("&")
            for arg in arg_list:
                if "=" in arg:
                    name, value = arg.split("=")
                else: continue

                if name == "offset":
                    offset = int(value)

        for iteration in range(self.gallery_limit):
            rss_url = url + "&offset="+str(offset)
            try:
                rss_feed = requests.get(
                    rss_url,
                    headers=headers,
                    verify=self.cert
                )
                tree = et.fromstring(rss_feed.content)
                items = tree.findall(".//item")
                for i, item in enumerate(items):
                    data = {}
                    # images only, disregard text
                    content_tag = item.find("./media:content", tree.nsmap)
                    if content_tag.get("medium") != "image":
                        continue

                    # get the data
                    title_tag = item.find("./media:title", tree.nsmap)
                    author_tag = item.find("./media:credit", tree.nsmap)
                    rating_tag = item.find(".media:rating", tree.nsmap)
                    link_tag = item.find("./link")

                    img_url = content_tag.get("url")
                    author = author_tag.text
                    link = link_tag.text
                    title = title_tag.text
                    rating = rating_tag.text

                    img_url = img_url.replace("http:", "https:")
                    link = link.replace("http:", "https:")

                    data["img_url"] = img_url
                    data["title"] = title
                    data["link"] = link
                    data["author"] = author
                    data["rating"] = rating
                    media_info.append(data)

            except requests.ConnectionError as e:
                print(e)
                error = tkmb.showerror(
                    title=M.ERROR,
                    message=M.ERR_NO_CONNECTION,
                    master=self
                )
                i = 0

            offset += i

            # are we done yet?
            if i < 59:
                break

        return media_info

    def nextImage(self):
        """ Display next image in the playlist """

        if not self.image_data:
            return

        if self.current >= len(self.image_data):
            self.current = 0
        self.loadImage(self.image_data[self.playlist[self.current]])
        self.current += 1
        self.timer = self.after(self.interval, self.nextImage)

    def loadImage(self, resource_data):
        """ this retrieves the actual image and displays it on the canvas
        
        Args: 
            resource_data (dict): the image resource data 
        """

        # construct the local filename
        img_url = resource_data["img_url"]
        path = self.ini["CONFIG"]["path"]
        if not path.endswith("/"):
            path += os.sep
        filename = path + img_url.split("/")[-1]
        image = None

        if self.nsfw is False and resource_data["rating"] == "adult":
            # Oups ... - don't serve mature content ...
            nsfw = self.createInfoImage(text=M.UI_NSFW_INFO)
            self.img_canvas.create_image(
                0, 0,
                image=nsfw,
                anchor=tk.NW
            )
            self.img_canvas.nsfw = nsfw

        # load locally stored image from disk or retrieve from web
        elif os.path.isfile(filename):
            image = Image.open(filename)
        else:
            file = open(filename, mode="wb")
            request = Request(img_url)
            request.add_header("User-Agent", M.UA_IMAGELOADER)
            opener = build_opener()
            content = opener.open(request).read()

            file.write(content)
            file.close()
            image = Image.open(filename)

        # remove last image
        self.img_canvas.delete(tk.ALL)
        self.img_canvas.image = None

        # draw the new image
        if image is not None:
            # scaling the image for the screen
            img_ratio = image.width / image.height
            new_height = self.height
            new_width = self.height * img_ratio
            if new_width > self.width:
                new_width = self.width
                new_height = new_width / img_ratio
            new_width = int(new_width)
            new_height = int(new_height)
            image = image.resize((new_width, new_height), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(image)

            # draw current image
            self.img_canvas.create_image(
                self.width / 2,
                self.height / 2,
                image=photo,
            )
            self.img_canvas.image = photo

        # display credits ...
        if self.credits is True:
            img_info = self.createCreditsImage(resource_data)
            self.img_canvas.create_image(
                0, self.height,
                image=img_info,
                anchor=tk.SW
            )

            self.img_canvas.img_info = img_info

    def pause(self, event):
        """ pauses and unpauses the slideshow"""

        if not self.playlist:
            return

        if self.timer:
            self.after_cancel(self.timer)
            self.timer = 0

            # display info
            info = self.createInfoImage(text=M.UI_PAUSED)
            item_id = self.img_canvas.create_image(
                0, 0,
                image=info,
                anchor=tk.NW
            )
            self.img_canvas.info = info
            self.update()

            self.after(2500, self.img_canvas.delete, item_id)

        else:
            self.nextImage()

    def showNext(self, event):
        """ Cancel timer - go to next image in playlist """

        if not self.playlist:
            return
        self.after_cancel(self.timer)
        self.nextImage()

    def showPrevious(self, event):
        """ Cancel timer - go to previous image in playlist """

        if not self.playlist:
            return
        self.after_cancel(self.timer)
        self.current -= 2
        if self.current < 0:
            self.current = len(self.playlist) - 1
        self.nextImage()

    def nextMode(self):
        """ Switch to next mode: called by the button as command """

        if self.mode == "sequential":
            self.reversedMode()
        elif self.mode == "reversed":
            self.randomMode()
        elif self.mode == "random":
            self.sequentialMode()

    def randomMode(self):
        """ switch to random display mode """

        if self.playlist:
            self.mode = "random"
            self.mode_button.config(text=M.UI_MODE_RND)
            random.shuffle(self.playlist)
            self.current = self.playlist.index(self.current)

    def sequentialMode(self):
        """ Switch to sequential display mode """

        if self.playlist:
            self.mode = "sequential"
            self.mode_button.config(text=M.UI_MODE_SEQ)
            self.current = self.playlist[self.current]
            self.playlist.sort()

    def reversedMode(self):
        """ Switch to reversed sequential display mode """

        if self.playlist:
            self.mode = "reversed"
            self.mode_button.config(text=M.UI_MODE_REV)
            self.current -= 2
            if self.current < 0:
                self.current = len(self.playlist) - 1
            current = self.playlist[self.current]
            self.playlist.sort()
            self.playlist.reverse()
            self.current = self.playlist.index(current)

    def intervalChanged(self):
        """ Interval change based on changes of """

        # we only care if this was done with an active entrie field
        if self.master.focus_get() != self.interval_entry:
            return

        try:
            interval_text = self.interval_var.get()

            interval_int = int(interval_text)
            if interval_int < 3:
                self.interval = 3000
            else:
                self.interval = int(1000 * interval_int)
        except ValueError:
            pass

    def setInterval(self, event):
        """ Setting the interval with up and down keys ... """

        if event.keysym == "Up":
            self.interval += 1000
            self.interval_var.set(self.interval // 1000)
        if event.keysym == "Down" and self.interval > 3000:
            self.interval -= 1000
            self.interval_var.set(self.interval // 1000)

    def toggleFullScreen(self, event=None):
        if self.fullscreen:
            self.fullscreen = False
            self.master.overrideredirect(False)
            self.menuframe.grid(row=0, column=0, sticky=tk.NSEW)
            self.master.geometry(self.stored_geometry)

        else:
            self.stored_geometry = self.master.geometry()
            self.menuframe.grid_forget()
            self.master.overrideredirect(True)
            self.master.geometry("{0}x{1}+0+0".format(
                self.master.winfo_screenwidth(),
                self.master.winfo_screenheight()
            ))
            self.fullscreen = True

    def resize(self, event):
        """ Event handler tracking the available canvas size"""

        self.width = self.img_canvas.winfo_width()
        self.height = self.img_canvas.winfo_height()

    def visitDA(self, event=None):
        """ opens webbrowser to access deviation page """

        try:
            cur_data = self.image_data[self.playlist[self.current]]
            url = cur_data["link"]
            webbrowser.open_new(url)
        except IndexError:
            pass

    def createCreditsImage(self, resource_data):
        """ create the info (credits, image number) 
        
        Args: 
            resource_data (dict): image resource data
            
        Returns:
            ImageTk.Photoimage: The image object

        """

        font_size = self.ini.getint("CONFIG", "font_size")
        img_height = int(1.5 * font_size)
        img = Image.new('RGBA', (self.width, img_height), (0, 0, 0, 0))

        font = ImageFont.truetype(
            font=self.ini["CONFIG"]["font_file"],
            size=self.ini.getint("CONFIG", "font_size")
        )
        title = resource_data["title"] + " by " + resource_data["author"]

        draw = ImageDraw.Draw(img)
        draw.text(
            (5, 5),
            text=title,
            fill="#000000",  # self.ini["CONFIG"]["text_color"],
            font=font,
        )
        image_num = str(self.playlist[self.current] + 1)
        total_num = str(len(self.playlist))
        page = image_num + " / " + total_num
        page_width, page_height = draw.textsize(page, font)

        draw.text(
            (self.width - 5 - page_width, 5),
            text=page,
            fill="#000000",  # self.ini["CONFIG"]["text_color"],
            font=font,
        )

        img = img.filter(ImageFilter.GaussianBlur(3))

        draw = ImageDraw.Draw(img)
        draw.text(
            (5, 5),
            text=resource_data["title"] + " by " + resource_data["author"],
            fill=self.ini["CONFIG"]["text_color"],
            font=font,
        )
        draw.text(
            (self.width - 5 - page_width, 5),
            text=page,
            fill=self.ini["CONFIG"]["text_color"],
            font=font,
        )

        return ImageTk.PhotoImage(img)

    def createInfoImage(self, text):
        """ Creates the loading library info ... """
        font_size = self.ini.getint("CONFIG", "font_size")

        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        font = ImageFont.truetype(
            font=self.ini["CONFIG"]["font_file"],
            size=font_size
        )

        draw = ImageDraw.Draw(img)
        info_width, info_height = draw.textsize(text, font)
        x = int(self.width / 2 - info_width / 2)
        y = int(self.height / 2 - info_height / 2)
        draw.text(
            (x, y),
            text=text,
            fill="#000000",
            font=font,
            align="center"

        )

        img = img.filter(ImageFilter.GaussianBlur(3))

        draw = ImageDraw.Draw(img)
        draw.text(
            (x, y),
            text=text,
            fill=self.ini["CONFIG"]["text_color"],
            font=font,
            align="center"
        )

        return ImageTk.PhotoImage(img)

    def showAbout(self, event=None):
        pass

    def exportConfig(self, event=None):
        """ Export the default config """

        if not os.path.isfile("config.ini"):
            with open("config.ini", 'w') as configfile:
                self.ini.write(configfile)

    def panicMode(self, event):
        import os
        prompt = "{user}@{host}:~$ ".format(
            user=os.getenv("USERNAME", "user"),
            host=os.getenv("USERDOMAIN", "SYSTEM")
        )

        self.master.title(M.TERM_TITLE)
        self.master.minsize(500, 350)
        self.menuframe.grid_forget()
        self.img_canvas.grid_forget()
        if self.timer:
            self.after_cancel(self.timer)

        var = tk.StringVar()
        var.set(prompt)
        label = tk.Label(
            self,
            font="Courier 10",
            foreground="#cccccc",
            background="#000000",
            justify=tk.LEFT,
            anchor=tk.NW,
            textvariable=var,
        )
        label.grid(row=0, column=0, sticky=tk.NW)

        self.after(500, self.panicSwitch, var)

    def panicSwitch(self, var):
        prompt = var.get()
        if prompt.endswith("█"):
            var.set(prompt[:-1])
        else:
            var.set(prompt + "█")
        self.after(500, self.panicSwitch, var)


def main(args):
    window = tk.Tk()
    app = App(window)

    # after init overwrite defaults or config with values from args!
    if args.limit:
        app.gallery_limit = args.limit
    if args.interval:
        app.interval = args.interval * 1000
        app.interval_var.set(str(args.interval))
    if args.nsfw:
        app.nsfw = args.nsfw
    if args.credits is False:
        app.credits = args.credits
    app.pack(fill=tk.BOTH, expand=1)
    window.mainloop()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=M.ARGPARSE_DESCRIPTION)
    parser.add_argument(
        "--interval",
        type=int,
        dest="interval",
        # default=10,
        help=M.ARGPARSE_INTERVAL)
    parser.add_argument(
        "--limit",
        type=int,
        dest="limit",
        # default=4,
        help=M.ARGPARSE_GALLERYLIMIT)
    parser.add_argument(
        "--path",
        dest="path",
        type=str,
        # default="downloads",
        help=M.ARGPARSE_PATH)
    parser.add_argument(
        "--nsfw",
        action="store_const",
        const=True,
        help=M.ARGPARSE_NSFW
    )
    parser.add_argument(
        "--no-credits",
        action="store_const",
        dest="credits",
        const=False,
        help=M.ARGPARSE_CREDITS
    )

    args = parser.parse_args()
    main(args)
