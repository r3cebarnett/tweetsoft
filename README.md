# tweetsoft
Discord Bot for Modular Twitter Feeds

## How it works
- Categories
- Accounts
- Adding and Removing
- Quick Response Times (1m)

## Planned Usage
- `.addcategory <category name>`
- `.addacct <category> <acct>`
- `.rmcategory <category>
- `.rmacct <category> <acct>`

I would like there to be a system in which everyone can submit requests to add accounts or categories, but only a moderator / admin can approve it. This is certainly on the backlog.

## Deployment
Backend will need to be a database such that there are categories, accounts, and then the ID of last tweet shown. When adding a new account, the last tweet should be printed to the appropriate discord channel and the storage / watch starts with *that* Tweet ID.
On Discord itself, there will be a category strictly for tweetsoft with a channel devoted to each category, which one channel being devoted to configuration. This configuration will be those four Planned Usage commands and any other settings/commands added in the future. The tweetsoft category and configuration channel should be created upon joining the server.
