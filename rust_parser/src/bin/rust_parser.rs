use std::fs;
use std::path;

use clap::Parser;

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
    let parse_result = <ICFPParser as pest::Parser<_>>::parse(Rule::expr, &input_icfp).unwrap();

    println!("{}", serde_json::to_string_pretty(&parse_result).unwrap());
}
