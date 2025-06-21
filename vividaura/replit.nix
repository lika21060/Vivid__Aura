{ pkgs }: {
  deps = [
    pkgs.python311Full  # Full Python 3.11 environment
    pkgs.python311Packages.pip
  ];
}
