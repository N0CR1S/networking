# ============================================================
# PROJECT 13: CTF HELPER TOOLBOX
# ------------------------------------------------------------
# What it does: a menu of small tools that are handy in "Capture the
# Flag" practice challenges (picoCTF, Hack The Box...): decode and
# encode common formats, break simple ciphers, and calculate hashes.
#
# How to run:   python 13_ctf_helpers.py
# Then pick a number from the menu.
# ============================================================

import base64      # base64 encoding/decoding
import binascii    # hex <-> bytes
import codecs      # contains ROT13
import hashlib     # hash functions
import string      # ready-made lists of letters


def do_base64():
    text = input("Base64 text to decode: ")
    print("Result:", base64.b64decode(text).decode(errors="replace"))


def do_hex():
    text = input("Hex text to decode (like 48656c6c6f): ")
    print("Result:", binascii.unhexlify(text).decode(errors="replace"))


def do_rot13():
    text = input("Text for ROT13 (applying it twice gives the original): ")
    print("Result:", codecs.encode(text, "rot_13"))


def do_caesar():
    # A Caesar cipher shifts every letter by a fixed number. There are only
    # 25 possible shifts, so we simply try them all ("brute force").
    text = input("Caesar-encrypted text: ")
    for shift in range(1, 26):
        result = ""
        for ch in text:
            if ch in string.ascii_lowercase:
                # find the letter's position (0-25), move it back, wrap around with % 26
                result += string.ascii_lowercase[(string.ascii_lowercase.index(ch) - shift) % 26]
            elif ch in string.ascii_uppercase:
                result += string.ascii_uppercase[(string.ascii_uppercase.index(ch) - shift) % 26]
            else:
                result += ch                     # keep spaces and punctuation as they are
        print(f"Shift {shift:2}: {result}")


def do_xor():
    # XOR with ONE secret byte. Only 256 possible keys, so we try them all and
    # show results that look like readable text.
    text = input("Hex text encrypted with single-byte XOR: ")
    data = binascii.unhexlify(text)
    for key in range(256):
        decoded = bytes(b ^ key for b in data)   # XOR every byte with the key
        # Keep it only if every character is printable (letters, digits, punctuation, space)
        if all(32 <= c < 127 for c in decoded):
            print(f"Key {key:3}: {decoded.decode()}")


def do_hash():
    text = input("Text to hash: ")
    for name in ("md5", "sha1", "sha256"):
        # hashlib.new(name, data) creates the hash calculator by name
        print(f"{name:7}", hashlib.new(name, text.encode()).hexdigest())


def do_crack():
    # Try every word in a small list and see if its hash matches yours
    target = input("Hash to crack (md5, sha1 or sha256): ").strip().lower()
    words = ["password", "123456", "qwerty", "admin", "letmein", "welcome", "flag", "secret", "hello"]
    for word in words:
        for name in ("md5", "sha1", "sha256"):
            if hashlib.new(name, word.encode()).hexdigest() == target:
                print(f"FOUND: '{word}' ({name})")
                return
    print("Not found in the small word list. Add more words to the list in the code!")


# The menu: number -> (description, function to run)
MENU = {
    "1": ("Base64 decode", do_base64),
    "2": ("Hex decode", do_hex),
    "3": ("ROT13", do_rot13),
    "4": ("Caesar cipher brute force", do_caesar),
    "5": ("Single-byte XOR brute force", do_xor),
    "6": ("Calculate hashes", do_hash),
    "7": ("Crack a hash with a small word list", do_crack),
    "0": ("Quit", None),
}

while True:                                      # repeat until the user quits
    print("\n=== CTF Toolbox ===")
    for number, (description, function) in MENU.items():
        print(f"{number}) {description}")
    choice = input("Choose: ").strip()
    if choice == "0":
        break
    if choice in MENU:
        try:
            MENU[choice][1]()                    # run the chosen function
        except Exception as error:               # e.g. invalid base64 input
            print("Error:", error)
    else:
        print("Please type a number from the menu.")
