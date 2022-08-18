# tweetsoft
Discord Bot for Modular Twitter Feeds

## How it works
- Categories
- Accounts
- Adding and Removing
- Quick Response Times (1m)

## Usage
- `.addacct <channel> <acct>`
- `.rmacct <channel> <acct>`

## Deployment
Backend will need to be a database such that there are categories, accounts, and then the ID of last tweet shown. When adding a new account, the last tweet should be printed to the appropriate discord channel and the storage / watch starts with *that* Tweet ID.
