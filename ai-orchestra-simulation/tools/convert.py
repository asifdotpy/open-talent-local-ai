import os
import sys


def convert_all():
    """
    Converts markdown agent prompts to TOML command files.
    """
    # Create the target directory
    commands_dir = "./.gemini/commands/"
    os.makedirs(commands_dir, exist_ok=True)

    # Walk through the agents-temp directory
    for root, _dirs, files in os.walk("agents-temp"):
        for file in files:
            if file.endswith(".md"):
                md_file_path = os.path.join(root, file)

                # Skip README.md in the root of agents-temp
                if os.path.dirname(md_file_path) == "agents-temp" and file == "README.md":
                    print(f"Skipping root README.md: {md_file_path}")
                    continue

                try:
                    with open(md_file_path, encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    print(f"Error reading {md_file_path}: {e}", file=sys.stderr)
                    continue

                # Extract description and prompt
                try:
                    parts = content.split("---", 2)
                    if len(parts) < 3:
                        print(f"Skipping {md_file_path}: no frontmatter found.", file=sys.stderr)
                        continue

                    frontmatter = parts[1]
                    prompt_content = parts[2].strip()

                    description = ""
                    for line in frontmatter.splitlines():
                        if line.startswith("description:"):
                            description = line.split("description:", 1)[1].strip()
                            break

                    if not description:
                        print(
                            f"Skipping {md_file_path}: description not found in frontmatter.",
                            file=sys.stderr,
                        )
                        continue

                    # Construct new filename
                    category = os.path.basename(root)
                    agent_name = os.path.splitext(file)[0]
                    toml_file_name = f"agents:{category}:{agent_name}.toml"
                    toml_file_path = os.path.join(commands_dir, toml_file_name)

                    # Write TOML file
                    with open(toml_file_path, "w", encoding="utf-8") as f:
                        f.write(f'description = "{description}"\n')
                        f.write('prompt = """\n')
                        f.write(prompt_content)
                        f.write('\n"""\n')

                    print(f"Converted {md_file_path} to {toml_file_path}")

                except Exception as e:
                    print(f"Error processing {md_file_path}: {e}", file=sys.stderr)


if __name__ == "__main__":
    convert_all()
