import argparse
import tkinter as tk
import tkinter.messagebox as tkmb
import requests
from urllib.request import Request, build_opener
import os.path
from lxml import etree as et
from PIL import ImageTk, Image
import random
import webbrowser
import messages as M


"""
Next steps ...

* adding
"""


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
        self.gallery_limit = 4
        self.interval = 10000
        self.mode = "sequential"
        self.interval_var = tk.StringVar()
        self.timer = None
        self.nsfw = False

        self.config(background="#000000")
        self.columnconfigure(0, weight=100)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=100)

        # creating the menu bar
        self.menuframe = tk.Frame(self)
        self.url_bar = tk.Entry(self.menuframe)
        self.url_bar.pack(side=tk.LEFT, fill=tk.X, expand=1)
        play_button = tk.Button(
            self.menuframe,
            text=M.UI_PLAY,
            command=self.fetchGallery
        )
        play_button.pack(side=tk.LEFT)

        mode_label=tk.Label(
            self.menuframe,
            text=M.UI_MODE
        )
        mode_label.pack(side=tk.LEFT)
        self.mode_button = tk.Button(
            self.menuframe,
            text=M.UI_MODE_SEQ,
            command=self.nextMode
        )
        self.mode_button.pack(side=tk.LEFT)
        interval_entry = tk.Entry(
            self.menuframe,
            width=4,
            textvariable=self.interval_var
        )
        interval_entry.pack(side=tk.LEFT)
        self.interval_var.set(str(self.interval // 1000))
        self.interval_var.trace("w", lambda n, e, m: self.intervalChanged())

        self.menuframe.grid(row=0, column=0, sticky=tk.NSEW)

        # this is the canvas
        self.img_canvas = tk.Canvas(
            self,
            width=300,
            height=300,
            background="#000000",
            borderwidth=0,
            highlightthickness=0
        )
        self.img_canvas.bind("<Button-1>", self.visitDA)
        self.img_canvas.grid(row=1, column=0, sticky=tk.NSEW)

        # the main tk instance
        self.master = master
        self.master.title(M.UI_TITLE)
        self.master.bind("<Configure>", self.resize)
        self.master.bind("<F12>", self.panicMode)
        self.master.bind("<Right>", self.showNext)
        self.master.bind("<Left>", self.showPrevious)
        self.master.bind("<F11>", self.toggleFullScreen)

    def fetchGallery(self):
        """ read the given url and get the appropriate rss """

        url = self.url_bar.get()
        # do not reload the same gallery
        if url == self.gallery_url:
            print("already loaded ...")
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
            print(len(elements))
            user = elements[0].split(".")[0]
            variant = elements[1]
            if variant == "favourites":
                variant = "favby"
            rss = M.RSS_BASE + variant + ":" + user
            if len(elements) > 3:
                rss += "/" + elements[2]

        print(rss)
        self.image_data = self.readGallery(rss, arguments)
        self.playlist = list(range(len(self.image_data)))
        print(len(self.playlist))

        # start
        self.nextImage()

    def readGallery(self, url, arguments):
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

        print ("Start @:", offset)
        for iteration in range(self.gallery_limit):
            rss_url = url + "&offset="+str(offset)
            try:
                rss_feed = requests.get(rss_url, headers=headers)
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

            except requests.ConnectionError:
                error = tkmb.showerror(
                    title=M.ERROR,
                    message=M.ERR_NO_CONNECTION,
                    master=self
                )

            print("This round:", i)

            if i < 59:
                break

            offset += i

        return media_info

    def nextImage(self):
        """ Display next image in the playlist """
        if not self.image_data:
            return
        else:
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

        # create local filename
        img_url = resource_data["img_url"]
        filename = "downloads/" + img_url.split("/")[-1]
        image = None

        # load locally stored image from disk or retrieve from web
        if self.nsfw is False and resource_data["rating"] == "adult":
            pass
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

        if image is None:
            # add credits ...
            self.img_canvas.create_text(
                int(self.width/2),
                int(self.height/2),
                text=M.UI_NSFW_INFO,
                fill="#ff0000"
            )

        else:
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

        # add credits ...
        self.img_canvas.create_text(
            2, 2,
            text=resource_data["title"] + " by " + resource_data["author"],
            anchor=tk.NW,
            fill="#cccccc"
        )

        # page numbers ...
        image_num = str(self.playlist[self.current] + 1)
        total_num = str(len(self.playlist))
        self.img_canvas.create_text(
            self.width - 2,
            self.height - 2,
            text=image_num + " / " + total_num,
            anchor=tk.SE,
            fill="#cccccc"
        )


    def showNext(self, event):
        """ Cancel timer - go to next image in playlist """
        self.after_cancel(self.timer)
        self.nextImage()

    def showPrevious(self, event):
        """ Cancel timer - go to previous image in playlist """
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
            current = self.playlist[self.current]
            self.playlist.sort()
            self.playlist.reverse()
            self.current = self.playlist.index(current)

    def intervalChanged(self):
        try:
            interval_text = self.interval_var.get()

            interval_float = float(interval_text)
            if interval_float < 3:
                self.interval = 3000
            else:
                self.interval = int(1000 * interval_float)
        except ValueError:
            pass

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
    app.gallery_limit = args.limit
    app.interval = args.interval * 1000
    app.interval_var.set(str(args.interval))
    app.nsfw = args.nsfw
    app.pack(fill=tk.BOTH, expand=1)
    window.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=M.ARGPARSE_DESCRIPTION)
    parser.add_argument(
        "-i", "--interval",
        type=int,
        default=10,
        help=M.ARGPARSE_INTERVAL)
    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=4,
        help=M.ARGPARSE_GALLERYLIMIT)
    parser.add_argument(
        "--nsfw",
        action="store_true",
        help=M.ARGPARSE_NSFW
    )

    args = parser.parse_args()
    main(args)
