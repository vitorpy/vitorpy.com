require 'date'
require 'fileutils'

desc "Create a new post"
task :new_post do
  # Get title from environment or prompt
  title = ENV['title']
  
  if title.nil? || title.empty?
    print "Enter post title: "
    title = STDIN.gets.chomp
  end
  
  if title.empty?
    puts "Error: Title cannot be empty"
    exit 1
  end
  
  # Generate filename
  date = Date.today.strftime('%Y-%m-%d')
  slug = title.downcase.strip.gsub(' ', '-').gsub(/[^\w-]/, '')
  filename = "_posts/#{date}-#{slug}.md"
  
  # Check if file already exists
  if File.exist?(filename)
    puts "Error: #{filename} already exists"
    exit 1
  end
  
  # Ensure _posts directory exists
  FileUtils.mkdir_p('_posts')
  
  # Create post with front matter
  File.open(filename, 'w') do |file|
    file.puts "---"
    file.puts "layout: post"
    file.puts "title: \"#{title}\""
    file.puts "date: #{DateTime.now.strftime('%Y-%m-%d %H:%M:%S %z')}"
    file.puts "categories: blog"
    file.puts "---"
    file.puts
    file.puts "Your content here..."
  end
  
  puts "Created new post: #{filename}"
  puts "Run 'bundle exec jekyll serve' to preview"
end

desc "Create a new draft"
task :new_draft do
  title = ENV['title']
  
  if title.nil? || title.empty?
    print "Enter draft title: "
    title = STDIN.gets.chomp
  end
  
  if title.empty?
    puts "Error: Title cannot be empty"
    exit 1
  end
  
  # Generate filename (no date for drafts)
  slug = title.downcase.strip.gsub(' ', '-').gsub(/[^\w-]/, '')
  filename = "_drafts/#{slug}.md"
  
  # Check if file already exists
  if File.exist?(filename)
    puts "Error: #{filename} already exists"
    exit 1
  end
  
  # Ensure _drafts directory exists
  FileUtils.mkdir_p('_drafts')
  
  # Create draft with front matter
  File.open(filename, 'w') do |file|
    file.puts "---"
    file.puts "layout: post"
    file.puts "title: \"#{title}\""
    file.puts "categories: blog"
    file.puts "---"
    file.puts
    file.puts "Draft content here..."
  end
  
  puts "Created new draft: #{filename}"
  puts "Run 'bundle exec jekyll serve --drafts' to preview"
end

desc "List all posts"
task :list_posts do
  posts = Dir.glob("_posts/*.md").sort.reverse
  
  if posts.empty?
    puts "No posts found"
  else
    puts "Posts (#{posts.count}):"
    posts.each do |post|
      # Extract title from front matter
      content = File.read(post)
      title_match = content.match(/^title:\s*["']?(.+?)["']?\s*$/m)
      title = title_match ? title_match[1] : "Untitled"
      
      filename = File.basename(post)
      puts "  #{filename} - #{title}"
    end
  end
end

desc "List all drafts"
task :list_drafts do
  drafts = Dir.glob("_drafts/*.md").sort
  
  if drafts.empty?
    puts "No drafts found"
  else
    puts "Drafts (#{drafts.count}):"
    drafts.each do |draft|
      # Extract title from front matter
      content = File.read(draft)
      title_match = content.match(/^title:\s*["']?(.+?)["']?\s*$/m)
      title = title_match ? title_match[1] : "Untitled"
      
      filename = File.basename(draft)
      puts "  #{filename} - #{title}"
    end
  end
end

desc "Publish a draft"
task :publish_draft do
  drafts = Dir.glob("_drafts/*.md")
  
  if drafts.empty?
    puts "No drafts to publish"
    exit 1
  end
  
  # List drafts
  puts "Select a draft to publish:"
  drafts.each_with_index do |draft, index|
    content = File.read(draft)
    title_match = content.match(/^title:\s*["']?(.+?)["']?\s*$/m)
    title = title_match ? title_match[1] : "Untitled"
    puts "  #{index + 1}. #{File.basename(draft)} - #{title}"
  end
  
  print "Enter number: "
  selection = STDIN.gets.chomp.to_i
  
  if selection < 1 || selection > drafts.length
    puts "Invalid selection"
    exit 1
  end
  
  draft = drafts[selection - 1]
  
  # Generate new filename with date
  date = Date.today.strftime('%Y-%m-%d')
  basename = File.basename(draft)
  new_filename = "_posts/#{date}-#{basename}"
  
  # Update date in front matter
  content = File.read(draft)
  content.sub!(/^(---.+?)(\n---)/m) do |match|
    front_matter = $1
    # Add or update date
    if front_matter.include?('date:')
      front_matter.sub!(/^date:.*$/m, "date: #{DateTime.now.strftime('%Y-%m-%d %H:%M:%S %z')}")
    else
      front_matter += "\ndate: #{DateTime.now.strftime('%Y-%m-%d %H:%M:%S %z')}"
    end
    "#{front_matter}\n---"
  end
  
  # Ensure _posts directory exists
  FileUtils.mkdir_p('_posts')
  
  # Write to new location
  File.write(new_filename, content)
  
  # Delete draft
  File.delete(draft)
  
  puts "Published: #{draft} -> #{new_filename}"
end