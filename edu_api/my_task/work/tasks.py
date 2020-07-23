from my_task.main import app


@app.task(name='work')
def work():
    print('work')
    return "work"
