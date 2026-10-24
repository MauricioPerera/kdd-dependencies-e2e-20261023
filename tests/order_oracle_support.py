"""Trusted oracle utilities; all subprocess transport uses explicit UTF-8."""
import ast
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run_cli(payload, *args, root=ROOT):
    env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONPATH', None)
    content = payload.encode('utf-8') if isinstance(payload, str) else payload
    result = subprocess.run([sys.executable, '-m', 'src.quote_cli', *args],
                            input=content, cwd=root, capture_output=True,
                            timeout=15, env=env, check=False)
    return result.returncode, result.stdout.decode('utf-8'), result.stderr.decode('utf-8')


def rejects_mutant(test, relative, function, replacement, oracle):
    """Require a successful control and assertion-only rejection of the mutant."""
    with tempfile.TemporaryDirectory(prefix='kdd-order-oracle-') as folder:
        root = Path(folder)
        for name in ('src', 'tests'):
            shutil.copytree(ROOT / name, root / name,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
        env.pop('PYTHONPATH', None)
        command = [sys.executable, '-m', 'unittest', oracle]

        def execute():
            result = subprocess.run(command, cwd=root, capture_output=True,
                                    encoding='utf-8', errors='strict', text=True,
                                    timeout=45, env=env, check=False)
            return result.returncode, result.stdout + result.stderr

        code, output = execute()
        test.assertEqual(code, 0, 'Control failed; mutant is inconclusive:\n' + output)
        test.assertRegex(output, r'Ran [1-9][0-9]* tests?')
        test.assertRegex(output, r'\bOK\b')
        path = root / relative
        source = path.read_text(encoding='utf-8')
        nodes = [n for n in ast.parse(source).body
                 if isinstance(n, ast.FunctionDef) and n.name == function]
        test.assertEqual(len(nodes), 1, 'Expected one production function')
        node = nodes[0]
        lines = source.splitlines(keepends=True)
        changed = ''.join(lines[:node.lineno - 1]) + replacement + '\n' + ''.join(lines[node.end_lineno:])
        path.write_text(changed, encoding='utf-8', newline='\n')
        code, output = execute()
        test.assertNotEqual(code, 0, 'Mutant survived')
        test.assertIn('AssertionError', output)
        test.assertIn('FAIL:', output)
        test.assertNotIn('ERROR:', output, 'Infrastructure/runtime failure is inconclusive')
        test.assertIsNotNone(re.search(r'FAILED \(failures=[1-9][0-9]*\)', output), output)
