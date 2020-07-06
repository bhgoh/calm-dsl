"""
Calm DSL Sample Runbook used for testing runbook pause and play

"""

from calm.dsl.runbooks import runbook, runbook_json, parallel
from calm.dsl.runbooks import RunbookTask as Task


code = '''print "Start"
sleep(20)
print "End"'''


@runbook
def DslParallelRunbook():
    "Runbook Service example"

    Task.Exec.escript(name="root", script=code)
    with parallel as p:  # noqa

        def branch(p):
            Task.Exec.escript(name="Task1", script=code)

        def branch(p):  # noqa
            Task.Exec.escript(name="Task2", script=code)
            Task.Exec.escript(name="Task3", script=code)

        def branch(p):  # noqa
            Task.Exec.escript(name="Task4", script=code)
            Task.Exec.escript(name="Task5", script=code)


def main():
    print(runbook_json(DslParallelRunbook))


if __name__ == "__main__":
    main()
