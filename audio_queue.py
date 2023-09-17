from random import shuffle
from typing import Optional


class AudioQueue():
    def __init__(self):
        self.queue = []

    def __str__(self) -> str:
        if not self.queue:
            return "Queue: []"
        result = "Queue: \n"
        for i, url in enumerate(self.queue):
            result += str(i+1) + ') ' + url + '\n'
        return result[:-1]

    def shuffle(self) -> None:
        shuffle(self.queue)

    def clear(self) -> None:
        self.queue.clear()

    def push(self, url: str) -> None:
        self.queue.append(url)

    def push_with_priority(self, url: str) -> None:
        self.queue.insert(0, url)

    def pop(self) -> str:
        if self.queue:
            return self.queue.pop(0)

    def get_first_one_to_leave(self) -> Optional[str]:
        if self.queue:
            return self.queue[0]
        return None
