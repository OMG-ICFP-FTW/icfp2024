use std::collections::HashMap;

use crate::ast::*;

pub struct Executor {
    pub variables: HashMap<i64, Expr>,
}

impl Executor {
    pub fn step(&mut self, pgm: Box<Expr>) -> Box<Expr> {
        match *pgm {
            Expr::Value(val) => Box::new(Expr::Value(val)),
            Expr::Unary(Unary { op, val }) => self.eval_unary(op, val),
            Expr::Binary(Binary { op, first, second }) => self.eval_binary(op, first, second),
            Expr::Lambda(lambda) => Box::new(Expr::Lambda(lambda)),
            Expr::If(If {
                condition,
                if_true,
                if_false,
            }) => self.eval_if(condition, if_true, if_false),
            Expr::Variable(var) => Box::new(Expr::Variable(var)),
        }
    }

    pub fn eval_binary(&mut self, op: BinaryOp, first: Box<Expr>, second: Box<Expr>) -> Box<Expr> {
        todo!("apply_binary")
    }

    pub fn eval_unary(&mut self, op: UnaryOp, val: Value) -> Box<Expr> {
        match op {
            UnaryOp::Neg => match val {
                Value::Int(i) => Box::new(Expr::Value(Value::Int(-i))),
                _ => panic!("Negation operator received a non-integer value"),
            },
            UnaryOp::Not => match val {
                Value::Bool(b) => Box::new(Expr::Value(Value::Bool(!b))),
                _ => panic!("Negation operator received a non-boolean value"),
            },
            UnaryOp::StrToInt => match val {
                Value::Str(s) => Box::new(Expr::Value(Value::Int(Value::decode_integer_body(
                    &Value::encode_string(&s),
                )))),
                _ => panic!("Str to str operator received a non-string value"),
            },
            UnaryOp::IntToStr => match val {
                Value::Int(s) => Box::new(Expr::Value(Value::decode_string(
                    &Value::encode_integer_body(s),
                ))),
                _ => panic!("Int to str operator received a non-integer value"),
            },
        }
    }

    pub fn eval_if(
        &mut self,
        condition: Box<Expr>,
        if_true: Box<Expr>,
        if_false: Box<Expr>,
    ) -> Box<Expr> {
        let mut next = self.step(condition);
        let mut max_iter = 1_000_000;
        while max_iter > 0 {
            match *next {
                Expr::Value(Value::Bool(val)) => {
                    if val {
                        return if_true;
                    } else {
                        return if_false;
                    }
                }
                Expr::Value(_) => {
                    panic!("Found non-boolean terminal")
                }
                _ => (),
            }
            next = self.step(next);
            max_iter -= 1;
        }
        panic!("If conditional never evaluated to a valid boolean value")
    }
}
