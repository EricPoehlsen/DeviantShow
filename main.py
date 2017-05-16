import tkinter as tk
import tkinter.messagebox as tkmb
import requests
from urllib.request import Request, build_opener
import os.path
from lxml import etree as et
from PIL import ImageTk, Image
import random
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
        self.image_urls = []
        self.played = []
        self.current = 0
        self.interval = 10000
        self.timer = None
        self.mode = "rand"

        self.config(background="#000000")

        # creating the menu bar
        self.menuframe = tk.Frame(self)
        self.url_bar = tk.Entry(self.menuframe)
        self.url_bar.pack(side=tk.LEFT, fill=tk.X, expand=1)
        loadbutton = tk.Button(
            self.menuframe,
            text=M.UI_LOAD,
            command=self.fetchGallery
        )
        loadbutton.pack(side=tk.LEFT)
        playbutton = tk.Button(
            self.menuframe,
            text=M.UI_PLAY,
            command=self.randomImage
        )
        playbutton.pack(side=tk.LEFT)
        self.menuframe.pack(fill=tk.X)

        # this is the canvas
        self.img_canvas = tk.Canvas(
            self,
            width=300,
            height=300,
            background="#000000"
        )
        self.img_canvas.pack(fill=tk.BOTH, expand=1)

        # the main tk instance
        self.master = master
        self.master.title(M.UI_TITLE)
        self.master.bind("<Configure>", self.resize)
        self.master.bind("<F12>", self.panicMode)
        self.master.bind("<Right>", self.showNext)
        self.master.bind("<Left>", self.showPrevious)

    def fetchGallery(self):
        """ read the given url and get the appropriate rss """

        url = self.url_bar.get()
        if url:
            try:
                if "deviantart.com" not in url:
                    raise ValueError
                url = url.split("//")[-1]
                elements = url.split("/")

                user = elements[0].split(".")[0]
                variant = elements[1]
                if variant == "favourites":
                    variant = "favby"
                rss = "https://backend.deviantart.com/rss.xml?q={variant}%3A{user}".format(
                    variant=variant,
                    user=user
                )
                if len(elements) > 2:
                    rss += "/" + elements[2]
            except ValueError:
                error = tkmb.showerror(
                    title=M.ERROR,
                    message=M.ERR_INVALID_URL,
                    master=self
                )
                self.image_urls = []
                return

            self.image_urls = self.readGallery(rss)
            self.played = []
            print(len(self.image_urls))

    def readGallery(self, url):
        """ retrieves the image urls (and metadata) from the rss 

        Args: 
            url (str): the rss url to access
        """

        media = []
        headers = requests.utils.default_headers()
        headers.update({"User-Agent": M.UA_RSSLOADER})
        try:
            tree = et.fromstring(requests.get(url, headers=headers).content)
            media = tree.findall(".//media:content", tree.nsmap)
        except requests.ConnectionError:
            error = tkmb.showerror(
                title=M.ERROR,
                message=M.ERR_NO_CONNECTION,
                master=self
            )
        link_list = []
        for item in media:
            link_list.append(item.get("url"))
        return link_list

    def nextImage(self):
        """ Display next image in sequential mode """
        if not self.image_urls:
            return
        else:
            if self.current >= len(self.image_urls):
                self.current = 0
            self.loadImage(self.image_urls[self.current])
            self.current += 1
            self.timer = self.after(self.interval, self.randomImage)

    def randomImage(self, next_index=None):
        """ Display next image in random mode 
        
        Args:
            next_index (int): integer of the next image to display
                              [Only used for going back]
        """

        if not self.image_urls:
            return
        else:
            indices = range(len(self.image_urls))
            unplayed = [i for i in indices if i not in self.played]
            if not next_index:
                next_index = random.choice(unplayed)
            url = self.image_urls[next_index]
            self.played.append(next_index)
            print(self.played)
            self.loadImage(url)

        self.timer = self.after(self.interval, self.randomImage)

    def loadImage(self, url):
        """ this retrieves the actual image and displays it on the canvas
        
        Args: 
            url (str): the image url 
        """

        # create local filename
        filename = "downloads/" + url.split("/")[-1]
        image = None

        # load locally stored image from disk or retrieve from web
        if os.path.isfile(filename):
            image = Image.open(filename)
        else:
            file = open(filename, mode="wb")
            request = Request(url)
            request.add_header("User-Agent", M.UA_IMAGELOADER)
            opener = build_opener()
            content = opener.open(request).read()

            file.write(content)
            file.close()
            image = Image.open(filename)

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

        # remove last image
        self.img_canvas.delete(tk.ALL)
        self.img_canvas.image = None

        # draw current image
        self.img_canvas.create_image(
            self.width / 2,
            self.height / 2,
            image=photo,
        )
        self.img_canvas.image = photo

    def showNext(self, event):
        """ Cancel timer - go to next image """

        self.after_cancel(self.timer)
        if self.mode == "rand":
            self.randomImage()
        else:
            self.nextImage()

    def showPrevious(self, event):
        """ Cancel image - go to previous image """
        self.after_cancel(self.timer)
        if self.mode == "rand":
            next_index = 0
            if len(self.played) > 1:
                next_index = self.played[-2]
                self.played = self.played[0:-2]
            print(next_index)
            self.randomImage(next_index=next_index)
        else:
            if self.current > 0:
                self.current -= 1
            self.nextImage()

    def resize(self, event):
        """ Event handler tracking the available canvas size"""
        self.width = self.img_canvas.winfo_width()
        self.height = self.img_canvas.winfo_height()
        print(self.width, self.height)

    def panicMode(self, event):
        import os
        prompt = "{user}@{host}:~$ ".format(
            user=os.getenv("USERNAME", "user"),
            host=os.getenv("USERDOMAIN", "SYSTEM")
        )

        self.master.title(M.NSA_TITLE)
        self.master.minsize(500, 350)
        self.menuframe.pack_forget()
        if self.timer:
            self.after_cancel(self.timer)
        self.img_canvas.pack_forget()
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
        label.pack(anchor=tk.NW)

        self.after(500, self.panicSwitch, var)

    def panicSwitch(self, var):
        prompt = var.get()
        if prompt.endswith("█"):
            var.set(prompt[:-1])
        else:
            var.set(prompt + "█")
        self.after(500, self.panicSwitch, var)


def main():
    window = tk.Tk()
    app = App(window)
    app.pack(fill=tk.BOTH, expand=1)
    window.mainloop()


if __name__ == "__main__":
    main()
