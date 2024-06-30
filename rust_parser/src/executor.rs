use std::collections::HashMap;

use crate::ast::*;

pub struct Executor {
    pub variables: HashMap<i64, Box<Expr>>,
}

impl Executor {
    pub fn step(&mut self, pgm: Box<Expr>) -> Box<Expr> {
        // println!("Step evaluating: {:#?}", pgm);
        match *pgm {
            Expr::Value(val) => Box::new(Expr::Value(val)),
            Expr::Unary(Unary { op, val: expr }) => match *expr {
                Expr::Value(val) => self.eval_unary(op, val),
                _ => Box::new(Expr::Unary(Unary {
                    op,
                    val: self.step(expr),
                })),
            },
            Expr::Binary(Binary { op, first, second }) => self.eval_binary(op, first, second),
            Expr::Lambda(lambda) => Box::new(Expr::Lambda(lambda)),
            Expr::If(If {
                condition,
                if_true,
                if_false,
            }) => self.eval_if(condition, if_true, if_false),
            Expr::Variable(Variable(id)) => {
                let expr = self
                    .variables
                    .get(&id)
                    .expect("ID not yet present at variable evaluation time")
                    .clone();
                // println!("Variable evaluated to {:#?}", expr);
                expr
            }
        }
    }

    pub fn eval_binary(&mut self, op: BinaryOp, first: Box<Expr>, second: Box<Expr>) -> Box<Expr> {
        match op {
            BinaryOp::Apply => match *first {
                Expr::Lambda(Lambda { body, arg }) => {
                    self.variables.insert(body, second);
                    arg
                }
                Expr::Value(val) => panic!("Apply operator received a non-lambda value: {:?}", val),
                val @ _ => Box::new(Expr::Binary(Binary {
                    op,
                    first: self.step(Box::new(val)),
                    second,
                })),
            },
            _ => match (*first, *second) {
                (Expr::Value(first_val), Expr::Value(second_val)) => match op {
                    BinaryOp::Add => match (first_val, second_val) {
                        (Value::Int(one), Value::Int(two)) => {
                            Box::new(Expr::Value(Value::Int(one + two)))
                        }
                        _ => panic!("Addition operator received a non-integer value"),
                    },
                    BinaryOp::Sub => match (first_val, second_val) {
                        (Value::Int(one), Value::Int(two)) => {
                            Box::new(Expr::Value(Value::Int(one - two)))
                        }
                        _ => panic!("Subtraction operator received a non-integer value"),
                    },
                    BinaryOp::Mult => match (first_val, second_val) {
                        (Value::Int(one), Value::Int(two)) => {
                            Box::new(Expr::Value(Value::Int(one * two)))
                        }
                        _ => panic!("Multiplication operator received a non-integer value"),
                    },
                    BinaryOp::Div => match (first_val, second_val) {
                        (Value::Int(one), Value::Int(two)) => {
                            Box::new(Expr::Value(Value::Int(one / two)))
                        }
                        _ => panic!("Dividing operator received a non-integer value"),
                    },
                    BinaryOp::Mod => match (first_val, second_val) {
                        (Value::Int(one), Value::Int(two)) => {
                            Box::new(Expr::Value(Value::Int(one % two)))
                        }
                        _ => panic!("Modulo operator received a non-integer value"),
                    },
                    BinaryOp::Lt => match (first_val, second_val) {
                        (Value::Int(one), Value::Int(two)) => {
                            Box::new(Expr::Value(Value::Bool(one < two)))
                        }
                        _ => panic!("Less than operator received a non-integer value"),
                    },
                    BinaryOp::Gt => match (first_val, second_val) {
                        (Value::Int(one), Value::Int(two)) => {
                            Box::new(Expr::Value(Value::Bool(one > two)))
                        }
                        _ => panic!("Great than operator received a non-integer value"),
                    },
                    BinaryOp::Eq => match (first_val, second_val) {
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
                    BinaryOp::Or => match (first_val, second_val) {
                        (Value::Bool(one), Value::Bool(two)) => {
                            Box::new(Expr::Value(Value::Bool(one | two)))
                        }
                        _ => panic!("Or operator received a non-boolean value"),
                    },
                    BinaryOp::And => match (first_val, second_val) {
                        (Value::Bool(one), Value::Bool(two)) => {
                            Box::new(Expr::Value(Value::Bool(one & two)))
                        }
                        _ => panic!("And operator received a non-boolean value"),
                    },
                    BinaryOp::Cat => match (first_val, second_val) {
                        (Value::Str(one), Value::Str(two)) => {
                            Box::new(Expr::Value(Value::Str(format!("{}{}", one, two))))
                        }
                        _ => panic!("Concatenation operator received a non-string value"),
                    },
                    BinaryOp::Take => match (first_val, second_val) {
                        (Value::Int(one), Value::Str(two)) => {
                            Box::new(Expr::Value(Value::Str(two[..(one as usize)].to_string())))
                        }
                        _ => panic!("Take operator received a the wrong types"),
                    },
                    BinaryOp::Drop => match (first_val, second_val) {
                        (Value::Int(one), Value::Str(two)) => {
                            Box::new(Expr::Value(Value::Str(two[(one as usize)..].to_string())))
                        }
                        _ => panic!("Drop operator received a the wrong types"),
                    },
                    BinaryOp::Apply => unreachable!(),
                },
                (Expr::Value(first_val), second) => {
                    return Box::new(Expr::Binary(Binary {
                        op,
                        first: Box::new(Expr::Value(first_val)),
                        second: self.step(Box::new(second)),
                    }))
                }
                (first, second) => {
                    return Box::new(Expr::Binary(Binary {
                        op,
                        first: self.step(Box::new(first)),
                        second: Box::new(second),
                    }))
                }
            },
        }
    }

    pub fn maximally_evaluate(&mut self, expression: Box<Expr>) -> Box<Expr> {
        let mut next = self.step(expression);
        let mut max_iter = 1_000_000;
        while max_iter > 0 {
            match *next {
                Expr::Value(_) | Expr::Lambda(_) | Expr::Variable(_) => return next,
                _ => (),
            }
            next = self.step(next);
            max_iter -= 1;
        }
        panic!("Maximal evaluation failed to resolve to a valid semi-terminal value: final state = {:?}", next)
    }

    pub fn fully_evaluate(&mut self, expression: Box<Expr>) -> Value {
        let mut next = self.step(expression);
        let max_iter = 1_000_000;
        let mut i = 0;
        while i < max_iter {
            match *next {
                Expr::Value(val) => return val,
                _ => (),
            }
            next = self.step(next);
            i += 1;
        }
        panic!(
            "Full evaluation failed to resolve to a terminal value: final state = {:#?}",
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

#[cfg(test)]
mod tests {
    use std::fs;

    use std::cell::RefCell;
    use std::collections::BTreeMap;
    use std::rc::Rc;

    use lazy_static::lazy_static;

    use super::*;

    lazy_static! {
        static ref INPUT_TO_OUTPUT: Vec<(String, String)> = {
            let inputs = fs::read_to_string("tests/inputs.icfp").unwrap();
            let outputs = fs::read_to_string("tests/outputs.txt").unwrap();

            inputs
                .lines()
                .filter(|s| !s.starts_with("#"))
                .map(|s| s.trim().to_string())
                .zip(
                    outputs
                        .lines()
                        .filter(|s| !s.starts_with("#"))
                        .map(|s| s.trim().to_string()),
                )
                .collect()
        };
    }

    #[test]
    fn executor_test() {
        for (input, expected) in INPUT_TO_OUTPUT.iter() {
            let mut parse_result = <crate::parser::ICFPParser as pest::Parser<_>>::parse(
                crate::parser::Rule::expr,
                input,
            )
            .unwrap();

            let parse_tree = parse_result.next().unwrap();
            let rewrites = BTreeMap::new();
            let unique_scope = Rc::new(RefCell::new(-1));
            let ast =
                Box::new(crate::parser::parse(parse_tree, &rewrites, unique_scope, true).unwrap());

            let mut executor = Executor {
                variables: HashMap::new(),
            };
            let actual = executor.fully_evaluate(ast);
            let stringified = match actual {
                Value::Bool(val) => serde_json::to_string(&val).unwrap(),
                Value::Str(val) => serde_json::to_string(&val).unwrap(),
                Value::Int(val) => serde_json::to_string(&val).unwrap(),
            };

            assert_eq!(expected, &stringified, "input={}", input);
        }
    }
}
