# GitHub PR Graph Generator

A simple Python script to visualize the branch relationships between
open pull requests in a GitHub repository.

## Installation

### Prerequisites

You'll need Python and the `requests` library:

```bash
pip install requests
```

### Installing Graphviz (Optional)

If you want to generate PNG or SVG images locally, install Graphviz:

**macOS:**
```bash
brew install graphviz
```

**Debian/Ubuntu:**
```bash
sudo apt-get install graphviz
```

**Don't want to install Graphviz?** No problem! You can paste the
contents of the generated `.dot` file into
[GraphvizOnline](https://dreampuf.github.io/GraphvizOnline/) to
visualize it in your browser.

### Getting the script

1. Download the `generate_pr_graph.py` script from this repository.

2. Make it executable:
   ```bash
   chmod +x generate_pr_graph.py
   ```

3. (Optional) Move it to a location in your `PATH` for easy access:
   ```bash
   mv generate_pr_graph.py /usr/local/bin/
   ```

### GitHub Authentication (Optional)

For public repositories, no authentication is required. For private
repositories, you'll need a GitHub personal access token:

1. Go to the [GitHub section for personal access tokens](https://github.com/settings/tokens)
2. Generate a new token (classic) with `repo` scope
3. Set it as an environment variable:
   ```bash
   export GITHUB_TOKEN=ghp_your_token_here
   ```

## Usage

### Basic usage

For public repositories:
```bash
./generate_pr_graph.py owner/repo
```

For example:
```bash
./generate_pr_graph.py microsoft/vscode
./generate_pr_graph.py kubernetes/kubernetes
```

### Private repositories

Set your GitHub token first:
```bash
export GITHUB_TOKEN=ghp_your_token_here
./generate_pr_graph.py mycompany/private-repo
```

### Setting a default repository

If you work with the same repository frequently, set a default:
```bash
export GITHUB_REPO=mycompany/private-repo
./generate_pr_graph.py
```

### Output

The script generates date-stamped files in organized folders:
```
dot/pr_graph_2025-10-30.dot    # Graphviz source file
png/pr_graph_2025-10-30.png    # Generated image (after running dot command)
```

To generate an image from the `.dot` file:
```bash
dot -Tpng dot/pr_graph_2025-10-30.dot -o png/pr_graph_2025-10-30.png
dot -Tsvg dot/pr_graph_2025-10-30.dot -o svg/pr_graph_2025-10-30.svg
```

The script will print these commands for you after generating the `.dot` file.

## Configuration

You can customize the script by editing these constants at the top of `generate_pr_graph.py`:

- `MAX_TITLE_LENGTH`: Maximum length for PR titles in graph labels
  (default: 50)
- `PRIMARY_BRANCH_NAMES`: Branch names to highlight in the graph
  (default: `["main", "master", "develop"]`)

## Contributing

If you find a bug or have a feature request, please [open an
issue](../../issues). Pull requests are welcome!

## Copyright and license

Copyright (c) 2025 [Harish Narayanan](https://harishnarayanan.org).

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
