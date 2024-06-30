use std::collections::HashMap;

use lazy_static::lazy_static;

use serde::{Deserialize, Serialize};

#[derive(Clone, Serialize, Deserialize, Debug, PartialEq, PartialOrd, Hash)]
pub enum Value {
    Str(String),
    Bool(bool),
    Int(i64),
}

static TARGET: &'static str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`|~ \n";
impl Value {
    pub fn decode_string(encoded: &str) -> Value {
        lazy_static! {
            static ref DECODE_TRANSLATION_TABLE: HashMap<char, char> = TARGET
                .chars()
                .zip((33..(33 + TARGET.len() as u32)).map(|c| c as u8 as char))
                .map(|(k, v)| (v, k))
                .collect();
        }
        Value::Str(
            encoded
                .chars()
                .map(|c| *DECODE_TRANSLATION_TABLE.get(&c).unwrap_or(&c))
                .collect(),
        )
    }

    pub fn encode_string(source: &str) -> String {
        lazy_static! {
            static ref ENCODE_TRANSLATION_TABLE: HashMap<char, char> = TARGET
                .chars()
                .zip((33..(33 + TARGET.len() as u32)).map(|c| c as u8 as char))
                .collect();
        }

        source
            .chars()
            .map(|c| *ENCODE_TRANSLATION_TABLE.get(&c).unwrap_or(&c))
            .collect()
    }

    pub fn decode_integer(encoded: &str) -> Value {
        Value::Int(Value::decode_integer_body(encoded))
    }

    pub fn encode_integer_body(mut i: i64) -> String {
        lazy_static! {
            static ref BASE94_CHARS: Vec<char> = (33..127).map(|c| c as u8 as char).collect();
        }

        // Edge case: if number is 0, return the corresponding base 94 character ('!')
        if i == 0 {
            return BASE94_CHARS[0].to_string();
        }

        let mut result = Vec::new();

        while i > 0 {
            let remainder = (i % 94) as usize;
            result.push(BASE94_CHARS[remainder]);
            i /= 94;
        }

        // Reverse the result because characters were appended in reverse order
        result.iter().rev().collect()
    }

    pub fn decode_integer_body(encoded: &str) -> i64 {
        lazy_static! {
            static ref CHAR_TO_VALUE: std::collections::HashMap<char, i64> = {
                // Define the base 94 characters
                let base94_chars: Vec<char> = (33..127).map(|c| c as u8 as char).collect();
                // Create a reverse lookup map from characters to their indices (values)
                let char_to_value: std::collections::HashMap<char, i64> = base94_chars
                    .iter()
                    .enumerate()
                    .map(|(idx, &ch)| (ch, idx as i64))
                    .collect();
                char_to_value
            };
        }

        let mut result = 0_i64;
        let mut power = 1_i64;
        for ch in encoded.chars().rev() {
            if let Some(&value) = CHAR_TO_VALUE.get(&ch) {
                result += value * power;
                power *= 94;
            } else {
                panic!("character in base-94 encoding unrecognized when decoding integer body ({}): '{}'", encoded, ch);
            }
        }

        result
    }
}

#[cfg(test)]
mod decode_test {
    use super::*;

    #[test]
    fn string() {
        assert_eq!(
            Value::Str("get index".to_string()),
            Value::decode_string("'%4}).$%8")
        );
    }

    #[test]
    fn integer() {
        assert_eq!(1337_i64, Value::decode_integer_body("/6"));
    }
}

#[derive(Clone, Serialize, Deserialize, Debug, PartialEq, PartialOrd, Hash)]
pub enum UnaryOp {
    Neg,
    Not,
    StrToInt,
    IntToStr,
}

impl UnaryOp {
    pub fn from_str(source: &str) -> UnaryOp {
        match source {
            "-" => UnaryOp::Neg,
            "!" => UnaryOp::Not,
            "#" => UnaryOp::StrToInt,
            "$" => UnaryOp::IntToStr,
            _ => unimplemented!(),
        }
    }
}

#[derive(Clone, Serialize, Deserialize, Debug, PartialEq, PartialOrd, Hash)]
pub struct Unary {
    pub op: UnaryOp,
    pub val: Value,
}

#[derive(Clone, Serialize, Deserialize, Debug, PartialEq, PartialOrd, Hash)]
pub enum BinaryOp {
    Add,
    Sub,
    Mult,
    Div,
    Mod,
    Lt,
    Gt,
    Eq,
    Or,
    And,
    Cat,
    Take,
    Drop,
    Apply,
}

impl BinaryOp {
    pub fn as_str(&self) -> &'static str {
        match self {
            BinaryOp::Add => "+",
            BinaryOp::Sub => "-",
            BinaryOp::Mult => "*",
            BinaryOp::Div => "/",
            BinaryOp::Mod => "%",
            BinaryOp::Lt => "<",
            BinaryOp::Gt => ">",
            BinaryOp::Eq => "=",
            BinaryOp::Or => "|",
            BinaryOp::And => "&",
            BinaryOp::Cat => ".",
            BinaryOp::Take => "T",
            BinaryOp::Drop => "D",
            BinaryOp::Apply => "$",
        }
    }

    pub fn from_str(source: &str) -> BinaryOp {
        match source {
            "+" => BinaryOp::Add,
            "-" => BinaryOp::Sub,
            "*" => BinaryOp::Mult,
            "/" => BinaryOp::Div,
            "%" => BinaryOp::Mod,
            "<" => BinaryOp::Lt,
            ">" => BinaryOp::Gt,
            "=" => BinaryOp::Eq,
            "|" => BinaryOp::Or,
            "&" => BinaryOp::And,
            "." => BinaryOp::Cat,
            "T" => BinaryOp::Take,
            "D" => BinaryOp::Drop,
            "$" => BinaryOp::Apply,
            _ => unimplemented!(),
        }
    }

    pub fn from_name(name: &str) -> BinaryOp {
        match name {
            "add" => BinaryOp::Add,
            "sub" => BinaryOp::Sub,
            "mult" => BinaryOp::Mult,
            "div" => BinaryOp::Div,
            "mod" => BinaryOp::Mod,
            "lt" => BinaryOp::Lt,
            "gt" => BinaryOp::Gt,
            "eq" => BinaryOp::Eq,
            "or" => BinaryOp::Or,
            "and" => BinaryOp::And,
            "cat" => BinaryOp::Cat,
            "take" => BinaryOp::Take,
            "drop" => BinaryOp::Drop,
            "apply" => BinaryOp::Apply,
            _ => unimplemented!(),
        }
    }
}

#[derive(Clone, Serialize, Deserialize, Debug, PartialEq, PartialOrd, Hash)]
pub struct Binary {
    pub op: BinaryOp,
    pub first: Box<Expr>,
    pub second: Box<Expr>,
}

#[derive(Clone, Serialize, Deserialize, Debug, PartialEq, PartialOrd, Hash)]
pub struct If {
    pub condition: Box<Expr>,
    pub if_true: Box<Expr>,
    pub if_false: Box<Expr>,
}

#[derive(Clone, Serialize, Deserialize, Debug, PartialEq, PartialOrd, Hash)]
pub struct Lambda {
    pub body: i64,
    pub arg: Box<Expr>,
}

#[derive(Clone, Serialize, Deserialize, Debug, PartialEq, PartialOrd, Hash)]
pub struct Variable(pub i64);

#[derive(Clone, Serialize, Deserialize, Debug, PartialEq, PartialOrd, Hash)]
pub enum Expr {
    Value(Value),
    Unary(Unary),
    Binary(Binary),
    Lambda(Lambda),
    If(If),
    Variable(Variable),
}
