# To learn more about how to use Nix to configure your environment
# see: https://firebase.google.com/docs/studio/customize-workspace
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.python311
    pkgs.python311Packages.pip
  ];

  # Sets environment variables in the workspace
  env = {};
  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      "ms-python.python"
    ];

    # Enable previews
    previews = {
      enable = true;
      previews = {
        web = {
          command = ["./devserver.sh"];
          manager = "web";
        };
      };
    };

    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        # Create a virtual environment
        create-venv = "python -m venv .venv";
        # Install dependencies
        install-deps = "source .venv/bin/activate && pip install -r requirements.txt";
      };
      # Runs when the workspace is (re)started
      onStart = {
        # Reminder to activate the venv
        activate-venv-msg = "echo 'Welcome! Remember to activate your virtual environment with: source .venv/bin/activate'";
      };
    };
  };
}
