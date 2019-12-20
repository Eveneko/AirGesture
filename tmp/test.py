import pyautogui


def main():
    pyautogui.sleep(5)
    pyautogui.press('enter')
    while 1:
        pyautogui.press('up')
        pyautogui.sleep(0.5)


if __name__ == '__main__':
    pyautogui.FAILSAFE = True
    main()
