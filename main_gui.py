from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import tubo
import salas
import frf
import desempenho

class WindowManager(ScreenManager):
    pass


class MainWindow(Screen):
    pass


gui = Builder.load_file("gui.kv")


class SaguiApp(App):

    def build(self):
        return gui

if __name__ == "__main__":
    SaguiApp().run()
