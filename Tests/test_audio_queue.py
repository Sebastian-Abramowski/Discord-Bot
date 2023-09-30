from utilities.audio_queue import AudioQueue


def test_str_queue():
    queue = AudioQueue()
    queue.push("sth1")
    queue.push("sth2")

    assert str(queue) == "Queue: \n1) sth1\n2) sth2"


def test_clear():
    queue = AudioQueue()
    queue.push("sth1")
    queue.push("sth2")
    queue.clear()
    assert queue.queue == []


def test_push():
    queue = AudioQueue()
    queue.push("sth1")
    queue.push("sth2")
    queue.push("sth3")
    queue.push("sth4")
    assert queue.queue == ["sth1", "sth2", "sth3", "sth4"]


def test_push_with_priority():
    queue = AudioQueue()
    queue.push("sth1")
    queue.push("sth2")
    queue.push("sth3")
    queue.push("sth4")
    queue.push_with_priority("sth0")
    assert queue.queue == ["sth0", "sth1", "sth2", "sth3", "sth4"]


def test_pop():
    queue = AudioQueue()
    queue.push("sth1")
    queue.push("sth2")
    queue.push("sth3")
    queue.push("sth4")
    queue.push_with_priority("sth0")

    assert queue.pop() == "sth0"
    assert queue.queue == ["sth1", "sth2", "sth3", "sth4"]
    assert queue.pop() == "sth1"
    assert queue.queue == ["sth2", "sth3", "sth4"]
    assert queue.pop() == "sth2"
    assert queue.queue == ["sth3", "sth4"]
    assert queue.pop() == "sth3"
    assert queue.queue == ["sth4"]
    assert queue.pop() == "sth4"
    assert queue.queue == []
    queue.pop()
    assert queue.queue == []


def test_get_first_one_to_leave():
    queue = AudioQueue()
    queue.push("sth1")
    queue.push("sth2")
    queue.push("sth3")
    queue.push("sth4")

    assert queue.get_first_one_to_leave() == "sth1"


def test_push_and_pop():
    queue = AudioQueue()
    queue.push("link1")
    queue.push("link1")
    queue.push("link1")
    queue.push("link1")
    queue.push("link2")

    assert queue.pop() == "link1"
    assert queue.pop() == "link1"
    assert queue.pop() == "link1"
    assert queue.pop() == "link1"
    assert queue.pop() == "link2"
