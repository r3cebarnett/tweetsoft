import configparser
import datetime
import logging
import tweepy

from discord.ext import commands, tasks

from sqlalchemy import select, func
from sqlalchemy.orm import sessionmaker

from db import engine, Channel, Account

logging.basicConfig(level=logging.INFO)

cfg = configparser.RawConfigParser()
cfg.read(".discord_config")
prefix = cfg.get("tweetsoft", "prefix")
token = cfg.get("tweetsoft", "discord_token")
twitter_token = cfg.get("tweetsoft", "twitter_token")

client = tweepy.Client(bearer_token=twitter_token)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

if not prefix:
    logging.info("No prefix found in config file... using t. as default")
    prefix = "t."

bot = commands.Bot(command_prefix=prefix)

## TODO Make a wrapper for checking perms on these

@bot.command()
async def addacct(ctx: commands.Context, *args: tuple[str]):
    logging.info(f"addacct called: {args}")

    if len(args) != 2 or len(ctx.message.channel_mentions) != 1:
        await ctx.send(f"Usage: {prefix}addacct <mention channel> <account>")
        return

    channel = ctx.message.channel_mentions[0]
    account = ''.join(args[1])
    server = ctx.guild.id

    if channel not in ctx.guild.text_channels:
        await ctx.send(f"Error: {channel} does not exist in this server!")
        return

    # First check to see if channel exists in DB:
    res = session.query(Channel).where(Channel.server_id == server, Channel.channel_id == channel.id)
    channel_obj = res.first()
    if not channel_obj:
        # create a channel obj
        channel_obj = Channel(channel_id=channel.id, server_id=server)
        session.add(channel_obj)

    # Then check to see if the account exists
    res = session.query(Account).where(func.lower(Account.username) == func.lower(account))
    account_obj = res.first()
    tweet_id = None
    if not account_obj:
        # create an account obj
        twitter_user = client.get_user(username=account)
        try:
            twitter_user_id = twitter_user.data.id
            account = twitter_user.data.username
        except:
            await ctx.send(f"Unable to find {account} on Twitter.")
            return

        last_tweet = client.get_users_tweets(twitter_user_id, max_results=5, exclude="replies", tweet_fields="source")
        tweet_id = last_tweet.data[0].id
        account_obj = Account(username=account, last_tweet=tweet_id, twitter_id=twitter_user_id)
        session.add(account_obj)

    # Then check to see if account has channel
    if channel_obj in account_obj.channels:
        await ctx.send(f"{account} is already registered to {channel.mention}!")
        return
    else:
        account_obj.channels.append(channel_obj)
        session.add(account_obj)

    await channel.send(f"`{account}` added to this channel by {ctx.author.mention}")

    if not tweet_id:
        tweet_id = account_obj.last_tweet
        last_tweet = client.get_tweet(tweet_id, tweet_fields="source")

    msg = f"https://fxtwitter.com/{account}/status/{tweet_id}"
    await channel.send(msg)

    session.commit()


@bot.command()
async def rmacct(ctx: commands.Context, *args: tuple[str]):
    logging.info(f"rmacct called: {args}")

    if len(args) != 2 or len(ctx.message.channel_mentions) != 1:
        await ctx.send(f"Usage: {prefix}addacct <mention channel> <account>")
        return

    channel = ctx.message.channel_mentions[0]
    account = ''.join(args[1])
    server = ctx.guild.id

    if channel not in ctx.guild.text_channels:
        await ctx.send(f"Error: {channel} does not exist in this server!")
        return

    # First check to see if channel exists in DB:
    res = session.query(Channel).where(Channel.server_id == server, Channel.channel_id == channel.id)
    channel_obj = res.first()
    if not channel_obj:
        await ctx.send(f"{channel.mention} not found in database")
        return

    # Then check to see if the account exists
    res = session.query(Account).where(func.lower(Account.username) == func.lower(account))
    account_obj = res.first()
    if not account_obj:
        await ctx.send(f"`{account}` not found in database")
        return

    # Finally try to remove channel from account
    try:
        account_obj.channels.remove(channel_obj)
    except ValueError:
        await ctx.send(f"Unable to find {channel.mention} in `{account}` list.")
        return

    # Send message to affected channel to log the removal of account
    await channel.send(f"`{account}` removed from this channel by {ctx.author.mention}")

    # If account has no more channels, remove account
    if len(account_obj.channels) == 0:
        session.delete(account_obj)

    session.commit()


@tasks.loop(minutes=1.0)
async def update():
    logging.info("Updating...")
    for acct in session.query(Account):
        try:
            tweets = client.get_users_tweets(acct.twitter_id, exclude="replies", tweet_fields="source", since_id=acct.last_tweet)
        except tweepy.TwitterServerError as e:
            logging.info(f"Unable to refresh tweets: {e}")
        if not tweets.data:
            continue

        for tweet in tweets.data[::-1]:
            tweet_id = tweet.id
            for channel in acct.channels:
                dpy_channel = bot.get_channel(int(channel.channel_id))
                logging.info(f"\t{acct.username} - {channel.channel_id} ({dpy_channel.name})")
                msg = f"https://fxtwitter.com/{acct.username}/status/{tweet_id}"
                await dpy_channel.send(msg)
        acct.last_tweet = tweets.data[0].id
        session.add(acct)
    session.commit()
    logging.info("Finished updating")

@update.before_loop
async def before_update():
    await bot.wait_until_ready()

update.start()

bot.run(token)