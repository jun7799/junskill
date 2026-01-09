#!/usr/bin/env python3
"""
每日热门文章猎手 - 定时任务调度器

支持两种运行模式：
1. 手动触发模式：python scheduler.py --mode manual
2. 自动定时模式：python scheduler.py --mode schedule --cron "0 9 * * *"

执行流程：
1. 调用fetch_articles.py获取最新文章
2. 调用calculate_trending.py计算热度分数
3. 过滤低热度文章
4. 调用feishu_client.py写入飞书表格
5. 生成执行报告
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict
import json

try:
    import schedule
    import time
except ImportError:
    schedule = None
    print("警告: 未安装 schedule 库，定时模式不可用")
    print("安装命令: pip install schedule")

SCRIPT_DIR = Path(__file__).parent


class TaskScheduler:
    """任务调度器"""

    def __init__(self):
        self.script_dir = SCRIPT_DIR
        self.report = {
            "start_time": datetime.now().isoformat(),
            "steps": [],
            "success": False,
            "error": None
        }

    def log_step(self, step_name: str, success: bool, message: str = "", data: Dict = None):
        """记录执行步骤"""
        self.report["steps"].append({
            "step": step_name,
            "success": success,
            "message": message,
            "data": data or {},
            "time": datetime.now().isoformat()
        })

    def run_script(self, script_name: str) -> bool:
        """运行Python脚本"""
        script_path = self.script_dir / script_name

        if not script_path.exists():
            self.log_step(f"运行{script_name}", False, f"脚本不存在: {script_path}")
            return False

        try:
            print(f"\n{'='*50}")
            print(f"执行: {script_name}")
            print(f"{'='*50}")

            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                cwd=str(self.script_dir.parent)
            )

            # 打印输出
            if result.stdout:
                print(result.stdout)

            if result.returncode == 0:
                self.log_step(f"运行{script_name}", True, "执行成功")
                return True
            else:
                if result.stderr:
                    print(result.stderr)
                self.log_step(f"运行{script_name}", False, f"执行失败 (退出码: {result.returncode})")
                return False

        except Exception as e:
            self.log_step(f"运行{script_name}", False, f"异常: {e}")
            return False

    def execute_pipeline(self) -> bool:
        """执行完整的抓取流程"""
        print("\n" + "="*60)
        print("每日热门文章猎手 - 开始执行")
        print("="*60)

        # 步骤1: 抓取文章
        if not self.run_script("fetch_articles.py"):
            self.report["success"] = False
            self.report["error"] = "文章抓取失败"
            self.generate_report()
            return False

        # 步骤2: 计算热度
        if not self.run_script("calculate_trending.py"):
            self.report["success"] = False
            self.report["error"] = "热度计算失败"
            self.generate_report()
            return False

        # 步骤3: 写入飞书
        if not self.run_script("feishu_client.py"):
            self.report["success"] = False
            self.report["error"] = "飞书写入失败"
            self.generate_report()
            return False

        # 全部成功
        self.report["success"] = True
        self.report["end_time"] = datetime.now().isoformat()

        print("\n" + "="*60)
        print("执行完成！")
        print("="*60)

        self.generate_report()
        return True

    def generate_report(self):
        """生成执行报告"""
        self.report["end_time"] = datetime.now().isoformat()

        # 计算耗时
        try:
            start = datetime.fromisoformat(self.report["start_time"])
            end = datetime.fromisoformat(self.report["end_time"])
            duration = (end - start).total_seconds()
            self.report["duration_seconds"] = duration
        except:
            pass

        # 保存报告
        report_path = self.script_dir.parent / "data" / "execution_report.json"
        os.makedirs(report_path.parent, exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.report, f, ensure_ascii=False, indent=2)

        # 打印摘要
        print("\n执行摘要:")
        print(f"  状态: {'成功' if self.report['success'] else '失败'}")
        print(f"  耗时: {self.report.get('duration_seconds', 0):.2f}秒")
        print(f"  执行步骤: {len(self.report['steps'])}")

        if not self.report["success"]:
            print(f"  错误: {self.report.get('error', '未知错误')}")

    def run_scheduled(self, cron_expression: str = "0 9 * * *"):
        """运行定时任务模式"""
        if schedule is None:
            print("错误: schedule 库未安装，无法使用定时模式")
            print("请安装: pip install schedule")
            return False

        print(f"\n定时任务模式已启动")
        print(f"执行周期: {cron_expression}")
        print(f"按 Ctrl+C 停止\n")

        # 解析cron表达式（简化版，仅支持基础格式）
        # 格式: 分 时 日 月 周
        parts = cron_expression.split()
        if len(parts) == 5:
            minute, hour = parts[0], parts[1]

            def job():
                self.execute_pipeline()

            try:
                if minute == "0" and hour == "9":
                    schedule.every().day.at("09:00").do(job)
                elif minute == "0" and hour == "8":
                    schedule.every().day.at("08:00").do(job)
                elif minute == "0" and hour == "0":
                    schedule.every().day.at("00:00").do(job)
                else:
                    # 自定义时间
                    time_str = f"{hour}:{minute}"
                    schedule.every().day.at(time_str).do(job)

                print(f"已设置定时任务，每天 {hour}:{minute} 执行\n")

                # 首次执行
                print("首次执行中...")
                job()

                # 持续运行
                while True:
                    schedule.run_pending()
                    time.sleep(60)  # 每分钟检查一次

            except KeyboardInterrupt:
                print("\n\n定时任务已停止")
            except Exception as e:
                print(f"\n定时任务错误: {e}")
                return False
        else:
            print(f"错误: 不支持的 cron 表达式格式: {cron_expression}")
            print("支持格式: 分 时 日 月 周 (例如: 0 9 * * * 表示每天9点)")
            return False

        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="每日热门文章猎手 - 任务调度器")
    parser.add_argument(
        "--mode",
        choices=["manual", "schedule"],
        default="manual",
        help="运行模式: manual=手动触发, schedule=定时运行"
    )
    parser.add_argument(
        "--cron",
        default="0 9 * * *",
        help="定时任务cron表达式 (默认: 0 9 * * * = 每天早上9点)"
    )

    args = parser.parse_args()

    scheduler = TaskScheduler()

    if args.mode == "manual":
        # 手动模式：立即执行一次
        success = scheduler.execute_pipeline()
        sys.exit(0 if success else 1)

    elif args.mode == "schedule":
        # 定时模式：按计划持续运行
        success = scheduler.run_scheduled(args.cron)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
