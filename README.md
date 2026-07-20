# itch.io Integration Plugin for GOG Galaxy 2.1+ (64-bit)

This plugin imports your itch.io library into GOG Galaxy 2.1+ 64-bit. Based on the original community integration, it has been updated for the current GOG Galaxy client and Python 3.13, with modernized token-based authentication.

---

## ✨ Features

* Imports your owned itch.io games into GOG Galaxy
* Includes installed itch.io games that do not have a claimed download key
* Detects games installed through the itch.io desktop app
* Launches installed games directly from GOG Galaxy
* Tracks game time for games launched through the integration
* Refreshes the local installation state automatically
* Uses a personal itch.io API token without a Cloudflare-dependent login window

---

## 📦 Installation

### Automatic Installation with Plugin Updater (Recommended)

Use the [melcom GOG Galaxy Plugin Updater](https://github.com/melcom-creations/galaxy-integrations-64bit/tree/main/tools/melcom-galaxy_plugin_updater) to install or update the integration automatically.

1. Download and extract the Plugin Updater.
2. Double-click `update-plugins.bat`.
3. Select your preferred language.
4. Follow the displayed instructions.

When updating an existing itch.io installation, the updater detects a personal token in `credentials.json`, creates an additional backup, and offers to restore the file after the update.

### Manual Installation

1. Close GOG Galaxy completely, including the system tray application.
2. Download the latest release package from this repository.
3. Extract the ZIP archive directly into:

```text
%localappdata%\GOG.com\Galaxy\plugins\installed\
```

The resulting directory structure must look like this:

```text
%localappdata%\GOG.com\Galaxy\plugins\installed\
└── itch_2df02142-4d8a-4a4b-9b6e-c3a0bc62f93b\
    ├── manifest.json
    ├── itch.py
    ├── credentials.json
    ├── setup.html
    ├── README.md
    └── ...
```

**Next step:** Complete the mandatory one-time setup below.

> [!IMPORTANT]
> Do not place backup copies of this plugin inside the `plugins\installed` directory. GOG Galaxy scans every folder inside this directory during startup, so duplicate plugin folders can cause GUID conflicts or load an outdated version.

---

## ⚠️ Mandatory One-Time Setup

The plugin requires the itch.io desktop app and a personal itch.io API token. When no valid token is available, GOG Galaxy displays the bundled setup guide after you click **Connect**. English and German versions of the guide are included with the plugin.

### Installing the itch.io Desktop App

1. Download and install the [itch.io desktop app](https://itch.io/app).
2. Start the app and sign in with your itch.io account.
3. Keep the app open until its local database has been created at:

```text
%appdata%\itch\db\butler.db
```

The plugin reads installed games from this database.

### Creating Your Personal API Token

1. Open the following authorization link in your regular web browser, not inside GOG Galaxy:

   [Authorize GOG Galaxy Integration](https://itch.io/user/oauth?client_id=3821cecdd58ae1a920be15f6aa479f7e&scope=profile&response_type=token&redirect_uri=http%3A%2F%2F127.0.0.1%3A7157%2Fgogg2itchintegration)

2. Sign in to itch.io and select **Authorize GOG Galaxy Integration**.
3. The browser will redirect to an error page because no local web server is running at the redirect address. This is expected.
4. Copy the complete token value shown after `access_token=` in the browser address bar:

   ```text
   http://127.0.0.1:7157/gogg2itchintegration#access_token=YOUR_TOKEN_HERE
   ```

5. Open the existing `credentials.json` file located at:

   ```text
   %localappdata%\GOG.com\Galaxy\plugins\installed\itch_2df02142-4d8a-4a4b-9b6e-c3a0bc62f93b\credentials.json
   ```

6. Insert your token and save the file:

   ```json
   {
     "access_token": "YOUR_TOKEN_HERE"
   }
   ```

7. Fully close and reopen GOG Galaxy.
8. Open **Settings -> Integrations -> itch.io** and click **Connect**.

> ⚠️ Keep your API token private. Never publish `credentials.json`, send it to another person, or commit it to a public repository. If the token stops working, repeat the authorization steps and replace it with a newly generated token.

---

## 🚀 First Start and Initial Sync

For the first synchronization after installing, updating, or configuring the plugin:

1. Start the itch.io desktop app and keep it open.
2. Start GOG Galaxy.
3. Connect the itch.io integration through **Settings -> Integrations** if necessary.
4. Open the account menu in the top-right corner and select **Sync integrations**.
5. Wait until the synchronization has finished.

Purchased games with claimed download keys are imported through the itch.io API. Games installed through the itch.io desktop app can also appear even if they were free downloads, jam entries, or otherwise never received a claimed download key.

---

## 🔄 Resetting the Plugin Database (Troubleshooting)

Reset the local plugin database if synchronization problems continue after restarting both applications.

1. Close GOG Galaxy completely.
2. Open `C:\ProgramData\GOG.com\Galaxy\storage\plugins\`.
3. Find every file starting with `itch_` and ending in `-storage.db`.
4. Rename each matching file by appending `.old`, for example:

   `itch_xxxxxxxxx-storage.db` -> `itch_xxxxxxxxx-storage.db.old`

5. Start the itch.io desktop app and keep it open.
6. Start GOG Galaxy, reconnect the integration if necessary, select **Sync integrations** from the account menu, and wait for synchronization to finish.

---

## 🛠️ What to Do If the Plugin Has Problems

If the database reset above does not resolve the problem, create a clean session with fresh diagnostic files before contacting me. The reset procedure preserves the previous database as a `.old` file; the steps below remove the active database so the issue can be reproduced from a clean state.

1. Close GOG Galaxy completely, including the system tray application.
2. Open the following directory and delete the existing log files:

   ```text
   %ProgramData%\GOG.com\Galaxy\logs
   ```

3. Open the plugin storage directory:

   ```text
   C:\ProgramData\GOG.com\Galaxy\storage\plugins
   ```

   Delete only the active itch.io database file starting with `itch_` and ending in `-storage.db`. Do not delete database files belonging to other integrations. If you are unsure which file is correct, do not delete anything from this directory.
4. Start the itch.io desktop app and keep it open. Start GOG Galaxy, reproduce the problem, and then close GOG Galaxy completely so the new log is fully written.
5. Return to the logs directory and locate the newly created itch.io plugin log:

   ```text
   plugin-itch-2df02142-4d8a-4a4b-9b6e-c3a0bc62f93b.log
   ```

Send only this log file, not the entire logs folder. Include the exact steps taken, the expected and actual result, and whether the problem can be reproduced.

Without a fresh plugin log and a detailed description, I cannot reliably determine what is causing the problem. Once everything is ready, continue with [Support & Feedback](#-support--feedback) for contact options.

---

## 🙏 Credits

**Original Plugin Author**  
Tauqua  
[Tauqua's original itch.io integration](https://github.com/tauqua/gog-galaxy-itch.io)

**64-bit Port, Setup Modernization and Continued Development**  
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

**GitHub Issues are intentionally disabled.** Health-related limitations prevent me from reliably managing separate issue trackers across all of my plugin repositories.

Before contacting me, follow **What to Do If the Plugin Has Problems** and prepare a fresh itch.io plugin log with a detailed description.

* **GOG:** Send me a message or add me as a friend through my [GOG profile](https://www.gog.com/u/melcom).
* **Email:** `melcom @ gmx.net`
* **Discord:** `.melcom` - the leading dot is part of the username. You can send me a message or add me as a friend.

Logs can be attached directly or shared using an accessible cloud storage link, such as Dropbox, OneDrive, Google Drive, or a similar service. Response times may vary depending on my health and available development time. Thank you for your understanding.
