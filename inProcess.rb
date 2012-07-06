
# ===========
# = Command =
# ===========
#
# addtodobeta.rb path/to/file.txt

# ===============
# = File Format =
# ===============
# assignment
# assignment
# assignment
# ...

require 'rubygems'
require 'appscript'
require 'date'
require 'active_support/all'

file = '/Users/Adam/Dropbox/Dump/sxTestInbox.md'

File.open(file).readlines.each do |line|
  
  if line.chomp.start_with?('!- ')
    Appscript.app('OmniFocus').default_document.make(:new => :inbox_task, 
                                  :with_properties => {name: line.chomp[3..-1]})
  end
  
end
