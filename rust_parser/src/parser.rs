use std::cell::RefCell;
use std::collections::BTreeMap;
use std::rc::Rc;

use crate::ast::*;

#[derive(pest_derive::Parser)]
#[grammar = "../icfp.pest"]
pub struct ICFPParser;

///
/// `unique_scope` counts down as all "natural" scopes are positive integers
pub fn parse(
    parse_tree: pest::iterators::Pair<Rule>,
    scope_rewrites: &BTreeMap<i64, i64>,
    unique_scope: Rc<RefCell<i64>>,
) -> anyhow::Result<Expr> {
    match parse_tree.as_rule() {
        Rule::string => Ok(Expr::Value(Value::decode_string(
            parse_tree.into_inner().next().unwrap().as_str(),
        ))),
        Rule::integer => {
            let mut inner = parse_tree.into_inner();
            Ok(Expr::Value(Value::decode_integer(
                inner.next().unwrap().as_str(),
            )))
        }
        Rule::boolean => {
            let mut inner = parse_tree.into_inner();
            Ok(Expr::Value(Value::Bool(
                inner.next().unwrap().as_str() == "T",
            )))
        }
        Rule::unary => {
            let mut inner = parse_tree.into_inner();
            let op = UnaryOp::from_str(inner.next().unwrap().as_str());
            Ok(Expr::Unary(Unary {
                op,
                val: Box::new(parse(
                    inner.next().unwrap(),
                    scope_rewrites,
                    Rc::clone(&unique_scope),
                )?),
            }))
        }
        Rule::binary => {
            let mut inner = parse_tree.into_inner();
            Ok(Expr::Binary(Binary {
                op: BinaryOp::from_str(inner.next().unwrap().as_str()),
                first: Box::new(parse(
                    inner.next().unwrap(),
                    scope_rewrites,
                    Rc::clone(&unique_scope),
                )?),
                second: Box::new(parse(
                    inner.next().unwrap(),
                    scope_rewrites,
                    Rc::clone(&unique_scope),
                )?),
            }))
        }
        Rule::r#if => {
            let mut inner = parse_tree.into_inner();
            Ok(Expr::If(If {
                condition: Box::new(parse(
                    inner.next().unwrap(),
                    scope_rewrites,
                    Rc::clone(&unique_scope),
                )?),
                if_true: Box::new(parse(
                    inner.next().unwrap(),
                    scope_rewrites,
                    Rc::clone(&unique_scope),
                )?),
                if_false: Box::new(parse(
                    inner.next().unwrap(),
                    scope_rewrites,
                    Rc::clone(&unique_scope),
                )?),
            }))
        }
        Rule::lambda => {
            let mut inner = parse_tree.into_inner();
            let id = Value::decode_integer_body(inner.next().unwrap().as_str());
            let rewrite_id = *unique_scope.borrow();
            *unique_scope.borrow_mut() = rewrite_id - 1;
            let mut rewrites = scope_rewrites.clone();
            rewrites.insert(id, rewrite_id);
            Ok(Expr::Lambda(Lambda {
                body: rewrite_id,
                arg: Box::new(parse(
                    inner.next().unwrap(),
                    &rewrites,
                    Rc::clone(&unique_scope),
                )?),
            }))
        }
        Rule::variable => {
            let mut inner = parse_tree.into_inner();
            let source_id = Value::decode_integer_body(inner.next().unwrap().as_str());
            // Rewrite scoped variables to "statically" implement capture-avoiding substitution
            let id: i64 = *scope_rewrites.get(&source_id).unwrap_or(&source_id);
            Ok(Expr::Variable(Variable(id)))
        }
        _ => panic!("Unexpected rule found: {:#?}", parse_tree),
    }
}
