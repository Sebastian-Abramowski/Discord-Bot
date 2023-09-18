# DonkeyBot

<img src="Assets/icon.png" alt="donkey image" width="24%">

## Features

Both bots use discord slash commands. After typing '/' in discord, you will get hints on how to use them.

### DonkeyMusicBot commands:

- /join
- /play
- /skip
- /loop
- /end_loop
- /end_loop_now
- /pause
- /resume
- /stop
- /disconnect
- /show_queue
- /clear_queue
- /shuffle_queue
- /put_on_top_of_queue
- /reset_bot
- /play_sui

### DonkeySecondaryBot commands:

- /check_country_command
- /check_marvel_character
- /check_movie
- /random_joke
- /random_fact
- /random_riddle
- /random_cat_image
- /random_num
- /flip_coin

## Requirements

Installation of used python modules:

```bash
pip install -r requirements.txt
```

You must have the <strong>ffmpeg</strong> executable in your path environment variable in order for this to work (reason: *https://discordpy.readthedocs.io/en/stable/api.html?highlight=ffmpeg#ffmpegopusaudio*)

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

For DonkeyMusicBot:

- `DONKEY_MUSIC_BOT_TOKEN`

For DonkeySecondaryBot:

- `DONKEY_SECONDARY_BOT_TOKEN`
- `URL_TO_MY_REPO`
- `API_NINJAS_API_KEY`
- `THECATAPI_API_KEY`
- `OMDB_API_API_KEY`
- `MARVEL_API_PUBLIC_KEY`
- `MARVEL_API_PRIVATE_KEY`
- `COUNTRYAPI_API_KEY`
