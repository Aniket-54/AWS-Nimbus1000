import sys
import os

sys.path.append(os.path.abspath("."))

from backend.api.search_candidates_lambda import service


query = "python machine learning sql"

results = service(query)

for r in results[:5]:

    print("Candidate:", r["Serial number"])
    print("Skills:", r["skills"])
    print("Score:", r["score"])
    print("----")