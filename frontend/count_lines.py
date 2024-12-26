import os


def count_lines(directory: str) -> dict:
    """Conta linhas de código Python no projeto."""

    ignore_dirs = [".git", ".venv", ".venv-SFM", "__pycache__", "node_modules", ".pytest_cache"]

    stats = {"total_lines": 0, "total_files": 0, "files": {}}

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = len(f.readlines())
                    if lines > 0:  # Conta apenas arquivos com pelo menos uma linha
                        stats["total_lines"] += lines
                        stats["files"][file_path] = lines
                        stats["total_files"] += 1

    return stats


if __name__ == "__main__":
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    stats = count_lines(project_dir)

    print(f"\nTotal de arquivos Python: {stats['total_files']}")
    print(f"Total de linhas: {stats['total_lines']}")
    print(f"Média de linhas por arquivo: {stats['total_lines']/stats['total_files']:.1f}")
    print("\nDetalhes por arquivo:")
    for file, lines in sorted(stats["files"].items(), key=lambda x: x[1], reverse=True):
        print(f"{file}: {lines} linhas")
