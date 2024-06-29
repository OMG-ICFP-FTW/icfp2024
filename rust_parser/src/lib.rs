use std::collections::HashMap;

use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub enum Value {
    Str(String),
    Bool(bool),
    Int(i64),
}

static TARGET: &'static str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`|~ \n";
impl Value {
    pub fn decode_string(encoded: &str) -> Value {
        // TODO(alex): wrap in lazy_static
        let decode_translation_table: HashMap<char, char> = TARGET
            .chars()
            .zip((33..(33 + TARGET.len() as u32)).map(|c| c as u8 as char))
            .collect();
        Value::Str(
            encoded
                .chars()
                .map(|c| *decode_translation_table.get(&c).unwrap_or(&c))
                .collect(),
        )
    }

    pub fn decode_integer(encoded: &str) -> Value {
        Value::Int(Value::decode_integer_body(encoded))
    }

    pub fn decode_integer_body(encoded: &str) -> i64 {
        // TODO(alex): wrap in lazy_static
        // Define the base 94 characters
        let base94_chars: Vec<char> = (33..127).map(|c| c as u8 as char).collect();
        // Create a reverse lookup map from characters to their indices (values)
        let char_to_value: std::collections::HashMap<char, i64> = base94_chars
            .iter()
            .enumerate()
            .map(|(idx, &ch)| (ch, idx as i64))
            .collect();

        let mut result = 0_i64;
        let mut power = 1_i64;
        for ch in encoded.chars().rev() {
            if let Some(&value) = char_to_value.get(&ch) {
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
    fn string() {}

    #[test]
    fn integer() {
        assert_eq!(1337_i64, Value::decode_integer_body("/6"));
    }
}

#[derive(Serialize, Deserialize, Debug)]
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

#[derive(Serialize, Deserialize, Debug)]
pub struct Unary {
    pub op: UnaryOp,
    pub val: Value,
}

#[derive(Serialize, Deserialize, Debug)]
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

#[derive(Serialize, Deserialize, Debug)]
pub struct Binary {
    pub op: BinaryOp,
    pub first: Box<Expr>,
    pub second: Box<Expr>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct If {
    pub condition: Box<Expr>,
    pub if_true: Box<Expr>,
    pub if_false: Box<Expr>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Lambda {
    pub body: i64,
    pub arg: Box<Expr>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Variable(pub i64);

#[derive(Serialize, Deserialize, Debug)]
pub enum Expr {
    Value(Value),
    Unary(Unary),
    Binary(Binary),
    Lambda(Lambda),
    If(If),
    Variable(Variable),
}
