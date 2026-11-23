import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GENERATED = (ROOT / ".venv", ROOT / "excecises" / "downloads")


def confirm(question: str) -> bool:
    """Ask for an explicit yes before removing resources."""
    return input(f"{question} [y/N] ").strip().lower() in ("y", "yes")


def clean_project() -> None:
    """Remove the project's environment and downloads, preserving results."""
    targets = [path for path in GENERATED if path.exists() or path.is_symlink()]
    if not targets:
        print("There are no project dependencies or downloads to clean up.")
        return
    if Path(sys.prefix).resolve() == GENERATED[0].resolve():
        print(
            "Run cleanup with a system Python to remove the project virtual environment."
        )
        return

    print("Project cleanup removes these paths, including nanoGPT checkpoints:")
    for path in targets:
        print(f"  {path}")
    if not confirm("Remove project dependencies and downloads?"):
        print("Project cleanup skipped.")
        return
    for path in targets:
        # Do not follow a project symlink into a directory outside this project.
        if path.is_symlink():
            path.unlink()
        else:
            shutil.rmtree(path)
        print(f"Removed {path}")


def uninstall_ollama_linux(binary: Path) -> None:
    """Remove a standard Ollama installation; leave model data and users intact."""
    # Only remove locations used by the standard installer; custom installations
    # and system packages need to be managed by their own installers.
    libraries = {
        Path("/usr/local/bin/ollama"): Path("/usr/local/lib/ollama"),
        Path("/usr/bin/ollama"): Path("/usr/lib/ollama"),
        Path("/bin/ollama"): Path("/lib/ollama"),
    }
    if binary not in libraries or binary.is_symlink():
        sys.exit(
            f"Unsupported Ollama installation at {binary}. Uninstall it using its package manager or installer."
        )
    if shutil.which("dpkg-query"):
        package = subprocess.run(
            ["dpkg-query", "-S", str(binary)],
            capture_output=True,
            text=True,
            check=False,
        )
        if package.returncode == 0:
            sys.exit(
                f"{binary} is managed by a system package. Remove it with its package manager."
            )
    if not shutil.which("sudo") and os.geteuid() != 0:
        sys.exit("sudo is required to remove this Ollama installation.")
    prefix = [] if os.geteuid() == 0 else ["sudo"]
    service = Path("/etc/systemd/system/ollama.service")
    if service.is_file() and shutil.which("systemctl"):
        subprocess.run(
            [*prefix, "systemctl", "disable", "--now", "ollama.service"], check=True
        )
        subprocess.run([*prefix, "rm", "-f", str(service)], check=True)
        subprocess.run([*prefix, "systemctl", "daemon-reload"], check=True)
    subprocess.run([*prefix, "rm", "-f", str(binary)], check=True)
    library = libraries[binary]
    if library.is_dir() and not library.is_symlink():
        subprocess.run([*prefix, "rm", "-r", str(library)], check=True)
    print(
        "Ollama's standard installation was removed. A manually started server may need to be stopped separately."
    )


def uninstall_ollama() -> None:
    """Optionally uninstall Ollama without deleting its shared model data."""
    command = shutil.which("ollama")
    if sys.platform == "win32" and not command:
        default_binary = (
            Path(os.environ.get("LOCALAPPDATA", ""))
            / "Programs"
            / "Ollama"
            / "ollama.exe"
        )
        if default_binary.is_file():
            command = str(default_binary)
    if not command:
        print("Ollama was not found on PATH; no uninstall was attempted.")
        return

    print(f"Ollama installation found: {command}")
    print("Uninstalling affects other projects. Shared Ollama model data will be kept.")
    if not confirm("Uninstall Ollama from this computer?"):
        print("Ollama uninstall skipped.")
        return

    if sys.platform.startswith("linux"):
        uninstall_ollama_linux(Path(command))
    elif sys.platform == "win32":
        if not shutil.which("winget"):
            sys.exit(
                "Windows Package Manager (winget) is unavailable. Uninstall Ollama through Windows Settings."
            )
        result = subprocess.run(
            [
                "winget",
                "uninstall",
                "--id",
                "Ollama.Ollama",
                "--exact",
                "--interactive",
            ],
            check=False,
        )
        if result.returncode != 0:
            sys.exit(
                "Ollama uninstall failed. Use Windows Settings > Installed apps to remove it."
            )
        print(
            "The Ollama uninstaller finished. Check Windows Settings if it remains installed."
        )
    else:
        sys.exit("Automatic Ollama uninstall is supported on Linux and Windows only.")


def main() -> None:
    """Offer project cleanup and Ollama uninstall as separate choices."""
    clean_project()
    uninstall_ollama()
    print("Exercise results and shared model caches were not removed.")


if __name__ == "__main__":
    main()
