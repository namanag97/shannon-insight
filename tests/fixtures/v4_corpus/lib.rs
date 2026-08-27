use std::collections::HashMap;

pub struct Registry {
    items: HashMap<String, i32>,
}

impl Registry {
    pub fn new() -> Self {
        Registry { items: HashMap::new() }
    }

    pub fn add(&mut self, key: String, value: i32) {
        if value > 0 {
            self.items.insert(key, value);
        }
    }
}

fn helper(x: i32) -> i32 {
    todo!()
}
