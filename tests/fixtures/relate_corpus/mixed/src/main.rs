mod config;
mod types;
mod util;

use crate::config::LIMIT;
use crate::types::Id;
use crate::util::run;

fn main() {
    let _: Id = run(LIMIT);
}
