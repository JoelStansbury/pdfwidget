import io

from ipywidgets import Image, HTML
from ipyevents import Event
from pdf2image import (
    convert_from_path,
    convert_from_bytes,
)


def load_pdf(fname=None , img_list=None, **kwargs):
    """
    Given an path to a pdf or a bytes object
    return the pages as a list of png byte arrays

    :type fname: str, bytes
    :param fname:  Path to the pdf or  Byte array of a pre-loaded pdf

    :type dpi: int
    :param dpi: -> Image quality in DPI

    :type fmt: str
    :param fmt: Output image format

    :type jpegopt: dict
    :param jpegopt: jpeg options (only for jpeg format)
        {
        `quality`: 0-100, 
        `progressive`: "y" OR "n",
        `optimize`: "y" OR "n"
        }
    
    first_page -> First page to process
    last_page -> Last page to process before stopping

    thread_count -> How many threads we are allowed to spawn for processing
    userpw -> PDF's password
    use_cropbox -> Use cropbox instead of mediabox
    transparent -> Output with a transparent background instead of a white one.
    poppler_path -> Path to look for poppler binaries
    grayscale -> Output grayscale image(s)
    """
    fmt = kwargs.get("fmt", "bmp")
    # convert pdf into a list of PIL images
    if isinstance(fname, str):
        pil_imgs = convert_from_path(fname, **kwargs) 
    elif isinstance(fname, bytes):
        pil_imgs = convert_from_bytes(fname, **kwargs)
    else:
        raise(ValueError(f"Unsuported type: {type(fname)}"))

    pages = []
    for i in pil_imgs:
        imgByteArr = io.BytesIO()
        i.save(imgByteArr, format=fmt)
        pages.append(imgByteArr.getvalue())
    return pages, pil_imgs


class PdfViewer(Image):
    def __init__(self, fname=None, page_nav="click", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.msg = HTML()

        if fname:
            self.load(fname, *args, **kwargs)
    
        paging_opts = {
            "click": self.construct_click_handler,
            "arrows": self.construct_arrow_handler
        }

        # Run the selected event constructor
        paging_opts[page_nav]()

    def construct_click_handler(self):
        """ Should only be run once """
        disp_events = Event(
            source=self, 
            watched_events=['click']
        )
        
        def handle_disp(event):
            if event["type"] == "click":
                x = self.images[self.page_index]._size[0]
                if event["relativeX"] > (x/2):
                    self.next_page()
                elif event["relativeX"] < (x/2):
                    self.previous_page()
        
        disp_events.on_dom_event(handle_disp)


    def construct_arrow_handler(self):
        """ Should only be run once """
        disp_events = Event(
            source=self, 
            watched_events=['keydown']
        )
        
        def handle_disp(event):
            if event["type"] == "keydown":
                self.key_funcs[event["key"]]()

        disp_events.on_dom_event(handle_disp)


    def load(self, fname, *args, **kwargs):
        self.page_index = 0
        self.pages, self.images = load_pdf(fname, *args, **kwargs)
        self.value = self.pages[0]
        self.key_funcs = {
            "ArrowLeft": self.previous_page, 
            "ArrowRight": self.next_page,
        }


    def previous_page(self):
        """
        Displays the previous page
        """
        self.page_index = max( 
            0,
            self.page_index - 1
        )
        self.value = self.pages[self.page_index]


    def next_page(self):
        """
        Displays the next page
        """
        self.page_index = min( 
            len(self.pages) - 1,
            self.page_index + 1
        )
        self.value = self.pages[self.page_index]