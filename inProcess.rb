#!/usr/bin/env ruby

require 'rubygems'
require 'appscript'
require 'date'
require 'fileutils'
require 'active_support/all' # Get all Rails Functions for Dealing with Dates

# Files and Locations

inboxDirectory = '/Users/Adam/Dropbox/Dump/'
inbox = inboxDirectory+'inbox.md'

inxDirectory = '/Users/Adam/Dropbox/Notes/'
inxStorage   = '/Users/Adam/Dropbox/Library/Logs/inxStorage/'

statsDirectory = '/Users/Adam/Dropbox/Active/DataLogs/'

cooking = '/Users/Adam/Dropbox/Notes/runx Cooking Lessons.md'


# Setup Variables

newItem= false
item = Array.new
i=0
removeBlank=false

output = "# Inbox\n`inbox.md` created "+Time.now.to_formatted_s(:long)+"\n* * * * * * * * * * * * * * * * * * * * * * * * * * * * * *\n"

# Get array of files, starting with `inbox.md` then listing all inx in alphabetical order, then use where in loop
filesToProcess = Array.new

if File.exist?(inbox) then filesToProcess.push(inbox) end

Dir.entries(inxDirectory).each do |f| 
  if f =~ /inx [0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}/
    filesToProcess.push(inxStorage+f)
    FileUtils.mv(inxDirectory+f, inxStorage+f)
  end
end


# Process Each File
filesToProcess.each do |file|
  File.open(file).readlines.each do |line|
  
    if newItem
      if item.first == "Task"
        taskNote=""
        item.drop(2).each { |x| taskNote += x + "\n" } 
        Appscript.app('OmniFocus').default_document.make(:new => :inbox_task, 
                                      :with_properties => {name: item[1], note: taskNote })
                                          
      elsif item.first == "Statistic"
        # puts item.drop(2).each {|x| x}.join(',')
        File.open(statsDirectory+item[1].gsub(/\s+/, "")+".csv", 'a') {|f| f.write(item.drop(2).each {|x| x}.join(',')+"\n")}
      
      elsif item.first == "LifeTrack"
        File.open(statsDirectory+"LifeTrack.txt", 'a') { |f| f.write(item[1]+',"'+item[2]+"\"\n") }
    
      elsif item.first == "Cooking"
        File.open(cooking, 'a').write(item[1])
      end
    
      newItem = false
      item = Array.new
    end
  
    if line.chomp.blank?
      newItem = true
      if ["Task", "Statistic","LifeTrack","Cooking"].include?(item.first)
        removeBlank = true
      end
    end
  
    if line.chomp.start_with?('!- ')                                                      # First Item is a task
      item.push("Task")
      item.push(line.chomp[3..-1].strip)
    elsif ((item.first == "Task") and (line.chomp[0..1] == "* "))                         # Task Note
      item.push(line.chomp.strip)
    elsif (line.chomp =~ /[A-z 0-9]+\. [0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}/)     # Statistic
      item.push("Statistic")
      line.chomp.strip.split('.').each { |x| item.push(x.strip) }
    elsif (line.chomp =~ /Life Track: [0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2} ---/) # Life Track
      item.push("LifeTrack")
      item.push(line.chomp.split(":",2)[1].strip.split(' ---',2)[0]) # Date 
      item.push(line.chomp.split(":",2)[1].strip.split(' ---',2)[1].strip) # Event
    elsif (line.chomp =~ /[0-9]{4}-[0-9]{2}-[0-9]{2} (Breakfast|Lunch|Dinner|Snack|Desert):/) # Cooking Lesson
      item.push("Cooking")
      item.push(line.chomp.strip)
    elsif (line.chomp == "# Inbox" || line.chomp =~ /`inbox.md` created / || line.chomp == "* * * * * * * * * * * * * * * * * * * * * * * * * * * * * *")
      # Do Nothing (Remove Blank)
    elsif !removeBlank
      output += line.chomp+"\n"
    end
  
    removeBlank=false
  
  end
end



# Determine what to do with inbox file
if output.split("\n").count > 3
  File.open(inbox,'w').write(output)
  puts "Remaining items written to `inbox.md`. Process Soon!"
else
  if File.exist?(inbox) then FileUtils.rm(inbox) end 
  puts "Inbox Zero!"
end



File.open(statsDirectory+"inboxProccessLog.md",'a').write(Time.now.to_s+"\n")
