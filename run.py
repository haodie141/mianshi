#!/usr/bin/env python
"""
一键启动脚本（开发模式）
- 8000 端口：Django 后台（含 REST API）
- 7860 端口：Gradio 权限管理界面
"""
import os
import sys
import subprocess
import threading
import django
from pathlib import Path

# 1. 把项目根目录加入 PYTHONPATH（PyCharm 外部终端也兼容）
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# 2. 选择 settings（如果你用的是 settings_local.py 就改这里）
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clinic.settings")

# 3. 建表 / 迁移（只跑一次）
django.setup()
subprocess.run([sys.executable, "manage.py", "makemigrations"], check=False)
subprocess.run([sys.executable, "manage.py", "migrate"], check=False)

# 4. 启动 Django（8000）
def run_django():
    subprocess.run(
        [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

# 5. 启动 Gradio（7860）
def run_gradio():
    # 动态引入，避免 django 未初始化
    from gradio_ui.app import demo
    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )

if __name__ == "__main__":
    print(">>> 启动 Django 后台 http://127.0.0.1:8000")
    t1 = threading.Thread(target=run_django, daemon=True)
    t1.start()

    print(">>> 启动 Gradio 界面 http://127.0.0.1:7860")
    run_gradio()   # 主线程阻塞，Ctrl-C 即可全停