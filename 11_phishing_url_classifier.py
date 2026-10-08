# ============================================================
# PROJECT 11: PHISHING URL CLASSIFIER (machine learning, beginner version)
# ------------------------------------------------------------
# What it does: teaches a small machine-learning model to tell
# "safe" web addresses from "phishing" (fake, scam) ones, by
# looking at simple features like length, number of dots, "@" etc.
#
# IMPORTANT: the training list below is TINY, made-up, and only for
# learning how it works. For real use, train on a public dataset
# (for example PhishTank or a "phishing URLs" CSV on Kaggle) with
# thousands of rows. Replace the two lists with data from that file.
#
# Setup:  pip install scikit-learn
# Run:    python 11_phishing_url_classifier.py
#         python 11_phishing_url_classifier.py http://paypa1-login.example.xyz/verify
# ============================================================

import sys
from sklearn.ensemble import RandomForestClassifier   # the learning algorithm

# Training examples. 0 = safe, 1 = phishing.
SAFE = [
    "https://www.google.com/search?q=python",
    "https://github.com/python/cpython",
    "https://en.wikipedia.org/wiki/Computer",
    "https://www.amazon.com/books",
    "https://www.bbc.com/news",
    "https://stackoverflow.com/questions",
    "https://www.paypal.com/signin",
    "https://www.microsoft.com/en-us",
]
PHISHING = [
    "http://paypa1-secure-login.verify-account.xyz/signin",
    "http://192.168.4.55/bank/login.php",
    "http://secure-update-microsoft.com.account-check.top/confirm",
    "http://amazon.com@evil-site.ru/login",
    "http://login-facebook-verify.free-gift-now.club/id=123456",
    "http://www.g00gle-security-alert.info/update-password-now",
    "http://bit.ly.confirm-your-bank-details.tk/a/b/c/d",
    "http://apple-id-locked.support-center-help.xyz/unlock",
]


def features(url):
    """Turn a URL into a list of numbers the model can learn from."""
    return [
        len(url),                                        # long URLs are suspicious
        url.count("."),                                  # many dots = many sub-domains
        url.count("-"),                                  # lots of hyphens
        url.count("/"),                                  # deep paths
        1 if "@" in url else 0,                          # "@" can hide the real site
        1 if url.startswith("https") else 0,             # https (not a guarantee, but a hint)
        1 if url.split("/")[2].replace(".", "").isdigit() else 0,   # raw IP address instead of a name
        sum(c.isdigit() for c in url),                   # number of digits
        1 if any(w in url.lower() for w in ("login", "verify", "secure", "update", "confirm")) else 0,
        1 if url.split("/")[2].endswith((".xyz", ".top", ".tk", ".club", ".ru")) else 0,   # cheap domains
    ]


# Build the training data: X = features, y = the correct answers (labels)
X = [features(u) for u in SAFE + PHISHING]
y = [0] * len(SAFE) + [1] * len(PHISHING)

model = RandomForestClassifier(n_estimators=50, random_state=1)   # a group of 50 decision trees
model.fit(X, y)                                                   # "fit" = learn from the examples

# Which URLs should we test?
if len(sys.argv) > 1:
    tests = [sys.argv[1]]
else:
    tests = [
        "https://www.wikipedia.org/",
        "http://secure-login-paypal.verify-now.top/account",
        "https://docs.python.org/3/",
    ]

for url in tests:
    probability = model.predict_proba([features(url)])[0][1]   # chance (0 to 1) of being phishing
    verdict = "PHISHING?" if probability > 0.5 else "looks safe"
    print(f"{verdict:10} ({probability * 100:.0f}% phishing)  {url}")
