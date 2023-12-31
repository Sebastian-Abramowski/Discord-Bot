from ds_bots import db, app
from ds_bots.models import Command

with app.app_context():
    db.create_all()

    db.session.add(Command('DonkeyMusicBot', '/join', 'channel'))
    db.session.add(Command('DonkeyMusicBot', '/play', 'play'))
    db.session.add(Command('DonkeyMusicBot', '/skip', 'play'))
    db.session.add(Command('DonkeyMusicBot', '/loop', 'play'))
    db.session.add(Command('DonkeyMusicBot', '/end_loop', 'play'))
    db.session.add(Command('DonkeyMusicBot', '/end_loop_now', 'play'))
    db.session.add(Command('DonkeyMusicBot', '/pause', 'play'))
    db.session.add(Command('DonkeyMusicBot', '/resume', 'play'))
    db.session.add(Command('DonkeyMusicBot', '/stop', 'play'))
    db.session.add(Command('DonkeyMusicBot', '/disconnect', 'channel'))
    db.session.add(Command('DonkeyMusicBot', '/show_queue', 'queue'))
    db.session.add(Command('DonkeyMusicBot', '/clear_queue', 'queue'))
    db.session.add(Command('DonkeyMusicBot', '/shuffle_queue', 'queue'))
    db.session.add(Command('DonkeyMusicBot', '/put_on_top_of_queue', 'queue'))
    db.session.add(Command('DonkeyMusicBot', '/reset_bot', 'reset'))
    db.session.add(Command('DonkeyMusicBot', '/play_sui', 'play'))

    db.session.add(Command('DonkeySecondaryBot', '/check_country', 'check'))
    db.session.add(Command('DonkeySecondaryBot', '/check_marvel_character', 'check'))
    db.session.add(Command('DonkeySecondaryBot', '/check_movie', 'check'))
    db.session.add(Command('DonkeySecondaryBot', '/random_joke', 'get_random'))
    db.session.add(Command('DonkeySecondaryBot', '/random_fact', 'get_random'))
    db.session.add(Command('DonkeySecondaryBot', '/random_riddle', 'get_random'))
    db.session.add(Command('DonkeySecondaryBot', '/random_cat_image', 'get_random'))
    db.session.add(Command('DonkeySecondaryBot', '/random_num', 'get_random'))
    db.session.add(Command('DonkeySecondaryBot', '/flip_coin', 'get_random'))

    db.session.commit()
