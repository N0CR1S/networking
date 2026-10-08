# ============================================================
# PROJECT 7: PASSWORD STRENGTH CHECKER
# ------------------------------------------------------------
# What it does:
#   1. Estimates how strong a password is (entropy = "how many
#      guesses would be needed", measured in bits).
#   2. Warns about weak patterns (too short, common words...).
#   3. Checks if the password appeared in known data leaks, using
#      the "Have I Been Pwned" service. Your full password is NEVER
#      sent: only the first 5 characters of its hash (k-anonymity).
#
# How to run:   python 07_password_checker.py
# (The typed password is hidden while you type.)
# ============================================================

import getpass     # asks for input without showing it on screen
import hashlib     # hash functions (SHA-1)
import math        # for the logarithm in the entropy formula
import urllib.request   # to talk to the Have I Been Pwned web service

# A tiny list of very common passwords (real attackers use millions)
COMMON = ["password", "123456", "qwerty", "letmein", "admin", "welcome", "iloveyou", "abc123"]


def entropy_bits(password):
    """Estimate strength in bits. More bits = harder to guess."""
    pool = 0                                   # how many different characters could be used
    if any(c.islower() for c in password):     # contains a lowercase letter?
        pool += 26
    if any(c.isupper() for c in password):     # contains an uppercase letter?
        pool += 26
    if any(c.isdigit() for c in password):     # contains a digit?
        pool += 10
    if any(not c.isalnum() for c in password): # contains a symbol like ! or #?
        pool += 32
    if pool == 0:
        return 0
    # Formula: length * log2(pool size)
    return len(password) * math.log2(pool)


def check_leaks(password):
    """Ask Have I Been Pwned how often this password appeared in leaks."""
    # Hash the password with SHA-1 and write it in capital letters
    sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix = sha1[:5]          # first 5 characters: this is all we send
    suffix = sha1[5:]          # the rest stays on our computer
    url = "https://api.pwnedpasswords.com/range/" + prefix
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            text = response.read().decode()   # a long list of "SUFFIX:COUNT" lines
    except Exception as error:
        print("Could not reach the leak database:", error)
        return None
    # Look through the returned lines for our own suffix
    for line in text.splitlines():
        line_suffix, count = line.split(":")
        if line_suffix == suffix:
            return int(count)  # found! This is how often it was leaked
    return 0                   # not found = good


password = getpass.getpass("Enter a password to test: ")

print("\n--- Results ---")
bits = entropy_bits(password)
print(f"Length: {len(password)} characters")
print(f"Estimated strength: {bits:.0f} bits")

# Turn the number into a simple verdict
if bits < 40:
    print("Verdict: WEAK")
elif bits < 60:
    print("Verdict: OK, but could be better")
else:
    print("Verdict: STRONG")

# Extra warnings
if len(password) < 12:
    print("Warning: use at least 12 characters.")
if password.lower() in COMMON:
    print("Warning: this is one of the most common passwords!")
if password.isdigit():
    print("Warning: only digits is very easy to guess.")

leaks = check_leaks(password)
if leaks is None:
    pass                                       # error was already printed
elif leaks > 0:
    print(f"DANGER: this password appeared {leaks} times in data leaks. Do not use it!")
else:
    print("Good: this password was not found in known leaks.")
