{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/release-23.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }: flake-utils.lib.eachDefaultSystem
    (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

  my-python-packages = python-packages: with python-packages; [
    virtualenv
    tox
  ];
  python = pkgs.python311.withPackages my-python-packages;
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [ python pkgs.geckodriver pkgs.chromedriver];
        };
      }
    );
}
