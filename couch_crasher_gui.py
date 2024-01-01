"""
Sample GUI for CouchCrasher
"""

import wx
import logging
import platform
import threading
import couchcrasher


class CouchCrasherGUI(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(CouchCrasherGUI, self).__init__(*args, **kwargs)

        self.cc_obj: couchcrasher.CouchCrasher = None

        self._header:          wx.StaticText = None
        self._label:           wx.StaticText = None
        self._method_dropdown: wx.Choice = None
        self._payload_button:  wx.Button = None
        self._exploit:         wx.Button = None

        self._font_title_size:       int = 18
        self._font_label_size:       int = 13
        self._last_element_position: int = 60

        if platform.system() == "Linux":
            self._font_title_size = 11
            self._font_label_size = 10

        if platform.system() != "Darwin":
            self._last_element_position += 10

        self.init_couchcrasher()
        self.init_ui()


    def init_couchcrasher(self):
        self.cc_obj = couchcrasher.CouchCrasher(None)


    def update_methods(self, event: wx.Event):
        item = event.GetEventObject().GetStringSelection()
        self.cc_obj.change_custom_method(item)


    def run_couchcrasher(self, event: wx.Event):
        # Create a modal dialog
        frame = wx.Dialog(self, title="Couch Crasher", size=(500, 380))
        frame.Centre()

        # Textbox for output
        output = wx.TextCtrl(frame, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_AUTO_URL)
        output.SetPosition((-1, 10))
        output.SetSize((480, 300))
        output.Centre(wx.HORIZONTAL)

        # Button to close dialog
        close_button = wx.Button(frame, label="Close", pos=(10, 320))
        close_button.Bind(wx.EVT_BUTTON, lambda event: frame.Close())
        close_button.Centre(wx.HORIZONTAL)

        # Set Window height to bottom of last element
        frame.SetSize((-1, close_button.GetPosition()[1] + self._last_element_position))

        # Add new logging handler to output to the textbox
        handler = ThreadHandler(output)
        logging.getLogger().addHandler(handler)

        frame.ShowWindowModal() if platform.system() == "Darwin" else frame.Show()

        thread = threading.Thread(target=self.cc_obj.install)
        thread.start()

        while thread.is_alive():
            wx.Yield()

        logging.getLogger().removeHandler(handler)


    def select_payload(self, event):
        with wx.FileDialog(self, "Select Payload", wildcard="All files (*.*)|*.*", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            self.cc_obj.change_payload(fileDialog.GetPath())
            self._exploit.Enable()
            self._payload_button.SetLabel(fileDialog.GetFilename())


    def set_background_color(self):
        if platform.system() != "Windows":
            return

        self.SetBackgroundColour(wx.Colour(240, 240, 240))


    def init_ui(self):
        self.SetTitle("Couch Crasher")
        self.SetSize((400, 200))
        self.Centre()

        self.set_background_color()

        # Label: header
        self._header = wx.StaticText(self, label=f"Couch Crasher v{couchcrasher.__version__}", pos=(10, 10), size=(180, -1))
        self._header.SetFont(wx.Font(self._font_title_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self._header.Centre(wx.HORIZONTAL)

        # Label: payload
        self._label = wx.StaticText(self, label="Payload", pos=(10, 10))
        self._label.SetFont(wx.Font(self._font_label_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self._label.SetPosition((-1, self._header.GetPosition()[1] + 30))
        self._label.Centre(wx.HORIZONTAL)

        # Button that reveals Finder window for user to select payload
        self._payload_button = wx.Button(self, label="None configured", pos=(10, 10))
        self._payload_button.SetPosition((-1, self._label.GetPosition()[1] + 20))
        self._payload_button.Centre(wx.HORIZONTAL)
        self._payload_button.Bind(wx.EVT_BUTTON, self.select_payload)

        # Choice: methods
        self._label = wx.StaticText(self, label="Persistence Method", pos=(10, 10))
        self._label.SetFont(wx.Font(self._font_label_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self._label.SetPosition((-1, self._payload_button.GetPosition()[1] + 30))
        self._label.Centre(wx.HORIZONTAL)

        supported_methods: list = self.cc_obj.supported_persistence_methods()

        self._method_dropdown = wx.Choice(self, pos=(10, 30), choices=supported_methods)
        self._method_dropdown.SetFont(wx.Font(self._font_label_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self._method_dropdown.SetPosition((-1, self._label.GetPosition()[1] + 20))
        self._method_dropdown.Centre(wx.HORIZONTAL)
        self._method_dropdown.Bind(wx.EVT_CHOICE, self.update_methods)

        recommended_method: str = self.cc_obj.recommended_persistence_method()
        try:
            self._method_dropdown.SetSelection(supported_methods.index(recommended_method))
        except ValueError:
            pass

        # wxButton: exploit
        self._exploit = wx.Button(self, label="Exploit", pos=(10, 60))
        self._exploit.SetPosition((-1, self._method_dropdown.GetPosition()[1] + 30))
        self._exploit.Bind(wx.EVT_BUTTON, self.run_couchcrasher)
        self._exploit.Centre(wx.HORIZONTAL)
        self._exploit.Disable()

        # Set Window height to bottom of last element
        self.SetSize((-1, self._exploit.GetPosition()[1] + self._last_element_position))

        self.Show(True)


class ThreadHandler(logging.Handler):
    """
    Reroutes logging output to a wx.TextCtrl using UI callbacks
    """

    def __init__(self, text_box: wx.TextCtrl):
        logging.Handler.__init__(self)
        self.text_box = text_box


    def emit(self, record: logging.LogRecord):
        wx.CallAfter(self.text_box.AppendText, self.format(record) + '\n')


def main():
    app = wx.App()
    CouchCrasherGUI(None, style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
    app.MainLoop()

if __name__ == '__main__':
    main()