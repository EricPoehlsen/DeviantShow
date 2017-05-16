import tkinter as tk
import tkinter.messagebox as tkmb
import requests
from urllib.request import urlopen
import os.path
from lxml import etree as et
from PIL import ImageTk, Image
import random
import messages as M

class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master=master)
        self.width = 0
        self.height = 0
        self.image_urls = []
        self.played = []
        self.current = 0
        frame = tk.Frame(self)
        self.url_bar = tk.Entry(frame)
        self.url_bar.pack(side=tk.LEFT, fill=tk.X, expand=1)
        loadbutton = tk.Button(frame, text=M.UI_LOAD, command=self.fetchGallery)
        loadbutton.pack(side=tk.LEFT)
        playbutton = tk.Button(frame, text=M.UI_PLAY, command=self.randomImage)
        playbutton.pack(side=tk.LEFT)
        frame.pack(fill=tk.X)
        self.img_canvas = tk.Canvas(
            self,
            width=300,
            height=300,
            background="#000000"
        )
        self.img_canvas.pack(fill=tk.BOTH, expand=1)
        self.master = master
        self.master.bind("<Configure>", self.resize)

    def readGallery(self, url):
        media = []
        try:
            tree = et.fromstring(requests.get(url).content)
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

    def fetchGallery(self):
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

    def nextImage(self):
        if not self.image_urls:
            return
        else:
            if self.current >= len(self.image_urls):
                self.current = 0
            self.loadImage(self.image_urls[self.current])

            self.current += 1

    def randomImage(self):
        if not self.image_urls:
            return
        else:
            indices = range(len(self.image_urls))
            unplayed = [i for i in indices if i not in self.played]
            next_index = random.choice(unplayed)
            url = self.image_urls[next_index]
            self.played.append(next_index)
            self.loadImage(url)
        self.after(10000, self.randomImage)

    def loadImage(self, url):
        filename = "downloads/" + url.split("/")[-1]
        image = None

        if os.path.isfile(filename):
            image = Image.open(filename)
        else:
            file = open(filename, mode="wb")
            content = urlopen(url).read()
            file.write(content)
            file.close()
            image = Image.open(filename)

        img_ratio = image.width / image.height
        canvas_ratio = self.width / self.height
        new_width = image.width
        new_height = self.height
        new_width = self.height * img_ratio
        if new_width > self.width:
            new_width = self.width
            new_height = new_width / img_ratio

        new_width = int(new_width)
        new_height = int(new_height)
        image = image.resize((new_width, new_height), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)

        self.img_canvas.delete(tk.ALL)
        self.img_canvas.image = None

        self.img_canvas.create_image(
            self.width / 2,
            self.height / 2,
            image=photo,
        )
        self.img_canvas.image = photo

    def resize(self, event):
        self.width = self.img_canvas.winfo_width()
        self.height = self.img_canvas.winfo_height()
        print(self.width, self.height)


def main():
    window = tk.Tk()
    app = App(window)
    app.pack(fill=tk.BOTH, expand=1)
    window.mainloop()


if __name__ == "__main__":
    main()
