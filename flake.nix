{
  description = "Parametric CAD projects for 3D printing and laser cutting";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    solidcraft = {
      url = "github:tangency-labs/solidcraft";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, solidcraft }:
    # Restricted to the systems for which solidcraft provides packages.
    flake-utils.lib.eachSystem [ "x86_64-linux" "aarch64-linux" "aarch64-darwin" ] (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShells.default = pkgs.mkShellNoCC {
          packages = [
            # Parametric CAD application (GUI: solidcraft, CLI: solidcraft-cli)
            solidcraft.packages.${system}.solidcraft
            pkgs.glow # look at md
            # Plot and geometry scripts in <project>/tools/
            (pkgs.python3.withPackages (ps: [ ps.matplotlib ]))
          ];
        };

        formatter = pkgs.nixpkgs-fmt;
      });
}
