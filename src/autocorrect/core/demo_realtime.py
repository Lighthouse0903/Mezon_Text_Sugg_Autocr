from realtime import autocorrect_line_live

if __name__ == "__main__":
    while True:
        s = input("Bạn gõ: ").strip()
        if not s:
            break
        cleaned = autocorrect_line_live(s)
        print("→", cleaned)
