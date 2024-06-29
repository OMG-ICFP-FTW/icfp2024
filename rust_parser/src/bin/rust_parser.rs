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

fn main() {
    let args = Args::parse();

    let input_icfp = fs::read_to_string(&args.input).unwrap();
    let mut parse_result = <ICFPParser as pest::Parser<_>>::parse(Rule::expr, &input_icfp).unwrap();

    let mut program: Vec<Expr> = vec![];
    let mut parse_stack: Vec<pest::iterators::Pair<_>> = vec![parse_result.next().unwrap()];
    while !parse_stack.is_empty() {
        let next = parse_stack.pop().unwrap();
        println!("{:?}", next);
    }
}
