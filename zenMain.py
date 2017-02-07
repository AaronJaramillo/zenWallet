from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.listview import ListView
from kivy.uix.textinput import TextInput
from kivy.graphics import Line
from kivy.garden.qrcode import QRCodeWidget
from kivy.uix.image import AsyncImage
from kivy.loader import Loader
from kivy.garden.modernmenu import ModernMenu
from kivy.uix.switch import Switch
import json
from bitcoin import *
import brainWallet as wallet
from kivy.config import Config
# golden ratio
Config.set('graphics', 'width', 309)
Config.set('graphics', 'height', 500)
Builder.load_file('zenUI.kv')

class brainWallet(Screen):
    pass
class walletScreen(Screen):
    # def wifIt(self, brain):
    #     self.ids.addy.data = str(self.brain.wifPriv)
    pass


class wifScreen(Screen):
    pass
    
class sendScreen(Screen):
    pass

class zenMain(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(brainWallet(name='hasher'))
        self.brain = wallet.BrainWallet()

        return self.sm
    def hashIt(self, brainString):
        self.brain.spinUp(brainString)
        #img = qrcode.make(str(self.brain.addr))
        self.sm.add_widget(walletScreen(name='walleter'))

        return self.sm
    def fireTX(self, payee, amount, fee):
        self.status = self.brain.spinTX(payee, amount, fee)

    def sendBitcoin(self, *args):
        print("send test")
        self.status = "pending"
        self.sm.add_widget(sendScreen(name='sender'))
        self.root.current = 'sender'
        args[0].parent.dismiss()
        #self.sm.ids.addy.data = str(self.brain.wifPriv)
        return self.sm

    def wifConfirm(self, *args):
        args[0].parent.open_submenu(
            choices=[
                dict(text='Confirm', index=1, callback=self.WIF),
            ])

    def WIF(self, *args):
        print("wif test")
        self.sm.add_widget(wifScreen(name='wiffer'))
        self.root.current = 'wiffer'
        args[0].parent.dismiss()
        #self.sm.ids.addy.data = str(self.brain.wifPriv)
        return self.sm
        

    def History(self, *args):
        self.sm.current = 'walleter'
        return self.sm

    def scanQR(self, *args):
        print("scan test")
        args[0].parent.dismiss()

    # def wif_screen(self):
    #     self.sm.add_widget(wifScreen(name='wiffer'))
    #     return self.sm

if __name__ == "__main__":
    zenMain().run()