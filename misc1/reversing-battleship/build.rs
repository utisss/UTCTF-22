fn main() -> std::io::Result<()> {
    prost_build::compile_protos(&["static/protos/battleship.proto"], &["static/protos/"])?;
    println!("cargo:rerun-if-changed=static/protos/battleship.proto");
    println!("cargo:rerun-if-changed=build.rs");

    Ok(())
}
