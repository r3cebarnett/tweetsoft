from sqlalchemy import Column, Integer, String, ForeignKey, Table, create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///tweetsoft.db", echo=False, future=True)
Base = declarative_base(bind=engine)

channel_account_assoc = Table(
    "channel_account",
    Base.metadata,
    Column("channel_id", ForeignKey("channel.channel_pid")),
    Column("account_id", ForeignKey("account.account_id"))
)

class Channel(Base):
    __tablename__ = "channel"
    channel_pid = Column(Integer, primary_key=True)
    channel_id = Column(String)
    server_id = Column(String)
    accounts = relationship("Account", secondary=channel_account_assoc, back_populates="channels")

class Account(Base):
    __tablename__ = "account"
    account_id = Column(Integer, primary_key=True)
    username = Column(String)
    twitter_id = Column(String)
    last_tweet = Column(String)
    channels = relationship("Channel", secondary=channel_account_assoc, back_populates="accounts")

Base.metadata.create_all()
