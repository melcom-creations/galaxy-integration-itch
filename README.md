# itch.io Integration Plugin for GOG Galaxy 2.1+ (64-bit)

This plugin imports your itch.io library into GOG Galaxy 2.1+ 64-bit. Based on the original community integration, it has been updated for the current GOG Galaxy client and Python 3.13, with modernized token-based authentication.

> **☕ Optional support**
>
> This integration is free and will remain free. If you'd like to support my work, you're welcome to [☕ buy me a coffee through PayPal](https://paypal.me/melcom2630). Support is entirely optional and always appreciated.

The steps below are for Windows. Dependencies are bundled; no separate Python installation is needed.

[Installation](#-installation) | [First Start](#-first-start-and-initial-sync) | [Troubleshooting](#-troubleshooting) | [Support & Feedback](#-support--feedback)

## ✨ Features

* Imports your owned itch.io games into GOG Galaxy
* Includes installed itch.io games that do not have a claimed download key
* Detects games installed through the itch.io desktop app
* Launches installed games directly from GOG Galaxy
* Tracks game time for games launched through the integration
* Refreshes the local installation state automatically
* Accepts the personal itch.io API token directly in the Galaxy setup window
* Stores authentication outside the plugin folder with Windows DPAPI protection

## 📦 Installation

### 🔄 Automatic Installation with Plugin Updater (Recommended)

Use the [melcom GOG Galaxy Plugin Updater](https://github.com/melcom-creations/galaxy-integrations-64bit/tree/main/tools/melcom-galaxy_plugin_updater) to install or update the integration.

1. Download and extract the Plugin Updater.
2. Double-click `update-plugins.bat`.
3. Select your preferred language and follow the displayed instructions.

The personal API token is stored outside the plugin folder. Plugin updates do not overwrite this configuration or require it to be restored.

### 📂 Manual Installation

1. Close GOG Galaxy completely, including the system tray application.
2. Download the [latest release package](https://github.com/melcom-creations/galaxy-integration-itch/releases/latest).
3. Extract the plugin folder from the ZIP archive into:

   ```text
   %localappdata%\GOG.com\Galaxy\plugins\installed\
   ```

Place `manifest.json` directly inside this folder, without an extra nested plugin folder:

```text
%localappdata%\GOG.com\Galaxy\plugins\installed\itch_2df02142-4d8a-4a4b-9b6e-c3a0bc62f93b\
```

> [!IMPORTANT]
> Do not place backup copies of this plugin inside the `plugins\installed` directory. GOG Galaxy scans every folder inside this directory during startup, so duplicate plugin folders can cause GUID conflicts or load an outdated version.

**Next step:** Continue with [One-Time Setup (Required)](#-one-time-setup-required), then [First Start and Initial Sync](#-first-start-and-initial-sync).

## ⚠️ One-Time Setup (Required)

The plugin requires the itch.io desktop app and a personal itch.io API token. When no valid token is available, GOG Galaxy displays the bundled setup guide after you click **Connect**. English and German versions of the guide are included with the plugin.

### 📦 Installing the itch.io Desktop App

1. Download and install the [itch.io desktop app](https://itch.io/app).
2. Start the app and sign in with your itch.io account.
3. Keep the app open until its local database has been created at:

```text
%appdata%\itch\db\butler.db
```

The plugin reads installed games from this database.

### 🔑 Creating Your Personal API Token

1. Open the following authorization link in your regular web browser, not inside GOG Galaxy:

   [Authorize GOG Galaxy Integration](https://itch.io/user/oauth?client_id=3821cecdd58ae1a920be15f6aa479f7e&scope=profile&response_type=token&redirect_uri=http%3A%2F%2F127.0.0.1%3A7157%2Fgogg2itchintegration)

2. Sign in to itch.io and select **Authorize GOG Galaxy Integration**.
3. The browser will redirect to an error page because no local web server is running at the redirect address. This is expected.
4. Copy the complete address from the browser address bar or only the token value shown after `access_token=`:

   ```text
   http://127.0.0.1:7157/gogg2itchintegration#access_token=YOUR_TOKEN_HERE
   ```

5. Open **Settings -> Integrations -> itch.io** in GOG Galaxy and click **Connect**.
6. Paste the complete callback address or token into the displayed setup field.
7. Click **Save and Connect**. The plugin verifies the token, stores it securely, and completes the connection automatically. A Galaxy restart is not required.

### 🔒 Token Storage and Replacement

The setup creates the external directory and an `auth.json` setup marker automatically. The authentication file is stored at:

```text
%localappdata%\melcom-creations\GOG Galaxy Integrations\itch.io\auth.json
```

On the first Connect click, this file contains only a credential-free setup marker. After successful verification, the plugin replaces it with the token protected by Windows DPAPI for the current Windows user. The token is not stored in the plugin folder.

Existing installations with the old `credentials.json` format are migrated automatically after the token has been validated. The legacy file is removed only after the protected external file has been written and read back successfully.

> ⚠️ Keep your API token private. Never publish `auth.json`, send it to another person, or commit it to a public repository. If the token stops working, close GOG Galaxy, delete the external `auth.json`, and click **Connect** again. The plugin recreates the directory and setup marker automatically.

## 🚀 First Start and Initial Sync

For the first synchronization after installing, updating, or configuring the plugin:

1. Start the itch.io desktop app and keep it open.
2. Start GOG Galaxy.
3. Connect the itch.io integration through **Settings -> Integrations** if necessary.
4. Open the account menu in the top-right corner and select **Sync integrations**.
5. Wait until the synchronization has finished.

Purchased games with claimed download keys are imported through the itch.io API. Games installed through the itch.io desktop app can also appear even if they were free downloads, jam entries, or otherwise never received a claimed download key.

## 🛠️ Troubleshooting

Restart Galaxy and the store app and try one synchronization. If the problem remains, collect a fresh log. A database reset is not required for this.

### 🧪 Create a Fresh Diagnostic Log

1. Close GOG Galaxy completely, including the system tray application.
2. Open `%ProgramData%\GOG.com\Galaxy\logs\`. Move the existing `plugin-itch-2df02142-4d8a-4a4b-9b6e-c3a0bc62f93b.log` to a backup folder outside this directory, if present. Leave other logs in place.
3. Start the itch.io desktop app. Start Galaxy, reproduce the problem once, then close Galaxy completely to finish writing the log.
4. Send the newly created plugin log, not the entire folder. Include the plugin and Galaxy versions, your steps, the expected and actual result, and whether the problem can be reproduced.

See [Support & Feedback](#-support--feedback) for contact options.

### 🔄 Reset Plugin Storage (Last Resort)

Use this only if restarting and synchronizing do not help, or when requested for troubleshooting. Cached library data and local playtime may be lost; signing in again may be required. Keep the backup. The separate `auth.json` file remains unchanged.

1. Close GOG Galaxy completely, including the system tray application.
2. Open `%ProgramData%\GOG.com\Galaxy\storage\plugins\`.
3. Find the active `itch_...-storage.db` file for your Galaxy account. If unsure which file is correct, stop. Leave other integrations' databases unchanged.
4. Append `.old` to its name. If that backup already exists, use an unused suffix; never overwrite it.
5. Start the itch.io desktop app. Start Galaxy, reconnect if necessary, and select **Sync integrations** once. Wait until it finishes.

To undo: close Galaxy, rename the new database to an unused backup name, then restore the saved database's original name. Never restore it while Galaxy is running.

## 🙏 Credits

**Original Plugin Author**  
Tauqua  
[Tauqua's original itch.io integration](https://github.com/tauqua/gog-galaxy-itch.io)

**64-bit Port, Setup Modernization and Continued Development**  
melcom

## ❤️ Special Thanks

I want to take a moment to thank the people who kept me going during this intense development phase:

* A huge thank you to my friend [**Hustlefan**](https://www.gog.com/u/Hustlefan). Over the past few days, you've been much more than just moral support. You gave me the encouragement I needed, patiently put up with all my Discord spam, and helped beta test the plugins. I'm really happy that you're pleased with the results. Thanks so much for all your support, my friend.

* And a big thank you to my girlfriend [**Florence H.** (fl0H0815)](https://www.gog.com/u/Florence_Heart). While she was enjoying the good life at her parents' place - complete with air conditioning and a huge swimming pool - she kept my spirits up by sending me photos of herself, her friends, her parents, and even her parents' dog. She reminded me that there's a wonderful world outside of a code editor every now and then... 🙈

  *Now that's what I call real support.* ❤️

Thank you both for having my back!

## 🤝 Support & Feedback

**GitHub Issues are intentionally disabled.** Health-related limitations prevent me from reliably managing separate issue trackers across all of my plugin repositories.

Before contacting me, follow [Troubleshooting](#-troubleshooting) and prepare a fresh itch.io plugin log with a detailed description.

* **GOG:** Send me a message or add me as a friend through my [GOG profile](https://www.gog.com/u/melcom).
* **Email:** `melcom @ gmx.net`
* **Discord:** `.melcom` - the leading dot is part of the username. You can send me a message or add me as a friend.

Logs can be attached directly or shared using an accessible cloud storage link, such as Dropbox, OneDrive, Google Drive, or a similar service. Response times may vary depending on my health and available development time. Thank you for your understanding.
