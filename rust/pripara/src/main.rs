extern crate serde_json;

use std::env;
use std::io::Read;
use std::fs::File;
use serde_json::{Value, Error};


struct Config {
    password: Option<String>,
    email: Option<String>,
}

impl Config {
    fn new() -> Config {
        Config {
            password: None,
            email: None,
        }
    }

    fn load(&mut self) {
        self.password = env::var("PRIPARA_PASSWORD").ok();
        self.email = env::var("PRIPARA_EMAIL").ok();
        if self.password.is_some() && self.email.is_some() {
            return
        }
        let config = Self::read_config();
        self.password = config.0;
        self.email = config.1;
    }

    fn read_config() -> (Option<String>, Option<String>) {
        match File::open("config.json") {
            Ok(mut f) => {
                let mut body = String::new();
                match f.read_to_string(&mut body) {
                    Ok(_) => {
                        let v: Value = serde_json::from_str(body.as_str()).unwrap();
                        (Some(v["password"].to_string()), Some(v["email"].to_string()))
                    },
                    Err(e) => (None, None),
                }
            },
            Err(e) => (None, None),
        }
    }

    fn write_config() {
    }
}

fn main() {
}
