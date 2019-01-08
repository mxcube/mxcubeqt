from QtImport import getQApp

def run_test():
    # Test individual widgets ------------------------------------------------
    tree_brick = None
    task_toolbox_brick = None

    # Search Bricks for overall logic tests
    for widget in getQApp().allWidgets():
        if hasattr(widget, "test"):
            widget.test()
        if widget.__class__.__name__ == "Qt4_TreeBrick":
            tree_brick = widget
        elif widget.__class__.__name__ == "Qt4_TaskToolBoxBrick":
            task_toolbox_brick = widget

    # Test overall logic -----------------------------------------------------
    # Select first sample tree item and mount it
    tree_brick.test_select_sample()
    task_toolbox_brick.task_tool_box_widget.collect_now_task(wait=True)

    
    getQApp().exit(0)
