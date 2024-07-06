import pyautogui
from PIL import ImageGrab
import keyboard
import time

# Warna target dalam format RGB
target_rgb_color = (194, 220, 0)

def find_pixel_and_click(target_rgb_color):
    # Ambil screenshot layar
    screenshot = ImageGrab.grab()
    width, height = screenshot.size

    # Loop melalui setiap piksel dalam screenshot
    for x in range(width):
        for y in range(height):
            # Dapatkan warna piksel
            if screenshot.getpixel((x, y))[:3] == target_rgb_color:
                # Klik pada koordinat (x, y) jika warna cocok
                pyautogui.click(x, y)
                return

def main():
    print("Menjalankan autoklik. Tekan '1' untuk berhenti.")
    while True:
        if keyboard.is_pressed('1'):
            print("Dihentikan oleh pengguna.")
            break
        find_pixel_and_click(target_rgb_color)
        time.sleep(0.1)  # Mengatur interval klik agar tidak terlalu cepat

if __name__ == "__main__":
    main()
