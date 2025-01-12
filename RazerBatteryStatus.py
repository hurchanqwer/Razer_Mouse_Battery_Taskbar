import re
import os
from pystray import MenuItem as item, Icon
from PIL import Image
import threading
import time

# 로컬 앱 데이터 경로 가져오기
LOG_FILE_PATH = os.path.expandvars(r"%LOCALAPPDATA%\Razer\Synapse3\Log\Razer Synapse 3.log")

# 배터리 상태 읽기 함수
def get_last_battery_state(file_path):
    """
    로그 파일에서 가장 최근의 배터리 상태를 읽어옵니다.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            # 역순으로 탐색하여 가장 최근의 "battery percentage" 찾기
            for line in reversed(file.readlines()):
                if "battery percentage" in line.lower():
                    match = re.search(r"\d+", line)
                    if match:
                        return int(match.group())  # 배터리 퍼센트 반환
        return None  # 배터리 상태 없음
    except (FileNotFoundError, IOError):
        print(f"Log file not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# 배터리 상태에 따라 아이콘 선택
def select_battery_icon(percentage):
    """
    배터리 퍼센트에 따라 적절한 아이콘 경로를 반환합니다.
    """
    if percentage is None:
        return "icons/battery0.png"
    elif percentage > 75:
        return "icons/battery100.png"
    elif percentage > 50:
        return "icons/battery75.png"
    elif percentage > 25:
        return "icons/battery50.png"
    elif percentage > 0:
        return "icons/battery25.png"
    else:
        return "icons/battery0.png"

# 트레이 아이콘 업데이트 함수
def update_tray_icon(icon):
    """
    배터리 상태를 주기적으로 업데이트하여 트레이 아이콘과 제목을 변경합니다.
    """
    while True:
        battery_percentage = get_last_battery_state(LOG_FILE_PATH)
        icon.title = f"Battery: {battery_percentage}%" if battery_percentage is not None else "Battery: N/A"
        
        # 배터리 상태에 맞는 아이콘 로드
        icon_path = select_battery_icon(battery_percentage)
        try:
            icon.icon = Image.open(icon_path)  # 아이콘 업데이트
        except Exception as e:
            print(f"Failed to load icon: {icon_path}. Error: {e}")

        time.sleep(60)  # 1분마다 업데이트

# 트레이 아이콘 실행
def setup_tray_icon():
    """
    트레이 아이콘을 설정하고 실행합니다.
    """
    initial_icon = Image.open("icons/battery100.png")  # 초기 아이콘
    menu = (item("Quit", quit_tray),)
    icon = Icon("BatteryStatus", initial_icon, "Battery: N/A", menu)
    
    # 배터리 상태 업데이트를 백그라운드에서 실행
    threading.Thread(target=update_tray_icon, args=(icon,), daemon=True).start()
    
    icon.run()

# 트레이 아이콘 종료
def quit_tray(icon, item):
    """
    트레이 아이콘을 종료합니다.
    """
    icon.stop()

# 실행
if __name__ == "__main__":
    setup_tray_icon()
