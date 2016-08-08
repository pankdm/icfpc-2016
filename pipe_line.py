import os
import json
import time

DIR = "./solve_convex/sols"
LATEST = "./latest_snapshot"
DEBUG = False
# IGNORE_TIME = 60 * 60 * 2
IGNORE_TIME = 0
APPROX = "./approx_queue.txt"
APPROX2 = "./approx2_queue.txt"
NEW = "./new_queue.txt"
ME = 137


file_names = [f for f in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, f))]

class Task:
  def __init__(self, task_id, score):
    self.task_id = task_id
    self.score = score
    self.sn = 0.0
    self.points_score = 0

unsolved_attempted_tasks = {}
solved_tasks = {}
tasks = {}
rejected = []

for f in file_names:
  s = f.split("_")
  if len(s) < 2:
    rejected.append(f[1:])
    continue
  score = s[1]
  task_id = int(s[0][1:])
  if float(score) < 1.0:
    unsolved_attempted_tasks[task_id] = Task(task_id, score)
  if float(score) == 1.0:
    solved_tasks[task_id] = Task(task_id, score)
  tasks[task_id] = Task(task_id, score)

approx_queue = []
approx2_queue = []
new_queue = []
with open(LATEST) as latest_data:
  data = json.load(latest_data)

#  all_id = []

  for problem in data["problems"]:
    owner = problem["owner"]
    if owner == str(ME):
      continue
    s_time = problem["publish_time"]
    if s_time + IGNORE_TIME > time.time():
      continue
    s = problem["solution_size"]
    t_id = problem["problem_id"]
    n = 1

    sum_res = 0
    for r in problem["ranking"]:
      if r["resemblance"] == 1.0:
        n += 1
      else:
          sum_res += r["resemblance"]



    if t_id in solved_tasks:
      continue

    elif t_id in rejected:
      continue

    elif t_id in unsolved_attempted_tasks:
      tt = unsolved_attempted_tasks[t_id]
      tt.sn = float(s) / n
      if tt.score > 0 and sum_res > 0:
          points_score = (float(s) / n) * float(tt.score) / sum_res
      else:
          points_score = 0
      tt.points_score = points_score

      approx_queue.append(unsolved_attempted_tasks[t_id])
      approx2_queue.append(unsolved_attempted_tasks[t_id])

    elif t_id not in tasks:
      t = Task(t_id, 0)
      t.sn = float(s) / n
      new_queue.append(t)

  approx_queue.sort(key=lambda x: x.sn, reverse=True)
  approx2_queue.sort(key = lambda x: x.sn * (1 - float(x.score)), reverse=True)
  new_queue.sort(key=lambda x: x.sn, reverse=True)

  def write_queue(file_name, tasks_queue):
    print 'writing to ', file_name
    with open(file_name, 'w') as queue_f:
      for t in tasks_queue:
        line = '{} {} {} {}\n'.format(
            t.task_id,
            t.sn,
            t.score,
            t.points_score
        )
        queue_f.write(line)

  write_queue(APPROX2, approx2_queue)
  write_queue(APPROX, approx_queue)
  write_queue(NEW, new_queue)

  #
  # with open(NEW, 'w') as new_f:
  #   for t in new_queue:
  #     new_f.write(str(t.task_id) + " " + str(t.sn) + "\n")
