from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, UniqueConstraint

from ds_bots import db


class Command(db.Model):
    __tablename__ = 'commands'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bot_name: Mapped[str] = mapped_column(String(100), nullable=False)
    command: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (
        UniqueConstraint('bot_name', 'command', name='unique_bot_command'),
    )

    def __init__(self, bot_name, command, category):
        self.bot_name = bot_name
        self.command = command
        self.category = category

    def __repr__(self):
        return f"Command: {self.command} of {self.bot_name} bot [Category: {self.category}]"
