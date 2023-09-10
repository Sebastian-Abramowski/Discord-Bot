# DonkeyBot

<img src="icon.png" alt="donkey image" width="24%">

## Requirements

Installation of used python modules:

```bash
pip install discord
pip install PyNaCl # (for voice support)
pip install python-dotenv
pip install yt-dlp
pip install Django # (for URL validator)
```

You must have the <strong>ffmpeg</strong> executable in your path environment variable in order for this to work (reason: *https://discordpy.readthedocs.io/en/stable/api.html?highlight=ffmpeg#ffmpegopusaudio*)

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`TOKEN` - discord bot token
