UI_TITLE = "DeviantShow"
UI_URL = "URL: "
UI_PLAY = "Play"
UI_MODE_SEQ = "1 2 3 ..."
UI_MODE_REV = "9 8 7 ..."
UI_MODE_RND = "4 7 2 ..."
UI_TIMER = "⌚"
UI_PAUSED = "Slideshow paused"
UI_ABOUT = "About"
UI_ABOUT_NAME = "DeviantShow v.0.1"
UI_ABOUT_AUTHOR = "\nA free open-source tool by:\nEric Pöhlsen"
UI_ABOUT_USE = "Slideshow tool for:"
UI_ABOUT_DA_URL = "https://www.deviantart.com"
UI_ABOUT_GITHUB = "Sourcecode and help available at:"
UI_ABOUT_GITHUB_URL = "https://www.github.com/EricPoehlsen/DeviantShow"
UI_ABOUT_CLOSE = "Close"

UI_NSFW_INFO = "This image was marked as\n" \
               "'mature content'\n" \
               "by its creator.\n\n" \
               "To display mature content start\n" \
               "DeviantShow with flag --nsfw "

UI_BUILD_GALLERY = "Generating gallery links"


RSS_BASE = "https://backend.deviantart.com/rss.xml?q="
UA_IMAGELOADER = "DeviantShow ImageLoader/0.1"
UA_RSSLOADER = "DeviantShow RSS Reader/0.1"

ERROR = "Error"
ERR_NO_CONNECTION = "Can't connect to DeviantArt ..."
ERR_INVALID_URL = "This does not look like a DeviantArt URL"
ERR_INVALID_PATH = "Specified path '{path}' is not valid "\
                   "and can't be created automatically!\n"\
                   "Please provide a valid --path argument!"

TERM_TITLE = "Terminal"

ARGPARSE_DESCRIPTION = "DeviantShow is a slide show for DeviantArt."
ARGPARSE_INTERVAL = "Display interval in seconds. Default is 10, minimum is 3."
ARGPARSE_GALLERYLIMIT = "Maximum number of RSS request. Default is 3.\n" \
"The RSS response yields a maximum of 60 gallery entries. This defines how " \
"many chunks of a larger gallery should be loaded."
ARGPARSE_NSFW = "This flag denotes that you want to recieve images marked " \
"as adult content. Please be aware that there is content on DeviantArt that " \
"might not be labeled as 'adult content' but is NSFW anyway!"
ARGPARSE_PATH = "Where to store (and look for) the images."\
"Can be a relative or absolute path"
ARGPARSE_CREDITS = "Don't display image title and creator."
