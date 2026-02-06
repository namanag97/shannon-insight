// Sample Rust file for testing tree-sitter parsing.

use std::fmt;
use std::io::{self, Write};

pub trait Greeter {
    fn greet(&self, name: &str) -> String;
}

pub struct HelloGreeter {
    prefix: String,
}

impl HelloGreeter {
    pub fn new(prefix: &str) -> Self {
        HelloGreeter {
            prefix: prefix.to_string(),
        }
    }
}

impl Greeter for HelloGreeter {
    fn greet(&self, name: &str) -> String {
        format!("{}, {}!", self.prefix, name)
    }
}

pub enum Status {
    Active,
    Inactive,
    Pending(u32),
}

fn process_data(data: &[i32]) -> i32 {
    let mut sum = 0;
    for &v in data {
        if v > 0 {
            for i in 0..v {
                sum += i;
            }
        }
    }
    sum
}

fn main() {
    let g = HelloGreeter::new("Hello");
    println!("{}", g.greet("World"));
}
