require_relative "lib/helper"
require_relative "lib/extra"
require "set"

puts Helper.describe(Set.new[Extra::VALUE])
