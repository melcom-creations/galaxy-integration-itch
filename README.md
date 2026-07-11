# itch.io Integration Plugin for GOG Galaxy 2.1+ (64-bit)

This repository contains the itch.io integration plugin for the 64-bit version of GOG Galaxy 2.1+.

The original community integration has been updated to work with the current 64-bit GOG Galaxy client and Python 3.13. In addition to compatibility improvements, this project includes dependency updates, bug fixes, stability improvements and ongoing maintenance.

---

## ✨ Features

* Compatible with GOG Galaxy 2.1+ (64-bit)
* Python 3.13 support
* Updated 64-bit dependencies
* Improved stability and compatibility
* Ongoing maintenance and bug fixes

---

## 📦 Installation

### Standard Installation (Recommended)

1. Close GOG Galaxy completely.
2. Download the latest release from this repository.
3. Open the following folder:

```text
%localappdata%\GOG.com\Galaxy\plugins\installed\
```

1. Extract the ZIP archive **directly into this folder**.

The resulting directory structure **must** look like this:

```text
%localappdata%\GOG.com\Galaxy\plugins\installed\
└── itch_2df02142-4d8a-4a4b-9b6e-c3a0bc62f93b\
    ├── manifest.json
    ├── itch.py
    ├── README.md
    └── ...
```

1. Start GOG Galaxy.

---

## 🔄 Resetting the Plugin Database (Recommended)

If the plugin behaves unexpectedly after an update, resetting the local plugin database is recommended.

1. Open `C:\ProgramData\GOG.com\Galaxy\storage\plugins\` and find the files starting with `itch_` and ending in `-storage.db`.
2. Rename each by appending `.old` (e.g. `itch_xxxxxxxxx-storage.db` -> `itch_xxxxxxxxx-storage.db.old`).
3. Start GOG Galaxy again and reconnect the itch.io integration if necessary.

### 🚀 First Start and Initial Sync (Important)

For a clean first run after installing or updating the plugin:

1. Close GOG Galaxy.
2. Open this folder:

```text
C:\ProgramData\GOG.com\Galaxy\storage\plugins\
```

1. If an `itch_...-storage.db` file exists there, delete it.
2. Start GOG Galaxy.
3. Start the itch app and keep it open.
4. In GOG Galaxy, open the account menu (top-right) and click **Sync integrations**.
5. Wait until sync finishes.

---

## ⚠️ Important

Do **not** place backup copies of this plugin inside the `plugins\installed` directory.

GOG Galaxy scans every folder inside this directory during startup. Duplicate plugin folders can lead to GUID conflicts or cause Galaxy to load an outdated version of the plugin.

---

## 🙏 Credits

**Original Plugin Author**
Tauqua
[Tauqua's original itch.io integration](https://github.com/tauqua/gog-galaxy-itch.io)

**64-bit Port, Setup Modernization & Continued Development**
melcom

---

## ❤️ Special Thanks

I want to take a moment to thank the people who kept me going during this intense development phase:

* A huge thank you to my friend [**Hustlefan**](https://www.gog.com/u/Hustlefan). Over the past few days, you've been much more than just moral support. You gave me the encouragement I needed, patiently put up with all my Discord spam, and helped beta test the plugins. I'm really happy that you're pleased with the results. Thanks so much for all your support, my friend.

* And a big thank you to my girlfriend [**Florence H.** (fl0H0815)](https://www.gog.com/u/Florence_Heart). While she was enjoying the good life at her parents' place - complete with air conditioning and a huge swimming pool - she kept my spirits up by sending me photos of herself, her friends, her parents, and even her parents' dog. She reminded me that there's a wonderful world outside of a code editor every now and then... 🙈

  *Now that's what I call real support.* ❤️

Thank you both for having my back!

---

## 🤝 Support & Feedback

This project is developed and maintained by one person. Response times may vary, especially during periods when health-related limitations reduce available development time.

**GitHub Issues are intentionally disabled.**

If you would like to report a bug or suggest an improvement, please use the contact form on my website:

📩 [Contact form](https://melcom-creations.github.io/melcom-music/contact.html)

Thank you for your patience and support!
