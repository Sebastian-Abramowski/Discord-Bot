# DonkeyBot

<img src="icon.png" alt="donkey image" width="24%">

## Requirements

Installation of used python modules:

```bash
pip install discord
pip install PyNaCl # (for voice support)
pip install python-dotenv # (for using environmental variables)
pip install yt-dlp # (for getting information about videos from YouTube and other video sites)
pip install Django # (for URL validator)
```

You must have the <strong>ffmpeg</strong> executable in your path environment variable in order for this to work (reason: *https://discordpy.readthedocs.io/en/stable/api.html?highlight=ffmpeg#ffmpegopusaudio*)

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`TOKEN` - discord bot token
