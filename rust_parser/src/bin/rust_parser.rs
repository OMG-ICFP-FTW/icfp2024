use std::fs;
use std::path;

use clap::Parser;

use rust_parser::*;

#[derive(clap::Parser, Debug)]
#[command(author, version, about, long_about = None, arg_required_else_help = true)]
struct Args {
    #[arg(long)]
    input: path::PathBuf,
    // #[arg(long)]
    // output: path::PathBuf,
}

#[derive(pest_derive::Parser)]
#[grammar = "../icfp.pest"]
struct ICFPParser;

fn parse(parse_tree: pest::iterators::Pair<Rule>) -> anyhow::Result<Expr> {
    match parse_tree.as_rule() {
        Rule::string => Ok(Expr::Value(Value::decode(
            parse_tree.into_inner().next().unwrap().as_str(),
        ))),
        Rule::integer => todo!("integer"),
        Rule::boolean => todo!("boolean"),
        Rule::unary => todo!("unary"),
        Rule::binary => {
            let mut inner = parse_tree.into_inner();
            Ok(Expr::Binary(Binary {
                op: BinaryOp::from_str(inner.next().unwrap().as_str()),
                first: Box::new(parse(inner.next().unwrap())?),
                second: Box::new(parse(inner.next().unwrap())?),
            }))
        }
        Rule::r#if => todo!(),
        Rule::lambda => todo!(),
        Rule::variable => todo!(),
        Rule::expr => todo!(),
        _ => unimplemented!(),
    }
}

fn main() {
    let args = Args::parse();

    let input_icfp = fs::read_to_string(&args.input).unwrap();
    let mut parse_result = <ICFPParser as pest::Parser<_>>::parse(Rule::expr, &input_icfp).unwrap();

    let parse_tree = parse_result.next().unwrap();
    let ast = parse(parse_tree);
    println!("AST: {:?}", ast);
}
