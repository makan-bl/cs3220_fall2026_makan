# Lab 5: Informed Search in Pac-Man World

Pac-Man must collect every food pellet in a generated maze, survive the ghosts, and reach the exit. Routes are planned with four informed search algorithms:

- A* with Euclidean distance
- A* with Manhattan distance
- IDA* with Manhattan distance
- RBFS with Manhattan distance

## Files

| File | Purpose |
|---|---|
| `Lab5.py` | Search algorithms, maze/world generation, Pac-Man agent and environment. Running it prints the task results and saves `lab5_paths.png`. |
| `lab5_app.py` | Streamlit web app: step through a run, play to the exit, or compare all four searches on the same maze. |
| `src/` | Provided course classes (Node, maze data, graph, problem, agent, environment). |
| `requirements.txt` | Packages for Streamlit Community Cloud. |

## Run locally

```bash
pip install -r requirements.txt
python Lab5.py            # console results + lab5_paths.png
streamlit run lab5_app.py # web app
```

## Maze rules

- Each move costs 1 performance point.
- Collecting food doubles current performance.
- Pac-Man beats a ghost only if its performance is higher than the ghost's power; winning costs 10% of performance.
- All food must be collected before the exit counts as success.

Note: Pac-Man always heads to the cheapest next food, which does not guarantee the cheapest complete tour.
