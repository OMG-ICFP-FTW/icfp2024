use std::collections::HashMap;

use crate::ast::*;

pub struct Executor {
    pub variables: HashMap<i64, Box<Expr>>,
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
            Expr::Variable(Variable(id)) => self
                .variables
                .get(&id)
                .expect("ID not yet present at variable evaluation time")
                .clone(),
        }
    }

    pub fn eval_binary(&mut self, op: BinaryOp, first: Box<Expr>, second: Box<Expr>) -> Box<Expr> {
        match op {
            BinaryOp::Add => match (self.fully_evaluate(first), self.fully_evaluate(second)) {
                (Value::Int(one), Value::Int(two)) => Box::new(Expr::Value(Value::Int(one + two))),
                _ => panic!("Addition operator received a non-integer value"),
            },
            BinaryOp::Sub => match (self.fully_evaluate(first), self.fully_evaluate(second)) {
                (Value::Int(one), Value::Int(two)) => Box::new(Expr::Value(Value::Int(one - two))),
                _ => panic!("Subtraction operator received a non-integer value"),
            },
            BinaryOp::Mult => match (self.fully_evaluate(first), self.fully_evaluate(second)) {
                (Value::Int(one), Value::Int(two)) => Box::new(Expr::Value(Value::Int(one * two))),
                _ => panic!("Multiplication operator received a non-integer value"),
            },
            BinaryOp::Div => match (self.fully_evaluate(first), self.fully_evaluate(second)) {
                (Value::Int(one), Value::Int(two)) => Box::new(Expr::Value(Value::Int(one / two))),
                _ => panic!("Dividing operator received a non-integer value"),
            },
            BinaryOp::Mod => match (self.fully_evaluate(first), self.fully_evaluate(second)) {
                (Value::Int(one), Value::Int(two)) => Box::new(Expr::Value(Value::Int(one % two))),
                _ => panic!("Modulo operator received a non-integer value"),
            },
            BinaryOp::Lt => match (self.fully_evaluate(first), self.fully_evaluate(second)) {
                (Value::Int(one), Value::Int(two)) => Box::new(Expr::Value(Value::Bool(one < two))),
                _ => panic!("Less than operator received a non-integer value"),
            },
            BinaryOp::Gt => match (self.fully_evaluate(first), self.fully_evaluate(second)) {
                (Value::Int(one), Value::Int(two)) => Box::new(Expr::Value(Value::Bool(one > two))),
                _ => panic!("Great than operator received a non-integer value"),
            },
            BinaryOp::Eq => match (self.fully_evaluate(first), self.fully_evaluate(second)) {
                (Value::Int(one), Value::Int(two)) => {
                    Box::new(Expr::Value(Value::Bool(one == two)))
                }
                (Value::Bool(one), Value::Bool(two)) => {
                    Box::new(Expr::Value(Value::Bool(one == two)))
                }
                (Value::Str(one), Value::Str(two)) => {
                    Box::new(Expr::Value(Value::Bool(one == two)))
                }
                _ => panic!("Equality operator received a non-integer value"),
            },
            BinaryOp::Or => match (self.fully_evaluate(first), self.fully_evaluate(second)) {
                (Value::Bool(one), Value::Bool(two)) => {
                    Box::new(Expr::Value(Value::Bool(one | two)))
                }
                _ => panic!("Or operator received a non-boolean value"),
            },
            BinaryOp::And => match (self.fully_evaluate(first), self.fully_evaluate(second)) {
                (Value::Bool(one), Value::Bool(two)) => {
                    Box::new(Expr::Value(Value::Bool(one & two)))
                }
                _ => panic!("And operator received a non-boolean value"),
            },
            BinaryOp::Cat => match (self.fully_evaluate(first), self.fully_evaluate(second)) {
                (Value::Str(one), Value::Str(two)) => {
                    Box::new(Expr::Value(Value::Str(format!("{}{}", one, two))))
                }
                _ => panic!("Concatenation operator received a non-string value"),
            },
            BinaryOp::Take => match (self.fully_evaluate(first), self.fully_evaluate(second)) {
                (Value::Int(one), Value::Str(two)) => {
                    Box::new(Expr::Value(Value::Str(two[..(one as usize)].to_string())))
                }
                _ => panic!("Take operator received a the wrong types"),
            },
            BinaryOp::Drop => match (self.fully_evaluate(first), self.fully_evaluate(second)) {
                (Value::Int(one), Value::Str(two)) => {
                    Box::new(Expr::Value(Value::Str(two[(one as usize)..].to_string())))
                }
                _ => panic!("Drop operator received a the wrong types"),
            },
            BinaryOp::Apply => {
                let evaluated = self.maximally_evaluate(first);
                match *evaluated {
                    Expr::Lambda(Lambda { body, arg }) => {
                        self.variables.insert(body, second);
                        arg
                    }
                    _ => panic!(
                        "Apply operator received a non-lambda value: {:?}",
                        evaluated
                    ),
                }
            }
        }
    }

    pub fn maximally_evaluate(&mut self, expression: Box<Expr>) -> Box<Expr> {
        let mut next = self.step(expression);
        let mut max_iter = 1_000_000;
        while max_iter > 0 {
            match *next {
                Expr::Unary(_) | Expr::Binary(_) | Expr::If(_) => (),
                _ => return next,
            }
            next = self.step(next);
            max_iter -= 1;
        }
        panic!("Maximal evaluation failed to resolve to a valid semi-terminal value: final state = {:?}", next)
    }

    pub fn fully_evaluate(&mut self, expression: Box<Expr>) -> Value {
        let mut next = self.step(expression);
        let mut max_iter = 1_000_000;
        while max_iter > 0 {
            match *next {
                Expr::Value(val) => return val,
                _ => (),
            }
            next = self.step(next);
            max_iter -= 1;
        }
        panic!(
            "Full evaluation failed to resolve to a terminal value: final state = {:?}",
            next
        )
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
        match self.fully_evaluate(condition) {
            Value::Bool(val) => {
                if val {
                    if_true
                } else {
                    if_false
                }
            }
            _ => {
                panic!("Found non-boolean terminal")
            }
        }
    }
}
