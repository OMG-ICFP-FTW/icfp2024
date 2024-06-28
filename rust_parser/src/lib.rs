use pyo3::prelude::*;

// use pyo3::prelude::{
//     pyfunction, pymodule, wrap_pyfunction, Bound, PyModule, PyModuleMethods, PyResult,
// };

#[pyfunction]
fn hello_python() -> PyResult<String> {
    Ok("Hello python!".to_string())
}

#[pymodule]
fn rust_parser(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello_python, m)?)?;
    Ok(())
}

fn parse(input: &str) -> anyhow::Result<()> {
    Ok(())
}
