import sys
import io
import contextlib

class PythonSandbox:
    @staticmethod
    def execute(code: str):
        # Extremely simplified production sandbox. 
        # In a real environment, this should run in a separate Docker container/gVisor.
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            try:
                # Restricting globals for a bit of safety (not full proof)
                safe_globals = {"__builtins__": __builtins__}
                exec(code, safe_globals)
            except Exception as e:
                return f"Execution Error: {str(e)}"
        return f.getvalue()

sandbox = PythonSandbox()
