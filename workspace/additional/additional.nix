{ pkgs }:

let
  decomp2dbg-gdb = pkgs.callPackage ./dbg-plugins/decomp2dbg.nix {};
  decomp2dbg-ghidra = pkgs.callPackage ./ghidra-extensions/decomp2dbg.nix {};

  pythonEnv = pkgs.python3.withPackages (ps: with ps; [
    angr
    asteval
    flask
    ipython
    jupyter
    psutil
    pwntools
    pycryptodome
    r2pipe
    requests
    ropper
    scapy
    selenium
  ]);

  ida-free = pkgs.ida-free.overrideAttrs (oldAttrs: {
    # This patch fixes IDA free to make sure libssl is correctly loaded in order to use the decompiler; this should be removed once the issue is fixed upstream.
    # https://github.com/NixOS/nixpkgs/blob/nixos-24.05/pkgs/by-name/id/ida-free/package.nix#L116
    preInstall = ''
    eval _"$(declare -f wrapProgram)"
    wrapProgram() {
      local program="$1"
      shift
      _wrapProgram \
        "$program" \
        --prefix LD_LIBRARY_PATH : ${pkgs.lib.getLib pkgs.openssl}/lib \
        "$@"
    }
    '';
  });

  ghidra-extended = pkgs.ghidra.withExtensions (_: [
    decomp2dbg-ghidra
  ]);

in
{
  packages = with pkgs; [
    (lib.hiPrio pythonEnv)

    gcc
    gnumake

    qemu

    strace
    gdb
    pwndbg
    gef
    decomp2dbg-gdb
    openssh
    netcat-openbsd

    vim
    emacs

    ghidra-extended
    ida-free
    radare2
    # TODO: angr-management
    # TODO: binary-ninja

    wireshark
    nmap
    tcpdump
    firefox
    geckodriver

    aflplusplus
    rappel
    ropgadget

    sage

    # TODO: apt-tools
  ];
}