# Video Downloader — iOS Shortcut

Downloads videos from **Twitter/X** and **browser URLs** (Safari, Chrome, etc.) directly to your Photos library.

Powered by [Cobalt](https://cobalt.tools) — a free, open-source video downloader that supports Twitter/X, YouTube, Instagram, TikTok, Reddit, Vimeo, and 20+ other sites.

---

## Files

| File | Description |
|------|-------------|
| `VideoDownloader.shortcut` | The shortcut — import this on your iPhone/iPad |
| `generate_shortcut.py` | Python script that regenerates the shortcut file |

---

## Setup (one time)

### 1. Get a free Cobalt API key

1. Visit [cobalt.tools](https://cobalt.tools) and sign up for a free account
2. Copy your API key from your account dashboard

### 2. Allow untrusted shortcuts on your device

1. Open **Settings → Shortcuts**
2. Enable **Allow Untrusted Shortcuts**

> This is required for shortcuts not distributed through Apple's gallery.

### 3. Import the shortcut

Transfer `VideoDownloader.shortcut` to your device by any of these methods:
- **AirDrop** the file from your Mac
- **iCloud Drive** — place the file there, open it from the Files app on iOS
- **Email** the file to yourself and open the attachment
- **USB** via Finder → Files

Tap the file on your iOS device. The Shortcuts app will open and prompt you to add it.

### 4. Add your API key

1. Open the **Shortcuts** app
2. Long-press **Video Downloader** → **Edit**
3. Find the **Text** action near the top (it says `YOUR_COBALT_API_KEY`)
4. Replace that text with your real Cobalt API key
5. Tap **Done**

---

## Usage

### From the Share Sheet (recommended)

1. Open a tweet in the **Twitter/X app** or a video page in **Safari**
2. Tap the **Share** button
3. Select **Video Downloader**
4. The video is saved to your **Photos** library

### Manually

1. Open the **Shortcuts** app
2. Tap **Video Downloader**
3. Paste or type the video URL when prompted
4. The video is saved to your **Photos** library

---

## Supported Sites

Cobalt supports all major video platforms. A few examples:

- Twitter / X
- YouTube
- Instagram (Reels, posts)
- TikTok
- Reddit
- Twitch clips
- Vimeo
- Dailymotion
- Pinterest

For the full list see [cobalt.tools](https://cobalt.tools).

---

## Regenerating the shortcut

If you want to customise the shortcut (change the API endpoint, add platforms, etc.):

```bash
python3 generate_shortcut.py
# Outputs: VideoDownloader.shortcut
```

Requires Python 3.9+ (no external dependencies).

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| "Cobalt API Error: api_key_missing" | Edit the shortcut and add your API key (Step 4 above) |
| "Cobalt API Error: link_error" | The URL is not supported or the video is private |
| Shortcut doesn't appear in Share Sheet | Go to Share Sheet → Edit Actions → add Video Downloader |
| iOS says shortcut is untrusted | Enable Settings → Shortcuts → Allow Untrusted Shortcuts |
