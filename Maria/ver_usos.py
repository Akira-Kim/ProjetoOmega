import sqlite3
import os

db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conhecimento.db")
con = sqlite3.connect(db)
cur = con.cursor()
cur.execute(
    """
    SELECT pergunta, resposta, vezes_usada
    FROM conhecimento
    WHERE vezes_usada > 0
    ORDER BY vezes_usada DESC
    LIMIT 10
    """
)
print("Respostas já usadas:")
for p, r, v in cur.fetchall():
    print(f"  [{v}x] {p} -> {r[:50]}")
con.close()