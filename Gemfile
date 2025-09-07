source "https://rubygems.org"
gem "jekyll", "~> 4.4.1"

# Standard library gems for Ruby 3.3.6+ compatibility
gem "csv"
gem "base64"
gem "bigdecimal"

group :jekyll_plugins do
  gem 'jekyll-feed'
  gem 'jekyll-seo-tag'
  gem 'jekyll-sitemap'
  gem 'jemoji'
end

# Windows and JRuby does not include zoneinfo files, so bundle the tzinfo-data gem
# and associated library.
install_if -> { RUBY_PLATFORM =~ %r!mingw|mswin|java! } do
  gem "tzinfo", "~> 1.2"
  gem "tzinfo-data"
end

# Performance-booster for watching directories on Windows
gem "wdm", "~> 0.2.0", :install_if => Gem.win_platform?
gem "webrick", "~> 1.7"
