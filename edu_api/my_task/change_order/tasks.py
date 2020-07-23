from my_task.main import app


@app.task(name="check_order")
def check_order():
    print("判断订单是否超时")
