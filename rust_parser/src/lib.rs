use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Debug)]
pub enum Value {
    Str(String),
    Bool(bool),
    Int(i64),
}

#[derive(Serialize, Deserialize, Debug)]
pub enum UnaryOp {
    Neg,
    Not,
    StrToInt,
    IntToStr,
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
    fn as_str(&self) -> &'static str {
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

    fn from_str(source: &str) -> BinaryOp {
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
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Binary {
    pub op: BinaryOp,
    pub first: Value,
    pub second: Value,
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
pub struct Variable(i64);

#[derive(Serialize, Deserialize, Debug)]
pub enum Expr {
    Value(Value),
    Unary(Unary),
    Binary(Binary),
    Lambda(Lambda),
    If(If),
    Variable(Variable),
}
