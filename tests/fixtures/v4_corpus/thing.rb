require 'json'

class Thing
  def initialize(name)
    @name = name
  end

  def shout
    if @name.empty?
      '...'
    else
      @name.upcase
    end
  end
end

def top_level_utility(n)
  n * 2
end
