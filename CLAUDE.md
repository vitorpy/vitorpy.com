# Claude Code Instructions

## Ruby/Jekyll Commands

Before running any Ruby or Jekyll commands, you must first run:
```bash
source ~/.rvm/scripts/rvm
rvm use
```

This includes commands like:
- `bundle install`
- `bundle exec jekyll build`
- `bundle exec jekyll serve`
- `rake` tasks

## Common Tasks

### Create a new post
```bash
source ~/.rvm/scripts/rvm
rvm use
rake new_post title="Your Post Title"
```

### Deploy the site
```bash
./deploy.sh
```
The deploy script already includes the necessary rvm commands.

### Extract FontAwesome icons subset
```bash
fontforge -script extract_icons.py
```

## Site Structure

- **Server**: Hosted on Hetzner at 167.235.24.234
- **Local development**: Use `bundle exec jekyll serve`
- **Deployment**: Use `./deploy.sh` to build and sync to server
- **Font subset**: Only 3 FontAwesome icons are used (GitHub, X/Twitter, Bluesky)