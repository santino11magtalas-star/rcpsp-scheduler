# suggested commit order

don't dump the whole repo in one commit -- that's the #1 thing that looks
auto-generated. commit it in pieces as you actually wire it up. rough order:

1. setup files
   git add .gitignore requirements.txt README.md
   git commit -m "initial repo setup"

2. the model
   git add src/rcpsp/__init__.py src/rcpsp/model.py
   git commit -m "add Activity/Project model + topological sort"

3. sample data
   git add data/
   git commit -m "add sample .sm instance for testing"

4. parser
   git add src/rcpsp/parser.py
   git commit -m "psplib .sm parser (wip)"
   # after you test it on a real psplib file and fix the resource row issue:
   git commit -am "fix resource availabilities parsing"

5. tests + demo
   git add tests/ demo.py
   git commit -m "parser tests + demo script"

after this: one branch per feature (cpm, sgs, annealing, exact...) and PR them
in. with 6 people that history will look exactly like what it is -- real work.
