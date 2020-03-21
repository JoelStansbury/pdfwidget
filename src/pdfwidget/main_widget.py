import io

from ipywidgets import Image
from ipyevents import Event
from pdf2image import (
    convert_from_path,
    convert_from_bytes,
)


def load_pdf(fname, dpi=None, **kwargs):
    """
    Given an path to a pdf or a bytes object
    return the pages as a list of png byte arrays

    :type fname: str, bytes
    :param fname: Path to the pdf, or a Byte array of a pre-loaded pdf

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
    if not dpi is None:
        kwargs["dpi"] = dpi
    if isinstance(fname, str):
        pil_imgs = convert_from_path(fname, **kwargs) 
    elif isinstance(fname, bytes):
        pil_imgs = convert_from_bytes(fname, **kwargs) 

    pages = []
    for i in pil_imgs:
        imgByteArr = io.BytesIO()
        i.save(imgByteArr, format=fmt)
        pages.append(imgByteArr.getvalue())
    return pages


class PdfViewer(Image):
    def __init__(self, fname, dpi, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page_index = 0
        self.pages = load_pdf(fname, dpi, *args, **kwargs)
        self.value = self.pages[0]
        
        # Event Handlers
        disp_events = Event(
            source=self, 
            watched_events=['click', 'keydown', 'mouseenter']
        )

        key_funcs = {
            "ArrowLeft": self.previous_page, 
            "ArrowRight": self.next_page,
        }
        
        def handle_disp(event):
            if event["type"] == "keydown":
                key_funcs[event["key"]]()

        disp_events.on_dom_event(handle_disp)


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