# Sample Ruby file for testing tree-sitter parsing.

require 'json'
require_relative './helper'

module Greetable
  def greet(name)
    raise NotImplementedError
  end
end

class HelloGreeter
  include Greetable

  def initialize(prefix = 'Hello')
    @prefix = prefix
  end

  def greet(name)
    "#{@prefix}, #{name}!"
  end

  private

  def helper
    puts 'helper'
  end
end

class DataProcessor
  def process_data(data)
    sum = 0
    data.each do |v|
      if v > 0
        (0...v).each do |i|
          sum += i
        end
      end
    end
    sum
  end
end

def standalone_function(x)
  x * 2
end

if __FILE__ == $PROGRAM_NAME
  g = HelloGreeter.new
  puts g.greet('World')
end
