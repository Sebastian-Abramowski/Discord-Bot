from utilities.validation import is_url_valid


def test_valid_url():
    assert is_url_valid("https://www.youtube.com/watch?v=dQw4w9WgXcQ")


def test_valid_url2():
    assert is_url_valid("https://vimeo.com/375468729")


def test_valid_url_that_leads_to_no_video():
    assert is_url_valid("https://www.youtube.com/watch?v=dQw4w9WgXc")


def test_valid_url_that_leads_to_no_video2():
    assert is_url_valid("https://www.TToutube.com/watch?v=dQw4w9WgXc")


def test_invalid_url():
    assert not is_url_valid("https://www.youtube.comwav=dQw4w9WgXc")


def test_invalid_url2():
    assert not is_url_valid("https:/www.youtube.com/watch?v=dQw4w9WgXcQ")


def test_invalid_url3():
    assert not is_url_valid("https://zajonc")


def test_invalid_url4():
    assert not is_url_valid("htps:/www.youtube.com/watch?v=dQw4w9WgXcQ")
