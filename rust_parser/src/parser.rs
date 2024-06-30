use crate::ast::*;

#[derive(pest_derive::Parser)]
#[grammar = "../icfp.pest"]
pub struct ICFPParser;

pub fn parse(parse_tree: pest::iterators::Pair<Rule>) -> anyhow::Result<Expr> {
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
            if let Expr::Value(value) = parse(inner.next().unwrap())? {
                Ok(Expr::Unary(Unary {
                    op,
                    val: value,
                }))
            } else {
                anyhow::bail!("Unary inner parsed to non-value type.")
            }
        }
        Rule::binary => {
            let mut inner = parse_tree.into_inner();
            Ok(Expr::Binary(Binary {
                op: BinaryOp::from_str(inner.next().unwrap().as_str()),
                first: Box::new(parse(inner.next().unwrap())?),
                second: Box::new(parse(inner.next().unwrap())?),
            }))
        }
        Rule::r#if => {
            let mut inner = parse_tree.into_inner();
            Ok(Expr::If(If {
                condition: Box::new(parse(inner.next().unwrap())?),
                if_true: Box::new(parse(inner.next().unwrap())?),
                if_false: Box::new(parse(inner.next().unwrap())?),
            }))
        }
        Rule::lambda => {
            let mut inner = parse_tree.into_inner();
            Ok(Expr::Lambda(Lambda {
                body: Value::decode_integer_body(inner.next().unwrap().as_str()),
                arg: Box::new(parse(inner.next().unwrap())?),
            }))
        }
        Rule::variable => {
            let mut inner = parse_tree.into_inner();
            Ok(Expr::Variable(Variable(Value::decode_integer_body(
                inner.next().unwrap().as_str(),
            ))))
        }
        _ => panic!("Unexpected rule found: {:#?}", parse_tree),
    }
}

