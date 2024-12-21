import os
import sys
import yaml
from github import Github
from pathlib import Path
import re
from .config import ConfigManager


class CodeReviewer:
    def __init__(self, github_token: str, config_path: str = None):
        """Initialize code reviewer.

        Args:
            github_token: GitHub API token
            config_path: Optional path to custom configuration file
        """
        self.github = Github(github_token)
        self.config = ConfigManager(config_path)
        # For backward compatibility with tests
        self.rules = self.config.config['rules']

    def _load_rules(self) -> dict:
        """Load review rules from config file."""
        # This method is kept for backward compatibility
        return self.config.config['rules']

    def review_pull_request(self, repo_name: str, pr_number: int):
        """Main method to review a pull request."""
        repo = self.github.get_repo(repo_name)
        pr = repo.get_pull(pr_number)

        review_comments = []

        for file in pr.get_files():
            if file.filename.endswith('.py'):  # Start with Python files
                review_comments.extend(self._review_file(file))

        if review_comments:
            self._post_review(pr, review_comments)

    def _review_file(self, file) -> list:
        """Review a single file and return list of comments."""
        comments = []

        # Get file content
        content = file.patch.split('\n') if file.patch else []

        # Apply rules
        comments.extend(self._check_line_length(content, file))
        comments.extend(self._check_file_size(content, file))
        comments.extend(self._check_naming_conventions(content, file))
        comments.extend(self._check_docstrings(content, file))
        comments.extend(self._check_function_length(content, file))
        comments.extend(self._check_complexity(content, file))
        comments.extend(self._check_imports(content, file))
        comments.extend(self._check_type_hints(content, file))
        comments.extend(self._check_constants(content, file))
        comments.extend(self._check_duplicates(content, file))
        comments.extend(self._check_magic_numbers(content, file))
        comments.extend(self._check_exception_handling(content, file))
        comments.extend(self._check_dead_code(content, file))
        comments.extend(self._check_string_duplicates(content, file))
        comments.extend(self._check_function_args(content, file))
        comments.extend(self._check_return_consistency(content, file))
        comments.extend(self._check_loop_complexity(content, file))
        comments.extend(self._check_comment_quality(content, file))
        comments.extend(self._check_security_patterns(content, file))
        comments.extend(self._check_test_coverage(content, file))
        comments.extend(self._check_dependency_cycles(content, file))
        comments.extend(self._check_performance_patterns(content, file))
        comments.extend(self._check_error_messages(content, file))
        comments.extend(self._check_api_documentation(content, file))
        comments.extend(self._check_spacing(content, file))
        comments.extend(self._check_unused_code(content, file))

        return comments

    def _check_line_length(self, content: list, file) -> list:
        """Check if any line exceeds maximum length."""
        comments = []
        max_length = self.config.get_rule('max_line_length', 100)

        for line_num, line in enumerate(content, 1):
            if len(line) > max_length:
                comments.append({
                    'path': file.filename,
                    'line': line_num,
                    'body': f'Line exceeds {max_length} characters'
                })
        return comments

    def _check_file_size(self, content: list, file) -> list:
        """Check if file exceeds maximum size."""
        comments = []
        max_lines = self.config.get_rule('max_file_lines', 300)

        if len(content) > max_lines:
            comments.append({
                'path': file.filename,
                'line': 1,
                'body': f'File exceeds {max_lines} lines'
            })
        return comments

    def _check_naming_conventions(self, content: list, file) -> list:
        """Check if names follow the configured conventions."""
        comments = []
        # Special names to ignore
        ignore_names = {'__name__', '__main__', '__init__', '__file__'}

        patterns = {
            'class': r'class\s+(\w+)',
            'function': r'def\s+(\w+)',
            'variable': r'(?:^|[\s=])(\w+)\s*='
        }

        conventions = self.config.get_rule('naming_conventions', {})

        for line_num, line in enumerate(content, 1):
            stripped_line = line.strip()
            indent = len(line) - len(line.lstrip())

            # Check for class names (PascalCase)
            if 'class' in line and conventions.get('classes') == 'PascalCase':
                matches = re.finditer(patterns['class'], line)
                for match in matches:
                    class_name = match.group(1)
                    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', class_name):
                        comments.append({
                            'path': file.filename,
                            'line': line_num,
                            'body': f'Class name "{class_name}" should be in PascalCase'
                        })

            # Check function names (snake_case)
            if 'def' in line and conventions.get('functions') == 'snake_case':
                matches = re.finditer(patterns['function'], line)
                for match in matches:
                    func_name = match.group(1)
                    if not re.match(r'^[a-z][a-z0-9_]*$', func_name):
                        comments.append({
                            'path': file.filename,
                            'line': line_num,
                            'body': f'Function name "{func_name}" should be in snake_case'
                        })

            # Check variable names (snake_case)
            if '=' in line and conventions.get('variables') == 'snake_case':
                matches = re.finditer(patterns['variable'], line)
                for match in matches:
                    var_name = match.group(1)
                    if var_name not in ignore_names and not re.match(r'^[a-z][a-z0-9_]*$', var_name):
                        comments.append({
                            'path': file.filename,
                            'line': line_num,
                            'body': f'Variable name "{var_name}" should be in snake_case'
                        })

        return comments

    def _check_docstrings(self, content: list, file) -> list:
        """Check if classes and functions have docstrings."""
        comments = []
        if not self.config.get_rule('required_docstrings'):
            return comments

        in_definition = False
        needs_docstring = False
        start_line = 0
        current_indent = 0
        min_docstring_words = 5  # Minimum words for a complete docstring

        for line_num, line in enumerate(content, 1):
            stripped_line = line.strip()
            indent = len(line) - len(line.lstrip())

            # Check for class or function definitions
            if stripped_line.startswith(('class ', 'def ')):
                if in_definition and needs_docstring:
                    comments.append({
                        'path': file.filename,
                        'line': start_line,
                        'body': 'Missing docstring for class/function'
                    })

                in_definition = True
                needs_docstring = True
                start_line = line_num
                current_indent = indent
                continue

            # Check for docstring
            if needs_docstring:
                if stripped_line.startswith(('"""', "'''")):
                    needs_docstring = False
                    # Check docstring content
                    docstring_content = stripped_line[3:-3] if stripped_line.endswith(
                        ('"""', "'''")) else ""
                    if not docstring_content:
                        # Multi-line docstring - collect until end
                        for next_line in content[line_num:]:
                            next_stripped = next_line.strip()
                            if next_stripped.endswith(('"""', "'''")):
                                docstring_content += " " + next_stripped[:-3]
                                break
                            docstring_content += " " + next_stripped

                    # Check docstring quality
                    words = [w for w in docstring_content.split()
                             if w not in ('"""', "'''")]
                    if len(words) < min_docstring_words:
                        comments.append({
                            'path': file.filename,
                            'line': line_num,
                            'body': 'Docstring is too brief. Add more detailed explanation.'
                        })
                elif stripped_line and not stripped_line.startswith('#'):
                    if indent <= current_indent:
                        # Function/class ended without docstring
                        comments.append({
                            'path': file.filename,
                            'line': start_line,
                            'body': 'Missing docstring for class/function'
                        })
                        needs_docstring = False
                        in_definition = False

        # Check last definition
        if needs_docstring:
            comments.append({
                'path': file.filename,
                'line': start_line,
                'body': 'Missing docstring for class/function'
            })

        return comments

    def _check_function_length(self, content: list, file) -> list:
        """Check if any function exceeds the maximum allowed length."""
        comments = []
        max_length = self.config.get_rule('max_function_lines', 50)

        current_function = None
        function_start = 0
        function_lines = 0
        indent_level = 0

        for line_num, line in enumerate(content, 1):
            stripped_line = line.strip()

            # Skip empty lines and comments
            if not stripped_line or stripped_line.startswith('#'):
                continue

            # Calculate indent level
            current_indent = len(line) - len(line.lstrip())

            # Check for function definition
            if stripped_line.startswith('def '):
                current_function = stripped_line[4:].split('(')[0].strip()
                function_start = line_num
                function_lines = 0
                indent_level = current_indent

            # Count lines within the function
            if current_function:
                if current_indent > indent_level:
                    function_lines += 1
                elif line.strip() and current_indent <= indent_level:
                    # Function ended
                    if function_lines > max_length:
                        comments.append({
                            'path': file.filename,
                            'line': function_start,
                            'body': f'Function "{current_function}" is too long ({function_lines} lines). Maximum allowed is {max_length} lines.'
                        })
                    current_function = None

        # Check last function in file
        if current_function and function_lines > max_length:
            comments.append({
                'path': file.filename,
                'line': function_start,
                'body': f'Function "{current_function}" is too long ({function_lines} lines). Maximum allowed is {max_length} lines.'
            })

        return comments

    def _check_complexity(self, content: list, file) -> list:
        """Check cognitive complexity and nesting depth of functions."""
        comments = []
        current_function = None
        function_start = 0
        current_depth = 0
        cognitive_complexity = 0
        max_depth = self.config.get_rule(
            'complexity', {}).get('max_nested_blocks', 3)
        max_cognitive = self.config.get_rule('complexity', {}).get(
            'max_cognitive_complexity', 15)

        # Keywords that increase complexity
        complexity_keywords = {
            'if': 1, 'else': 1, 'elif': 1,
            'for': 1, 'while': 1,
            'try': 1, 'except': 1,
            'and': 1, 'or': 1
        }

        for line_num, line in enumerate(content, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue

            # Calculate indent level
            indent = len(line) - len(line.lstrip())
            if not stripped.startswith(('"""', "'''")):  # Skip docstring indents
                current_depth = indent // 4

            if stripped.startswith('def '):
                # Check previous function's complexity
                if current_function:
                    if cognitive_complexity > max_cognitive:
                        comments.append({
                            'path': file.filename,
                            'line': function_start,
                            'body': f'Function has cognitive complexity of {cognitive_complexity}. Maximum allowed is {max_cognitive}.'
                        })
                    if current_depth > max_depth:
                        comments.append({
                            'path': file.filename,
                            'line': function_start,
                            'body': f'Function has too deep nesting (depth: {current_depth}). Maximum allowed is {max_depth}.'
                        })

                current_function = stripped[4:].split('(')[0]
                function_start = line_num
                cognitive_complexity = 0
                current_depth = 0
            else:
                # Calculate complexity based on keywords and nesting
                for keyword in complexity_keywords:
                    if keyword in stripped.split():
                        cognitive_complexity += complexity_keywords[keyword] * (
                            current_depth + 1)

        # Check last function
        if current_function:
            if cognitive_complexity > max_cognitive:
                comments.append({
                    'path': file.filename,
                    'line': function_start,
                    'body': f'Function has cognitive complexity of {cognitive_complexity}. Maximum allowed is {max_cognitive}.'
                })
            if current_depth > max_depth:
                comments.append({
                    'path': file.filename,
                    'line': function_start,
                    'body': f'Function has too deep nesting (depth: {current_depth}). Maximum allowed is {max_depth}.'
                })

        return comments

    def _check_imports(self, content: list, file) -> list:
        """Check import order and organization."""
        comments = []
        imports = []
        current_group = None
        last_import = None
        blank_lines_between_groups = 0

        for line_num, line in enumerate(content, 1):
            stripped = line.strip()

            # Handle blank lines
            if not stripped:
                if last_import:
                    blank_lines_between_groups += 1
                continue

            # Skip comments
            if stripped.startswith('#'):
                continue

            if stripped.startswith(('import ', 'from ')):
                group = self._determine_import_group(stripped)

                # Check group separation
                if current_group and group != current_group:
                    if blank_lines_between_groups == 0:
                        comments.append({
                            'path': file.filename,
                            'line': line_num,
                            'body': f'Import from "{group}" group should be separated from "{current_group}" group by a blank line'
                        })

                # Check order within current group
                if last_import and group == current_group:
                    # Normalize imports for comparison
                    current = self._normalize_import(stripped)
                    previous = self._normalize_import(last_import)
                    if current < previous:  # Only check if current is less than previous
                        comments.append({
                            'path': file.filename,
                            'line': line_num,
                            'body': 'Imports are not properly sorted within their group'
                        })

                current_group = group
                last_import = stripped
                imports.append((line_num, stripped, group))
                blank_lines_between_groups = 0

        return comments

    def _normalize_import(self, import_line: str) -> str:
        """Normalize import line for sorting."""
        # Remove comments and whitespace
        import_line = import_line.split('#')[0].strip()

        # Handle 'from' imports
        if import_line.startswith('from '):
            parts = import_line.split('import')
            module = parts[0].replace('from ', '').strip()
            imports = parts[1].strip()
            # Sort 'from' imports after regular imports
            # 'z' prefix ensures 'from' comes after 'import'
            return f"z{module}.{imports}"

        # Handle regular imports - just get the module name
        return import_line.split('import ')[1].strip()

    def _check_type_hints(self, content: list, file) -> list:
        """Check for proper use of type hints."""
        comments = []
        if not self.config.get_rule('require_type_hints', True):
            return comments

        for line_num, line in enumerate(content, 1):
            stripped = line.strip()
            if stripped.startswith('def '):
                # Check return type hint
                if not '->' in stripped:
                    comments.append({
                        'path': file.filename,
                        'line': line_num,
                        'body': 'Function is missing return type hint'
                    })

                # Check parameter type hints
                params = stripped[stripped.find(
                    '(')+1:stripped.find(')')].strip()
                if params and not ':' in params:
                    comments.append({
                        'path': file.filename,
                        'line': line_num,
                        'body': 'Function parameters are missing type hints'
                    })

        return comments

    def _post_review(self, pr, comments: list):
        """Post review comments to the pull request."""
        if comments:
            # Format the review body
            review_body = "Code Review Results:\n\n"

            # Filter comments to only include those on changed lines
            filtered_comments = []
            for file in pr.get_files():
                # Get the changed line numbers for this file
                changed_lines = set()
                patch = file.patch if file.patch else ""
                for hunk in patch.split('\n@@')[1:]:
                    # Parse the hunk header
                    hunk_header = hunk.split('\n')[0]
                    try:
                        # Extract line numbers from hunk header
                        _, new_lines = hunk_header.split(' ')
                        start_line = int(new_lines.split(',')[0].strip('+'))
                        count = int(new_lines.split(',')[
                                    1]) if ',' in new_lines else 1
                        changed_lines.update(
                            range(start_line, start_line + count))
                    except (ValueError, IndexError):
                        continue

                # Filter comments for this file
                file_comments = [
                    comment for comment in comments
                    if comment['path'] == file.filename and comment['line'] in changed_lines
                ]
                filtered_comments.extend(file_comments)

            # Add filtered comments to review body
            if filtered_comments:
                review_body += "\n".join([
                    f"- {comment['path']} (line {comment['line']}): {comment['body']}"
                    for comment in filtered_comments
                ])

                # Create the review
                pr.create_review(
                    body=review_body,
                    event='COMMENT',
                    comments=filtered_comments
                )
            else:
                # If no comments on changed lines, just post a general message
                review_body = "No issues found in the changed code."
                pr.create_review(
                    body=review_body,
                    event='COMMENT'
                )

    def _check_constants(self, content: list, file) -> list:
        """Check if constants follow naming conventions."""
        comments = []
        constant_pattern = r'([A-Z_][A-Z0-9_]*)\s*='

        # Patterns to ignore
        ignore_patterns = [
            r'^\s*class\s+.*:',  # Class definitions
            r'^\s*def\s+.*:',    # Function definitions
            r'^\s*@.*',          # Decorators
            r'^\s*#.*',          # Comments
            r'^\s*""".*"""',     # Docstrings
            r"^\s*'''.*'''",     # Docstrings
        ]

        for line_num, line in enumerate(content, 1):
            # Skip lines matching ignore patterns
            if any(re.match(pattern, line) for pattern in ignore_patterns):
                continue

            # Find assignments
            if '=' in line and not line.strip().startswith(('def', 'class', '@')):
                stripped_line = line.strip()

                # Check if it looks like a constant (all caps)
                if re.search(r'[A-Z]{2}', stripped_line):
                    matches = re.finditer(
                        r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=', stripped_line)
                    for match in matches:
                        name = match.group(1)
                        if not re.match(r'^[A-Z][A-Z0-9_]*$', name):
                            comments.append({
                                'path': file.filename,
                                'line': line_num,
                                'body': f'Constant "{name}" should be in UPPER_CASE'
                            })

        return comments

    def _check_duplicates(self, content: list, file) -> list:
        """Check for duplicate code blocks."""
        comments = []
        min_block_size = 4  # Minimum lines to consider as a block
        similarity_threshold = 0.85  # Minimum similarity to flag as duplicate

        def normalize_line(line: str) -> str:
            """Normalize line for comparison by removing whitespace and variable names."""
            return re.sub(r'[a-zA-Z_][a-zA-Z0-9_]*', 'VAR', line.strip())

        def calculate_similarity(block1: list, block2: list) -> float:
            """Calculate similarity between two code blocks."""
            if len(block1) != len(block2):
                return 0.0

            matching_lines = sum(
                1 for l1, l2 in zip(block1, block2)
                if normalize_line(l1) == normalize_line(l2)
            )
            return matching_lines / len(block1)

        # Get meaningful lines (skip empty lines and comments)
        meaningful_lines = [
            (i, line.strip()) for i, line in enumerate(content, 1)
            if line.strip() and not line.strip().startswith('#')
        ]

        # Check for duplicate blocks
        for size in range(min_block_size, len(meaningful_lines) // 2 + 1):
            for i in range(len(meaningful_lines) - size * 2 + 1):
                block1 = [line for _, line in meaningful_lines[i:i + size]]

                # Compare with subsequent blocks
                for j in range(i + size, len(meaningful_lines) - size + 1):
                    block2 = [line for _, line in meaningful_lines[j:j + size]]

                    similarity = calculate_similarity(block1, block2)
                    if similarity >= similarity_threshold:
                        comments.append({
                            'path': file.filename,
                            'line': meaningful_lines[i][0],
                            'body': (
                                f'Possible code duplication detected. '
                                f'Block of {size} lines is {similarity:.0%} similar to '
                                f'block at line {meaningful_lines[j][0]}. '
                                'Consider refactoring to remove duplication.'
                            )
                        })
                        # Skip to the end of current block to avoid multiple warnings
                        break

        return comments

    def _check_magic_numbers(self, content: list, file) -> list:
        """Check for magic numbers in code."""
        comments = []

        # Numbers that are usually acceptable
        allowed_numbers = {0, 1, -1, 100, 1000}
        # Patterns where numbers are acceptable
        allowed_patterns = [
            r'^\s*#',  # Comments
            r'^\s*"""',  # Docstrings
            r"^\s*'''",  # Docstrings
            r'^\s*@\w+\(',  # Decorators
            r'^\s*from\s+\w+\s+import',  # Import statements
            r'^\s*if\s+__name__\s*==\s*[\'"]__main__[\'"]',  # Main block
            r'range\(\d+\)',  # Range functions
            r'\.{3}\d+',  # Slices
        ]

        number_pattern = r'(?<![.\w])-?\d+(?!\.\d*[eE]|[.\w])'

        for line_num, line in enumerate(content, 1):
            # Skip allowed patterns
            if any(re.match(pattern, line) for pattern in allowed_patterns):
                continue

            # Find numbers in line
            matches = re.finditer(number_pattern, line)
            for match in matches:
                number = int(match.group())
                if number not in allowed_numbers:
                    # Check if number is already defined as a constant
                    if not re.search(rf'[A-Z][A-Z0-9_]*\s*=\s*{number}', '\n'.join(content)):
                        comments.append({
                            'path': file.filename,
                            'line': line_num,
                            'body': f'Magic number "{number}" found. Consider defining it as a named constant.'
                        })

        return comments

    def _check_exception_handling(self, content: list, file) -> list:
        """Check for proper exception handling practices."""
        comments = []
        in_try = False
        try_line = 0
        has_except = False
        has_specific_except = False
        bare_except_line = 0

        exception_patterns = {
            'bare_except': r'^\s*except\s*:',
            'too_broad': r'^\s*except\s+(Exception|BaseException)\s*:',
            'pass_in_except': r'^\s*except\s+.*:\s*\n\s*pass\s*$',
            'print_only': r'^\s*except\s+.*:\s*\n\s*print\s*\(',
        }

        for line_num, line in enumerate(content, 1):
            stripped_line = line.strip()

            # Track try blocks
            if stripped_line.startswith('try:'):
                in_try = True
                try_line = line_num
                has_except = False
                has_specific_except = False

            # Check except clauses
            elif in_try and stripped_line.startswith('except'):
                has_except = True

                # Check for bare except
                if re.match(exception_patterns['bare_except'], line):
                    bare_except_line = line_num
                    comments.append({
                        'path': file.filename,
                        'line': line_num,
                        'body': 'Bare except clause used. Specify exception types explicitly.'
                    })

                # Check for too broad exception handling
                elif re.match(exception_patterns['too_broad'], line):
                    comments.append({
                        'path': file.filename,
                        'line': line_num,
                        'body': 'Too broad exception clause. Catch specific exceptions instead.'
                    })
                else:
                    has_specific_except = True

                # Look ahead for pass or print-only handling
                next_line = content[line_num].strip(
                ) if line_num < len(content) else ''
                if re.match(exception_patterns['pass_in_except'], line + '\n' + next_line):
                    comments.append({
                        'path': file.filename,
                        'line': line_num,
                        'body': 'Empty except clause (pass). Implement proper error handling.'
                    })
                elif re.match(exception_patterns['print_only'], line + '\n' + next_line):
                    comments.append({
                        'path': file.filename,
                        'line': line_num,
                        'body': 'Print-only except clause. Consider proper error handling or logging.'
                    })

            # Check for finally or end of try block
            elif in_try and (stripped_line.startswith('finally:') or
                             (not stripped_line.startswith((' ', 'elif', 'else:')) and stripped_line)):
                if not has_except:
                    comments.append({
                        'path': file.filename,
                        'line': try_line,
                        'body': 'Try block without except clause.'
                    })
                in_try = False

        return comments

    def _check_dead_code(self, content: list, file) -> list:
        """Check for unused imports, variables, and functions."""
        comments = []
        imports = {}
        variables = {}
        functions = {}
        used_functions = set()

        # First pass: collect definitions and usages
        for line_num, line in enumerate(content, 1):
            stripped_line = line.strip()

            # Skip comments
            if stripped_line.startswith('#'):
                continue

            # Collect imports
            if stripped_line.startswith('import ') or stripped_line.startswith('from '):
                if 'import' in stripped_line:
                    imported = stripped_line.split(
                        'import')[1].strip().split(' as ')
                    name = imported[-1].strip()
                    imports[name] = line_num

            # Collect function definitions
            elif stripped_line.startswith('def '):
                func_name = stripped_line[4:].split('(')[0].strip()
                functions[func_name] = line_num

            # Collect function calls
            else:
                for func_name in functions:
                    if f"{func_name}(" in stripped_line:
                        used_functions.add(func_name)

            # Collect variable assignments
            if '=' in stripped_line and not stripped_line.startswith(('if', 'while', 'for')):
                var_name = stripped_line.split('=')[0].strip()
                if var_name.isidentifier():
                    variables[var_name] = line_num

        # Check functions
        for name, line_num in functions.items():
            if name.startswith('_'):  # Skip private functions
                continue
            if name not in used_functions:
                comments.append({
                    'path': file.filename,
                    'line': line_num,
                    'body': f'Unused function: "{name}"'
                })

        # Check imports
        for name, line_num in imports.items():
            # Skip special cases
            if name in ('*', '') or name.startswith('_'):
                continue

            # Count occurrences after import
            content_after_import = '\n'.join(content[line_num:])
            # 1 for the import itself
            if content_after_import.count(name) <= 1:
                comments.append({
                    'path': file.filename,
                    'line': line_num,
                    'body': f'Unused import: "{name}"'
                })

        # Check variables
        for name, line_num in variables.items():
            if name.startswith('_'):  # Skip private variables
                continue

            # Count occurrences after definition
            content_after_def = '\n'.join(content[line_num:])
            # 1 for the definition itself
            if content_after_def.count(name) <= 1:
                comments.append({
                    'path': file.filename,
                    'line': line_num,
                    'body': f'Unused variable: "{name}"'
                })

        return comments

    def _check_string_duplicates(self, content: list, file) -> list:
        """Check for duplicate string literals."""
        comments = []
        string_literals = {}
        min_length = 10  # Minimum string length to consider
        min_occurrences = 3  # Minimum occurrences to flag

        # String patterns
        string_patterns = [
            r'"([^"\\]*(\\.[^"\\]*)*)"',  # Double-quoted strings
            r"'([^'\\]*(\\.[^'\\]*)*)'",  # Single-quoted strings
        ]

        # Skip patterns (strings that are typically duplicated)
        skip_patterns = [
            r'^[A-Z_]+$',  # Constants
            r'^https?://',  # URLs
            r'^[\W\d]+$',  # Strings with only special chars and numbers
            r'^[a-z_]+$',  # Common variable names
        ]

        for line_num, line in enumerate(content, 1):
            for pattern in string_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    string = match.group(1)

                    # Skip if string is too short or matches skip patterns
                    if len(string) < min_length or any(re.match(p, string) for p in skip_patterns):
                        continue

                    # Store string occurrence
                    if string not in string_literals:
                        string_literals[string] = []
                    string_literals[string].append(line_num)

        # Check for duplicates
        for string, lines in string_literals.items():
            if len(lines) >= min_occurrences:
                comments.append({
                    'path': file.filename,
                    'line': lines[0],
                    'body': (
                        f'String literal "{string[:30]}..." appears {len(lines)} times. '
                        f'Consider defining it as a constant. Other occurrences at lines: {", ".join(map(str, lines[1:]))}'
                    )
                })

        return comments

    def _check_function_args(self, content: list, file) -> list:
        """Check function argument count and complexity."""
        comments = []
        max_args = self.config.get_rule(
            'functions', {}).get('max_arguments', 5)
        max_defaults = self.config.get_rule(
            'functions', {}).get('max_default_args', 3)

        # Pattern to match function definitions with arguments
        func_pattern = r'def\s+(\w+)\s*\((.*?)\)\s*(?:->.*?)?:'

        for line_num, line in enumerate(content, 1):
            if 'def ' in line and not line.strip().startswith('#'):
                match = re.search(func_pattern, line)
                if match:
                    func_name = match.group(1)
                    args_str = match.group(2).strip()

                    if not args_str:
                        continue

                    # Split arguments and handle special cases
                    args = [
                        arg.strip()
                        for arg in args_str.split(',')
                        if arg and not arg.startswith('self')
                    ]

                    # Count regular and default arguments
                    default_args = len([arg for arg in args if '=' in arg])
                    total_args = len(args)

                    if total_args > max_args:
                        comments.append({
                            'path': file.filename,
                            'line': line_num,
                            'body': (
                                f'Function "{func_name}" has too many arguments ({total_args}). '
                                f'Maximum allowed is {max_args}. Consider using a class or data structure.'
                            )
                        })

                    if default_args > max_defaults:
                        comments.append({
                            'path': file.filename,
                            'line': line_num,
                            'body': (
                                f'Function "{func_name}" has too many default arguments ({default_args}). '
                                f'Maximum allowed is {max_defaults}. Consider breaking it into smaller functions.'
                            )
                        })

                    # Check for boolean flag arguments
                    bool_flags = [
                        arg for arg in args
                        if '=' in arg and ('True' in arg or 'False' in arg)
                    ]
                    if len(bool_flags) > 2:
                        comments.append({
                            'path': file.filename,
                            'line': line_num,
                            'body': (
                                f'Function "{func_name}" has too many boolean flags ({len(bool_flags)}). '
                                'Consider using a configuration object or breaking it into smaller functions.'
                            )
                        })

        return comments

    def _check_return_consistency(self, content: list, file) -> list:
        """Check for consistent return types and patterns in functions."""
        comments = []
        current_function = None
        function_start = 0
        return_lines = []
        in_function = False
        indent_level = 0

        # Patterns for return statements
        return_pattern = r'^\s*return\s*(.*)$'
        func_pattern = r'def\s+(\w+)\s*\([^)]*\)\s*(?:->?\s*([^:]+))?\s*:'

        for line_num, line in enumerate(content, 1):
            stripped_line = line.strip()

            # Skip empty lines and comments
            if not stripped_line or stripped_line.startswith('#'):
                continue

            # Track function definitions
            if stripped_line.startswith('def '):
                if current_function and return_lines:
                    self._analyze_returns(
                        comments, file, current_function,
                        function_start, return_lines
                    )

                match = re.match(func_pattern, stripped_line)
                if match:
                    current_function = match.group(1)
                    function_start = line_num
                    return_lines = []
                    in_function = True
                    indent_level = len(line) - len(line.lstrip())
                continue

            # Track return statements
            if in_function:
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= indent_level and stripped_line:
                    in_function = False
                    if return_lines:
                        self._analyze_returns(
                            comments, file, current_function,
                            function_start, return_lines
                        )
                elif re.match(return_pattern, stripped_line):
                    return_value = re.match(
                        return_pattern, stripped_line).group(1)
                    return_lines.append((line_num, return_value.strip()))

        # Check last function
        if current_function and return_lines:
            self._analyze_returns(
                comments, file, current_function,
                function_start, return_lines
            )

        return comments

    def _analyze_returns(self, comments: list, file, function_name: str,
                         start_line: int, return_lines: list) -> None:
        """Analyze return statements for consistency."""
        if not return_lines:
            return

        # Categorize return values
        return_types = set()
        for _, value in return_lines:
            if value == '':  # bare return
                return_types.add('None')
            elif value.isdigit():
                return_types.add('int')
            elif value in ('True', 'False'):
                return_types.add('bool')
            elif value.startswith('"') or value.startswith("'"):
                return_types.add('str')
            elif value.startswith('['):
                return_types.add('list')
            elif value.startswith('{'):
                return_types.add('dict')
            elif value == 'None':
                return_types.add('None')
            else:
                return_types.add('other')

        # Check for multiple return types
        if len(return_types) > 1 and 'None' not in return_types:
            comments.append({
                'path': file.filename,
                'line': start_line,
                'body': (
                    f'Function "{function_name}" has inconsistent return types: {", ".join(return_types)}. '
                    'Consider making return types consistent.'
                )
            })

        # Check for early returns
        if len(return_lines) > 2:
            early_returns = [
                line_num for line_num, _ in return_lines[:-1]
            ]
            if early_returns:
                comments.append({
                    'path': file.filename,
                    'line': start_line,
                    'body': (
                        f'Function "{function_name}" has multiple return points (lines: {", ".join(map(str, early_returns))}). '
                        'Consider restructuring to have a single return point.'
                    )
                })

    def _check_loop_complexity(self, content: list, file) -> list:
        """Check for overly complex loop structures."""
        comments = []
        in_loop = False
        loop_start = 0
        loop_depth = 0
        max_depth = self.config.get_rule(
            'loops', {}).get('max_nested_depth', 2)
        max_conditions = self.config.get_rule(
            'loops', {}).get('max_conditions', 3)

        # Track loop-related keywords and conditions
        loop_keywords = {'for', 'while'}
        condition_keywords = {'if', 'elif', 'else', 'break', 'continue'}

        current_conditions = 0
        current_depth = 0

        def check_line_complexity(line: str) -> int:
            """Count complexity factors in a single line."""
            complexity = 0
            # Count logical operators
            complexity += line.count(' and ') + line.count(' or ')
            # Count comparisons
            complexity += sum(1 for op in ['==', '!=',
                              '>', '<', '>=', '<='] if op in line)
            return complexity

        for line_num, line in enumerate(content, 1):
            stripped_line = line.strip()
            indent = len(line) - len(line.lstrip())

            # Skip comments and empty lines
            if not stripped_line or stripped_line.startswith('#'):
                continue

            # Check for loop start
            if any(stripped_line.startswith(keyword) for keyword in loop_keywords):
                if not in_loop:
                    in_loop = True
                    loop_start = line_num
                    current_conditions = check_line_complexity(stripped_line)
                current_depth = indent // 4  # Assuming 4 spaces per indent
                loop_depth = max(loop_depth, current_depth)

            # Track conditions within loops
            elif in_loop and any(keyword in stripped_line.split() for keyword in condition_keywords):
                current_conditions += 1 + check_line_complexity(stripped_line)

            # Check if we're exiting a loop
            elif in_loop and indent <= (loop_depth * 4):
                # Check depth
                if loop_depth > max_depth:
                    comments.append({
                        'path': file.filename,
                        'line': loop_start,
                        'body': (
                            f'Loop has too many nested levels (depth: {loop_depth}). '
                            f'Maximum allowed is {max_depth}. Consider refactoring.'
                        )
                    })

                # Check conditions
                if current_conditions > max_conditions:
                    comments.append({
                        'path': file.filename,
                        'line': loop_start,
                        'body': (
                            f'Loop has too many conditions ({current_conditions}). '
                            f'Maximum allowed is {max_conditions}. Consider simplifying.'
                        )
                    })

                in_loop = False
                current_conditions = 0

        return comments

    def _check_comment_quality(self, content: list, file) -> list:
        """Analyze comment quality and meaningfulness."""
        comments = []

        # Patterns for potentially low-quality comments
        low_quality_patterns = {
            'obvious': r'^\s*#\s*(?:end|start|begin|finish)',
            'todo': r'^\s*#\s*(?:todo|fixme|xxx)(?:\s|$)',
            'empty': r'^\s*#\s*$',
            'single_word': r'^\s*#\s*\w+\s*$',
        }

        # Words that might indicate meaningful comments
        meaningful_indicators = {
            'because', 'handles', 'prevents', 'ensures', 'implements',
            'fixes', 'addresses', 'resolves', 'workaround', 'note'
        }

        # Track comment blocks
        in_block_comment = False
        block_start = 0
        block_lines = []

        for line_num, line in enumerate(content, 1):
            stripped_line = line.strip()

            # Handle block comments
            if stripped_line.startswith('"""') or stripped_line.startswith("'''"):
                if not in_block_comment:
                    in_block_comment = True
                    block_start = line_num
                    block_lines = []
                else:
                    in_block_comment = False
                    self._analyze_comment_block(
                        comments, file, block_start, block_lines)
                continue

            if in_block_comment:
                block_lines.append(stripped_line)
                continue

            # Handle inline comments
            if '#' in line:
                comment_text = line[line.index('#')+1:].strip()

                # Check for low-quality patterns
                for pattern_name, pattern in low_quality_patterns.items():
                    if re.match(pattern, line, re.IGNORECASE):
                        if pattern_name == 'todo':
                            comments.append({
                                'path': file.filename,
                                'line': line_num,
                                'body': 'TODO comment found. Consider creating an issue instead.'
                            })
                        elif pattern_name != 'empty':
                            comments.append({
                                'path': file.filename,
                                'line': line_num,
                                'body': f'Low-quality comment detected. Consider making it more descriptive.'
                            })

                # Check comment length and content
                words = comment_text.split()
                if words and not any(word.lower() in meaningful_indicators for word in words):
                    if len(words) < 3:
                        comments.append({
                            'path': file.filename,
                            'line': line_num,
                            'body': 'Comment is too brief. Add more context to make it meaningful.'
                        })
                    elif all(len(word) < 4 for word in words):
                        comments.append({
                            'path': file.filename,
                            'line': line_num,
                            'body': 'Comment uses very short words. Consider adding more descriptive text.'
                        })

        return comments

    def _analyze_comment_block(self, comments: list, file, start_line: int,
                               block_lines: list) -> None:
        """Analyze a block comment for quality."""
        if not block_lines:
            return

        # Join lines and remove quote markers
        block_text = ' '.join(block_lines)
        block_text = re.sub(r'[\'"]', '', block_text).strip()

        # Check for common issues
        if len(block_text.split()) < 5:
            comments.append({
                'path': file.filename,
                'line': start_line,
                'body': 'Block comment is too brief. Add more detailed explanation.'
            })

        # Check for incomplete sentences
        sentences = re.split(r'[.!?]+', block_text)
        for sentence in sentences:
            if sentence.strip() and len(sentence.split()) < 3:
                comments.append({
                    'path': file.filename,
                    'line': start_line,
                    'body': 'Block comment contains incomplete sentences. Use full, descriptive sentences.'
                })
                break

    def _check_security_patterns(self, content: list, file) -> list:
        """Check for common security issues in code."""
        comments = []

        security_patterns = {
            'hardcoded_password': (
                r'(?:password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
                'Hardcoded password found. Use environment variables or secure storage.'
            ),
            'sql_injection': (
                r'execute\([^)]*\%.*?\)',
                'Possible SQL injection vulnerability. Use parameterized queries.'
            ),
            'shell_injection': (
                r'(?:os\.system|subprocess\.call|subprocess\.Popen)\([^)]*\+',
                'Possible shell injection vulnerability. Use subprocess with shell=False.'
            ),
            'weak_crypto': (
                r'(?:md5|sha1)\(',
                'Weak cryptographic hash found. Use stronger algorithms like SHA-256 or better.'
            ),
            'insecure_random': (
                r'random\.',
                'Using standard random module. Use secrets for cryptographic operations.'
            ),
            'debug_enabled': (
                r'(?:DEBUG|DEVELOPMENT)\s*=\s*True',
                'Debug mode enabled. Ensure this is disabled in production.'
            ),
            'sensitive_info_logging': (
                r'(?:logging|print|logger).*?(?:password|token|key|secret)',
                'Possible sensitive information in logs. Avoid logging credentials.'
            ),
        }

        # Additional security checks
        cors_patterns = {
            'cors_all': r"(?:CORS_ORIGIN_ALLOW_ALL|Access-Control-Allow-Origin:\s*\*)",
            'cors_unsafe': r"Access-Control-Allow-Origin:\s*'?http",
        }

        for line_num, line in enumerate(content, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue

            # Check each security pattern
            for pattern_name, (pattern, message) in security_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    comments.append({
                        'path': file.filename,
                        'line': line_num,
                        'body': f'Security issue: {message}'
                    })

            # Check CORS configurations
            for pattern in cors_patterns.values():
                if re.search(pattern, line):
                    comments.append({
                        'path': file.filename,
                        'line': line_num,
                        'body': 'Security issue: Overly permissive CORS configuration.'
                    })

            # Check for dangerous eval/exec usage
            if 'eval(' in line or 'exec(' in line:
                comments.append({
                    'path': file.filename,
                    'line': line_num,
                    'body': 'Security issue: Using eval() or exec() is dangerous. Consider safer alternatives.'
                })

            # Check for unsafe deserialization
            if 'pickle.loads' in line or 'yaml.load(' in line:
                comments.append({
                    'path': file.filename,
                    'line': line_num,
                    'body': 'Security issue: Unsafe deserialization. Use pickle.loads with trusted data only or yaml.safe_load().'
                })

        return comments

    def _check_test_coverage(self, content: list, file) -> list:
        """Analyze test coverage and quality."""
        comments = []

        # Only analyze test files
        if not file.filename.startswith('tests/') and not file.filename.endswith('_test.py'):
            return comments

        test_patterns = {
            'assertion': r'assert\s+\w+',
            'test_function': r'def\s+test_\w+',
            'mock_usage': r'(?:mock|patch|MagicMock)',
            'fixture_usage': r'@pytest\.fixture',
        }

        test_functions = []
        current_function = None
        function_start = 0
        assertion_count = 0
        has_docstring = False

        for line_num, line in enumerate(content, 1):
            stripped_line = line.strip()

            # Track test functions
            if re.match(test_patterns['test_function'], stripped_line):
                if current_function:
                    self._analyze_test_function(
                        comments, file, current_function,
                        function_start, assertion_count, has_docstring
                    )

                current_function = stripped_line[4:].split('(')[0].strip()
                function_start = line_num
                assertion_count = 0
                has_docstring = False
                test_functions.append(current_function)
                continue

            # Check for docstring
            if current_function and (
                stripped_line.startswith(
                    '"""') or stripped_line.startswith("'''")
            ):
                has_docstring = True

            # Count assertions
            if current_function and 'assert' in stripped_line:
                assertion_count += 1

        # Check last function
        if current_function:
            self._analyze_test_function(
                comments, file, current_function,
                function_start, assertion_count, has_docstring
            )

        # Check overall test file quality
        if test_functions:
            # Check for setup/teardown
            has_setup = any(
                'setup_method' in line or 'setUp' in line for line in content)
            has_teardown = any(
                'teardown_method' in line or 'tearDown' in line for line in content)

            if not has_setup and len(test_functions) > 3:
                comments.append({
                    'path': file.filename,
                    'line': 1,
                    'body': 'Consider adding setup method for test initialization.'
                })

            if not has_teardown and any('mock' in line for line in content):
                comments.append({
                    'path': file.filename,
                    'line': 1,
                    'body': 'Consider adding teardown method for proper cleanup of mocks.'
                })

            # Check for test organization
            if not any('class Test' in line for line in content) and len(test_functions) > 5:
                comments.append({
                    'path': file.filename,
                    'line': 1,
                    'body': 'Consider organizing tests into test classes for better structure.'
                })

        return comments

    def _analyze_test_function(self, comments: list, file, function_name: str,
                               start_line: int, assertion_count: int,
                               has_docstring: bool) -> None:
        """Analyze a test function for quality."""
        min_assertions = self.config.get_rule(
            'testing', {}).get('min_assertions', 1)
        require_docstrings = self.config.get_rule(
            'testing', {}).get('require_docstrings', True)

        if assertion_count < min_assertions:
            comments.append({
                'path': file.filename,
                'line': start_line,
                'body': (
                    f'Test function "{function_name}" has too few assertions '
                    f'({assertion_count}). Minimum expected is {min_assertions}.'
                )
            })

        if require_docstrings and not has_docstring:
            comments.append({
                'path': file.filename,
                'line': start_line,
                'body': f'Test function "{function_name}" is missing a docstring.'
            })

    def _check_dependency_cycles(self, content: list, file) -> list:
        """Check for circular dependencies in imports."""
        comments = []
        imports = []

        # Extract imports
        import_patterns = [
            r'^import\s+([\w.]+)',
            r'^from\s+([\w.]+)\s+import',
        ]

        for line_num, line in enumerate(content, 1):
            stripped_line = line.strip()

            # Skip comments and empty lines
            if not stripped_line or stripped_line.startswith('#'):
                continue

            # Collect imports
            for pattern in import_patterns:
                match = re.match(pattern, stripped_line)
                if match:
                    module = match.group(1)
                    imports.append((module, line_num))

        # Check for potential cycles
        current_module = os.path.splitext(file.filename)[0].replace('/', '.')
        for module, line_num in imports:
            # Check if module imports current module
            if self._has_circular_import(current_module, module, set()):
                comments.append({
                    'path': file.filename,
                    'line': line_num,
                    'body': f'Potential circular dependency detected between {current_module} and {module}.'
                })

        return comments

    def _has_circular_import(self, source: str, target: str, visited: set) -> bool:
        """Recursively check for circular imports."""
        if source == target:
            return True

        if target in visited:
            return False

        visited.add(target)

        try:
            # Try to find the module file
            module_path = target.replace('.', '/') + '.py'
            if not os.path.exists(module_path):
                return False

            # Read the module's imports
            with open(module_path, 'r') as f:
                content = f.read()

            # Extract imports
            imports = []
            for pattern in [r'^import\s+([\w.]+)', r'^from\s+([\w.]+)\s+import']:
                imports.extend(re.findall(pattern, content, re.MULTILINE))

            # Recursively check imports
            return any(self._has_circular_import(source, imp, visited.copy()) for imp in imports)

        except (IOError, OSError):
            return False

    def _check_performance_patterns(self, content: list, file) -> list:
        """Check for common performance anti-patterns."""
        comments = []

        performance_patterns = {
            'list_in_loop': (
                r'for.*:\s*.*append',
                'Consider using list comprehension or initializing with proper size'
            ),
            'dict_in_loop': (
                r'for.*:\s*.*\[\w+\]\s*=',
                'Consider using dict comprehension or initializing with proper size'
            ),
            'nested_loops': (
                r'^\s*for.*:\s*.*\n\s*for.*:',
                'Nested loops detected. Consider using more efficient data structures or algorithms'
            ),
            'string_concat': (
                r'\+=\s*["\']',
                'String concatenation in loop. Use join() or StringBuilder pattern'
            ),
            'global_variable': (
                r'global\s+\w+',
                'Global variable usage may cause performance issues. Consider alternative patterns'
            ),
        }

        # Additional performance checks
        in_function = False
        current_function = None
        function_locals = set()
        repeated_calls = {}

        for line_num, line in enumerate(content, 1):
            stripped_line = line.strip()

            # Skip comments and empty lines
            if not stripped_line or stripped_line.startswith('#'):
                continue

            # Track function definitions
            if stripped_line.startswith('def '):
                in_function = True
                current_function = stripped_line[4:].split('(')[0]
                function_locals = set()
                repeated_calls = {}

            # Check performance patterns
            for pattern_name, (pattern, message) in performance_patterns.items():
                if re.search(pattern, line, re.MULTILINE):
                    comments.append({
                        'path': file.filename,
                        'line': line_num,
                        'body': f'Performance issue: {message}'
                    })

            if in_function:
                # Track repeated function calls
                function_calls = re.findall(r'(\w+)\(', line)
                for func in function_calls:
                    if func not in function_locals:
                        repeated_calls[func] = repeated_calls.get(func, 0) + 1
                        if repeated_calls[func] > 3:
                            comments.append({
                                'path': file.filename,
                                'line': line_num,
                                'body': (
                                    f'Performance issue: Function "{func}" is called repeatedly. '
                                    'Consider caching the result.'
                                )
                            })

                # Check for inefficient container operations
                if 'in ' in line and any(container in line for container in ['list(', 'tuple(', '[']):
                    comments.append({
                        'path': file.filename,
                        'line': line_num,
                        'body': 'Performance issue: Using "in" with list/tuple. Consider using set for O(1) lookup.'
                    })

                # Check for inefficient string operations
                if re.search(r'(?:str|list|tuple)\(.*\).*\s+\+\s+', line):
                    comments.append({
                        'path': file.filename,
                        'line': line_num,
                        'body': 'Performance issue: Type conversion in concatenation. Consider moving outside loop.'
                    })

            # Check for function end
            if in_function and not line.startswith(' '):
                in_function = False

        return comments

    def _check_error_messages(self, content: list, file) -> list:
        """Check quality and helpfulness of error messages."""
        comments = []

        error_patterns = {
            'generic_error': (
                r'raise\s+(?:Exception|Error)\s*\(\s*["\'](?:error|failed|invalid)["\']',
                'Generic error message. Include specific details about the error.'
            ),
            'empty_except': (
                r'except[^:]+:\s*(?:pass|return|print)',
                'Empty except block or only printing. Provide meaningful error handling.'
            ),
            'uninformative_message': (
                r'raise\s+\w+\s*\(\s*["\'][^"\']{1,20}["\']\s*\)',
                'Error message might be too brief. Include more context.'
            ),
        }

        # Track error handling context
        in_try = False
        error_vars = set()

        for line_num, line in enumerate(content, 1):
            stripped_line = line.strip()

            # Skip comments
            if stripped_line.startswith('#'):
                continue

            # Track error variables
            if 'Exception' in line and '=' in line:
                var_name = line.split('=')[0].strip()
                error_vars.add(var_name)

            # Check raise statements
            if 'raise' in stripped_line:
                # Check for f-strings in error messages (good practice)
                if 'raise' in stripped_line and '"' in stripped_line and 'f"' not in stripped_line:
                    comments.append({
                        'path': file.filename,
                        'line': line_num,
                        'body': 'Consider using f-strings for dynamic error messages to include context.'
                    })

                # Check for error variable usage
                if any(var in stripped_line for var in error_vars):
                    comments.append({
                        'path': file.filename,
                        'line': line_num,
                        'body': 'Consider adding context when re-raising exceptions.'
                    })

            # Check error patterns
            for pattern_name, (pattern, message) in error_patterns.items():
                if re.search(pattern, stripped_line):
                    comments.append({
                        'path': file.filename,
                        'line': line_num,
                        'body': f'Error message quality: {message}'
                    })

            # Check for error message formatting
            if 'raise' in stripped_line and '%' in stripped_line:
                comments.append({
                    'path': file.filename,
                    'line': line_num,
                    'body': 'Use f-strings instead of % formatting in error messages for better readability.'
                })

            # Check for exception chaining
            if 'raise' in stripped_line and 'from' not in stripped_line and in_try:
                comments.append({
                    'path': file.filename,
                    'line': line_num,
                    'body': 'Use exception chaining with "raise ... from" to preserve error context.'
                })

            # Track try blocks
            if stripped_line.startswith('try:'):
                in_try = True
            elif in_try and not line.startswith(' '):
                in_try = False

        return comments

    def _check_api_documentation(self, content: list, file) -> list:
        """Analyze API documentation quality and completeness."""
        comments = []

        # Only check files that might contain API endpoints
        if not any(pattern in file.filename for pattern in ['api', 'views', 'endpoints', 'routes']):
            return comments

        doc_patterns = {
            'missing_response': (
                r'@(?:api|route|endpoint).*\ndef\s+\w+[^:]*:(?!\s*["\'].*response)',
                'API endpoint missing response documentation.'
            ),
            'missing_params': (
                r'@(?:api|route|endpoint).*\ndef\s+\w+[^:]*:(?!\s*["\'].*param)',
                'API endpoint missing parameter documentation.'
            ),
            'missing_errors': (
                r'@(?:api|route|endpoint).*\ndef\s+\w+[^:]*:(?!\s*["\'].*raises?)',
                'API endpoint missing error documentation.'
            ),
        }

        in_class = False
        class_name = None
        current_function = None
        docstring_lines = []
        collecting_docstring = False

        required_sections = {
            'Args', 'Returns', 'Raises', 'Example'
        }

        def check_docstring_completeness():
            if not docstring_lines:
                return

            docstring = '\n'.join(docstring_lines)
            found_sections = set()

            for section in required_sections:
                if f'{section}:' in docstring or f'{section}\n' in docstring:
                    found_sections.add(section)

            missing_sections = required_sections - found_sections
            if missing_sections and current_function:
                comments.append({
                    'path': file.filename,
                    'line': current_function[1],  # Line number
                    'body': f'API documentation for "{current_function[0]}" missing sections: {", ".join(missing_sections)}'
                })

            # Check for example code
            if 'Example' in found_sections and '```' not in docstring:
                comments.append({
                    'path': file.filename,
                    'line': current_function[1],
                    'body': 'Example section should include code blocks using markdown-style backticks.'
                })

        for line_num, line in enumerate(content, 1):
            stripped_line = line.strip()

            # Track class definitions
            if stripped_line.startswith('class '):
                in_class = True
                class_name = stripped_line[6:].split('(')[0].strip()

            # Track function definitions
            elif stripped_line.startswith('def '):
                if current_function:
                    check_docstring_completeness()

                func_name = stripped_line[4:].split('(')[0].strip()
                current_function = (
                    f'{class_name}.{func_name}' if in_class else func_name,
                    line_num
                )
                docstring_lines = []
                collecting_docstring = True

            # Collect docstring content
            elif collecting_docstring:
                if stripped_line.startswith('"""') or stripped_line.startswith("'''"):
                    if len(stripped_line) > 3 and stripped_line.endswith(stripped_line[:3]):
                        # Single line docstring
                        docstring_lines.append(stripped_line[3:-3])
                        collecting_docstring = False
                    elif docstring_lines:
                        # End of multi-line docstring
                        collecting_docstring = False
                    else:
                        # Start of multi-line docstring
                        if len(stripped_line) > 3:
                            docstring_lines.append(stripped_line[3:])
                elif collecting_docstring:
                    docstring_lines.append(stripped_line)

            # Check for common API patterns
            for pattern_name, (pattern, message) in doc_patterns.items():
                if re.search(pattern, line):
                    comments.append({
                        'path': file.filename,
                        'line': line_num,
                        'body': message
                    })

            # Check HTTP method documentation
            if '@' in line and any(method in line.lower() for method in ['get', 'post', 'put', 'delete']):
                next_line = content[line_num].strip(
                ) if line_num < len(content) else ''
                if not any(keyword in next_line.lower() for keyword in ['async', 'def']):
                    comments.append({
                        'path': file.filename,
                        'line': line_num,
                        'body': 'HTTP method decorator should be immediately followed by function definition.'
                    })

        # Check last function
        if current_function:
            check_docstring_completeness()

        return comments

    def _determine_import_group(self, import_line: str) -> str:
        """Determine which group an import belongs to."""
        # Remove comments
        import_line = import_line.split('#')[0].strip()

        # Extract module name
        if import_line.startswith('from '):
            module = import_line.split('from ')[1].split('import')[0].strip()
        else:
            module = import_line.split('import ')[1].strip()

        # Get first part of module path
        base_module = module.split('.')[0]

        # Standard library modules
        stdlib_modules = {
            'os', 'sys', 'pathlib', 'typing', 'datetime', 'json',
            'collections', 're', 'math', 'random', 'time', 'abc',
            'argparse', 'ast', 'asyncio', 'base64', 'bisect', 'calendar',
            'configparser', 'copy', 'csv', 'enum', 'functools', 'glob',
            'hashlib', 'inspect', 'io', 'itertools', 'logging', 'operator',
            'platform', 'queue', 'shutil', 'signal', 'socket', 'sqlite3',
            'statistics', 'string', 'subprocess', 'tempfile', 'textwrap',
            'threading', 'traceback', 'unittest', 'uuid', 'warnings', 'weakref',
            'xml', 'zipfile'
        }

        # Third-party modules (common ones)
        third_party_modules = {
            'pytest', 'requests', 'numpy', 'pandas', 'django', 'flask',
            'sqlalchemy', 'pydantic', 'fastapi', 'aiohttp', 'beautifulsoup4',
            'pillow', 'matplotlib', 'scipy', 'tensorflow', 'torch', 'yaml',
            'github', 'mock', 'setuptools', 'pip', 'wheel', 'virtualenv',
            'coverage', 'pylint', 'mypy', 'black', 'isort', 'flake8'
        }

        if base_module in stdlib_modules:
            return 'stdlib'
        elif base_module in third_party_modules:
            return 'third_party'
        return 'local'

    def _check_spacing(self, content: list, file) -> list:
        """Check spacing around operators and assignments."""
        comments = []
        if not self.config.get_rule('spacing.around_operators', True):
            return comments

        operators = ['+', '-', '*', '/', '=', '==', '!=', '>=', '<=']
        for line_num, line in enumerate(content, 1):
            for op in operators:
                if op in line and not f' {op} ' in line:
                    comments.append({
                        'path': file.filename,
                        'line': line_num,
                        'body': f'Missing spaces around operator "{op}"'
                    })
        return comments

    def _check_unused_code(self, content: list, file) -> list:
        """Check for unused functions."""
        comments = []
        if not self.config.get_rule('functions.warn_unused', True):
            return comments

        function_defs = {}
        function_calls = set()
        in_test_file = 'test' in file.filename.lower()

        # First pass: collect definitions and calls
        for line_num, line in enumerate(content, 1):
            stripped = line.strip()

            # Skip test functions
            if in_test_file and stripped.startswith('def test_'):
                continue

            if stripped.startswith('def '):
                func_name = stripped[4:].split('(')[0]
                function_defs[func_name] = line_num
            else:
                # Look for function calls
                for func in function_defs:
                    if f'{func}(' in line or f'{func} =' in line:
                        function_calls.add(func)

        # Check for unused functions
        for func, line_num in function_defs.items():
            if func not in function_calls and not func.startswith('_'):
                comments.append({
                    'path': file.filename,
                    'line': line_num,
                    'body': f'Unused function: "{func}"'
                })

        return comments


def main():
    # Get environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    github_repository = os.getenv('GITHUB_REPOSITORY')
    github_event_path = os.getenv('GITHUB_EVENT_PATH')

    if not all([github_token, github_repository, github_event_path]):
        print("Error: Required environment variables not found")
        sys.exit(1)

    # Read PR number from GitHub Actions event
    with open(github_event_path) as f:
        event_data = yaml.safe_load(f)
        pr_number = event_data['pull_request']['number']

    # Initialize and run reviewer
    reviewer = CodeReviewer(github_token)
    reviewer.review_pull_request(github_repository, pr_number)


if __name__ == "__main__":
    main()
