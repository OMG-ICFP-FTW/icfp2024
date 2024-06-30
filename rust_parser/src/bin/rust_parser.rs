use std::fs;
use std::path;

use std::cell::RefCell;
use std::collections::BTreeMap;
use std::collections::HashMap;
use std::rc::Rc;

use clap::Parser;

use rust_parser::ast::*;

#[derive(clap::Parser, Debug)]
#[command(author, version, about, long_about = None, arg_required_else_help = true)]
struct Args {
    #[command(subcommand)]
    command: Command,

    #[arg(long, default_value_t = false)]
    ast: bool,

    #[arg(long, default_value_t = false)]
    no_rewrite_id: bool,

    #[arg(long)]
    input: path::PathBuf,
}

#[derive(clap::Subcommand, Debug)]
enum Command {
    Parse,
    Debug,
    Step { iterations: i64 },
}

fn main() {
    let args = Args::parse();

    let input_icfp = fs::read_to_string(&args.input).unwrap();
    let ast: Expr = if !args.ast {
        let mut parse_result = <rust_parser::parser::ICFPParser as pest::Parser<_>>::parse(
            rust_parser::parser::Rule::expr,
            &input_icfp,
        )
        .unwrap();

        let parse_tree = parse_result.next().unwrap();
        let rewrites = BTreeMap::new();
        let unique_scope = Rc::new(RefCell::new(-1));
        rust_parser::parser::parse(parse_tree, &rewrites, unique_scope, !args.no_rewrite_id)
            .unwrap()
    } else {
        serde_json::from_str(&input_icfp).unwrap()
    };

    match args.command {
        Command::Parse => {
            println!("AST: {}", &ast);
        }
        Command::Debug => {
            println!("AST: {:#?}", &ast);
        }
        Command::Step { iterations } => {
            let mut executor = rust_parser::executor::Executor {
                variables: HashMap::new(),
            };
            let mut next = executor.step(Box::new(ast));
            let mut i = 1;
            while i < iterations {
                next = executor.step(next);
                i += 1;
            }
            println!("AST: {}", &next);
        }
    }
}
