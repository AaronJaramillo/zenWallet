#from qrcodewidget import QRCodeWidget
#
#Ideally this code would be imported using the above command
#and this file would only have the import, unfortuantly for some reason this is bugging and throws  ImportError: No module named 'qrcodewidget' hopefully some one can fix this
#
#I've left the qrcodewidget.py as a copy of this file
#the widget runs from this file though. 
#
# 
''' Kivy Widget that accepts data and displays qrcode
'''

from threading import Thread
from functools import partial

from kivy.uix.floatlayout import FloatLayout

from kivy.graphics.texture import Texture
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty, StringProperty, ListProperty,\
    BooleanProperty
from kivy.lang import Builder
from kivy.clock import Clock
import qrcode
try:
    import qrcode
except ImportError:
    sys.exit("Error: qrcode does not seem to be installed." +\
             "Try 'sudo pip install qrcode'")



Builder.load_string('''
<QRCodeWidget>
    on_parent: if args[1]: qrimage.source = self.loading_image
    canvas.before:
        # Draw white Rectangle
        Color:
            rgba: root.background_color
        Rectangle:
            size: self.size
            pos: self.pos
    canvas.after:
        Color:
            rgba: .5, .5, .5, 1 if root.show_border else 0
        Line:
            width: dp(1.333)
            points:
                dp(2), dp(2),\
                self.width - dp(2), dp(2),\
                self.width - dp(2), self.height - dp(2),\
                dp(2), self.height - dp(2),\
                dp(2), dp(2)
    Image
        id: qrimage
        pos_hint: {'center_x': .5, 'center_y': .5}
        allow_stretch: True
        size_hint: None, None
        size: root.width * .9, root.height * .9
''')

class QRCodeWidget(FloatLayout):

    show_border = BooleanProperty(True)
    '''Whether to show border around the widget.

    :data:`show_border` is a :class:`~kivy.properties.BooleanProperty`,
    defaulting to `True`.
    '''

    data = StringProperty(None, allow_none=True)
    ''' Data using which the qrcode is generated.

    :data:`data` is a :class:`~kivy.properties.StringProperty`, defaulting to
    `None`.
    '''

    background_color = ListProperty((1, 1, 1, 1))
    ''' Background color of the background of the widget to be displayed
    behind the qrcode.

    :data:`background_color` is a :class:`~kivy.properties.ListProperty`,
    defaulting to `(1, 1, 1, 1)`.
    '''

    loading_image = StringProperty('data/images/image-loading.gif')
    '''Intermediate image to be displayed while the widget ios being loaded.
    
    :data:`loading_image` is a :class:`~kivy.properties.StringProperty`,
    defaulting to `'data/images/image-loading.gif'`.
    '''

    def __init__(self, **kwargs):
        super(QRCodeWidget, self).__init__(**kwargs)
        self.addr = None
        self.qr = None
        self._qrtexture = None

    def on_data(self, instance, value):
        if not (self.canvas or value):
            return
        img = self.ids.get('qrimage', None)

        if not img:
            # if texture hasn't yet been created delay the texture updation
            Clock.schedule_once(lambda dt: self.on_data(instance, value))
            return
        img.anim_delay = .25
        img.source = self.loading_image
        Thread(target=partial(self.generate_qr, value)).start()

    def generate_qr(self, value):
        self.set_addr(value)
        self.update_qr()

    def set_addr(self, addr):
        if self.addr == addr:
            return
        MinSize = 210 if len(addr) < 128 else 500
        self.setMinimumSize((MinSize, MinSize))
        self.addr = addr
        self.qr = None

    def update_qr(self):
        if not self.addr and self.qr:
            return
        QRCode = qrcode.QRCode
        L = qrcode.constants.ERROR_CORRECT_L
        addr = self.addr
        try:
            self.qr = qr = QRCode(
                version=None,
                error_correction=L,
                box_size=10,
                border=0,
                )
            qr.add_data(addr)
            qr.make(fit=True)
        except Exception as e:
            print(e)
            self.qr=None
        self.update_texture()

    def setMinimumSize(self, size):
        # currently unused, do we need this?
        self._texture_size = size

    def _create_texture(self, k, dt):
        self._qrtexture = texture = Texture.create(size=(k,k), colorfmt='rgb')
        # don't interpolate texture
        texture.min_filter = 'nearest'
        texture.mag_filter = 'nearest'

    def update_texture(self):
        if not self.addr:
            return

        matrix = self.qr.get_matrix()
        k = len(matrix)
        
        # create the texture in main UI thread otherwise
        # this will lead to memory corruption
        Clock.schedule_once(partial(self._create_texture, k), -1)
        
        
        cr, cg, cb, ca = self.background_color[:]
        cr, cg, cb = cr*255, cg*255, cb*255
        ###used bytearray for python 3.5 eliminates need for btext
        buff = bytearray()
        for r in range(k):
            for c in range(k):
                buff.extend([0, 0, 0] if matrix[r][c] else [cr, cg, cb])

        # then blit the buffer
        # join not neccesarry when using a byte array 
        # buff =''.join(map(chr, buff))
        # update texture in UI thread.
        Clock.schedule_once(lambda dt: self._upd_texture(buff))

    def _upd_texture(self, buff):
        texture = self._qrtexture
        if not texture:
            # if texture hasn't yet been created delay the texture updation
            Clock.schedule_once(lambda dt: self._upd_texture(buff))
            return
        
        texture.blit_buffer(buff, colorfmt='rgb', bufferfmt='ubyte')
        texture.flip_vertical()
        img = self.ids.qrimage
        img.anim_delay = -1
        img.texture = texture
        img.canvas.ask_update()

if __name__ == '__main__':
    from kivy.app import runTouchApp
    import sys
    data = str(sys.argv[1:])
    runTouchApp(QRCodeWidget(data=data))
