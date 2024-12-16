from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from pyzbar import pyzbar
import cv2

from kivy.graphics import Color, Rectangle


class ColoredLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            # Set the background color (RGBA)
            Color(0.5, 0.5, 0.5, 1)  # Grey color
            self.rect = Rectangle(size=self.size, pos=self.pos)

        # Bind the size and position to update the rectangle
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class MainScreen(Screen):
    # first screen that is displayed when program is run
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.box: BoxLayout = BoxLayout()
        self.box.orientation = "vertical"  # vertical placing of widgets
        self.output_text: str = "Hello I am a label"

        self.togglflag: bool = True
        self.cam = cv2.VideoCapture(0)  # start OpenCV camera
        self.cam.set(3, 1280)  # set resolution of camera
        self.img = Image()
        self.output_lbl: ColoredLabel = ColoredLabel(
            text=self.output_text,
            size_hint=(1, 0.2),
            font_size="45dp",
            halign="center",  # Center horizontally
            valign="middle",  # Center vertically
        )
        self.output_lbl.text_size = (None, 200)
        self.output_lbl.pos_hint == {"center_x": 0.5, "center_y": 0.5}

        # Set text size to label size
        # create Toggle Button for pause and play of video stream
        self.tog_btn = ToggleButton(
            text="Pause",
            group="camstart",
            state="down",
            size_hint_y=None,
            height="48dp",
            on_press=self.change_state,
        )
        self.but = Button(
            text="Stop", size_hint_y=None, height="48dp", on_press=self.stop_stream
        )
        self.box.add_widget(self.output_lbl)
        self.box.add_widget(self.img)
        self.box.add_widget(self.tog_btn)
        self.box.add_widget(self.but)
        self.add_widget(self.box)
        Clock.schedule_interval(self.update, 1.0 / 30)  # update for 30fps

    # update frame of OpenCV camera
    def update(self, dt):
        if self.togglflag:
            ret, frame = self.cam.read()  # retrieve frames from OpenCV camera

            if ret:
                buf1 = cv2.flip(src=frame, flipCode=0)  # convert it into texture
                buf: bytes = buf1.tobytes()
                image_texture: Texture = Texture.create(
                    size=(frame.shape[1], frame.shape[0]),
                    colorfmt="bgr",
                )
                image_texture.blit_buffer(
                    buf,
                    colorfmt="bgr",
                    bufferfmt="ubyte",
                )

                self.img.texture = image_texture  # display image from the texture
                ret, bw_im = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)

                barcodes: list[pyzbar.Decoded] = pyzbar.decode(image=bw_im)
                barcode: pyzbar.Decoded
                for barcode in barcodes:
                    if len(barcode) >= 1:
                        decoded_data: bytes = barcode.data
                        self.output_text: str = decoded_data.decode("utf-8")

                        print("qr scan result:")
                        print(f"{self.output_text}")
                        self.output_lbl.text = self.output_text

                        self.output_lbl.text_size = (
                            self.output_lbl.size
                        )  # Update text_size
                        self.output_lbl.texture_update()  # Update texture for auto-sizing
                        # rect=barcode.rect

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    cv2.destroyAllWindows()
                    exit(0)

    # change state of toggle button
    def change_state(self, *args):
        if self.togglflag:
            self.tog_btn.text = "Play"
            self.togglflag = False
        else:
            self.tog_btn.text = "Pause"
            self.togglflag = True

    def stop_stream(self, *args):
        self.cam.release()  # stop camera

    def change_screen(self, *args):
        self.stop_stream()
        main_app.sm.current = (
            "second"  # once barcode is detected, switch to second screen
        )


class QR_Code_Scanner_App(App):
    def build(self):
        self.sm: ScreenManager = (
            ScreenManager()
        )  # screenmanager is used to manage screens
        self.mainsc: MainScreen = MainScreen()
        scrn: Screen = Screen(name="main")
        scrn.add_widget(self.mainsc)
        self.sm.add_widget(scrn)
        return self.sm


if __name__ == "__main__":
    main_app: QR_Code_Scanner_App = QR_Code_Scanner_App()
    main_app.run()
