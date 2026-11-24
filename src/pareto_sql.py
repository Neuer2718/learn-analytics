from pathlib import Path
import duckdb

PROJECT_DIR = Path(__file__).resolve().parent.parent
sql = (PROJECT_DIR / "src" / "pareto.sql").read_text()
print(duckdb.sql(sql).df())