{
  description = "Nix flake for menta";
  inputs.nixpkgs.url = "nixpkgs/nixos-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        overlay = final: prev: {
          menta = with final; python3Packages.buildPythonPackage rec {
            pname = "menta";
            version = "0.0.1a2";
            src = ./.;
            format = "pyproject";

            nativeBuildInputs = with pkgs.python3Packages; [
              poetry-core
            ];

            checkInputs = with pkgs.python3Packages; [
              freezegun
              pytest-benchmark
              pytestCheckHook 
            ];

            propagatedBuildInputs = with pkgs.python3Packages; [
              pynacl
            ];

            pythonImportsCheck = [ "menta" ];

            doCheck = true;
          };
        };

        pkgs = import nixpkgs {
          overlays = [
            overlay
          ];
          inherit system;
        };
      in rec {
        packages = flake-utils.lib.flattenTree {
          menta = pkgs.menta;
        };
        defaultPackage = packages.menta;
        devShell = with pkgs; let
          pythonEnv = pkgs.python3.withPackages (ps:
            [
              ps.black
              ps.coverage
              ps.freezegun
              ps.mypy
              ps.poetry-core
              ps.pylint
              ps.pytest
              ps.pytest-benchmark
              ps.pynacl
            ]
          );
        in mkShell {
          buildInputs = [
            pythonEnv
          ];
        };
      }
  );
}
