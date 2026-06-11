# send_pr.py
import sys
import json
import urllib.request
from datetime import datetime
from pathlib import Path 

LOG_FILE = Path(__file__).parent / "send_pr.log" 
 
def log(msg: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
  
def send_to_power_automate():  
    if len(sys.argv) < 3:
        log("ERROR: 인자 부족")
        return 
  
    user_name = sys.argv[1]
    branch_name = sys.argv[2]     
    commit_msg = sys.argv[3]

    # 1. 파워 오토메이트 트리거에서 복사한 HTTP POST URL을 여기에 붙여넣으세요.
    power_automate_url = "https://defaulta141d6e8fddb43098b7144753a7849.5a.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/30572e11ecf54bf19adbeb495a518bb1/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=ILLMYO6OKr7ys1lB6tij2uVpU1Nq5vhfKddFqxzTOIo" 

    # 2. 보낼 데이터 구성 (1단계 스키마 구조와 일치해야 합니다)
    payload = {
        "user_name" : user_name,
        "branch_name": branch_name,
        "commit_msg": commit_msg
    }
    
    data = json.dumps(payload).encode("utf-8")
    
    req = urllib.request.Request(
        power_automate_url, 
        data=data, 
        headers={"Content-Type": "application/json"}
    )

    try:
        log(f"파워 오토메이트로 데이터 전송 시도... (브랜치: {branch_name})")
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            log(f"전송 완료 — 응답 코드: {status}")
            print("PR 알림 트리거 완료")
    except Exception as e:
        log(f"ERROR: 전송 실패 — {e}")
        print(f"ERROR: {e}")

if __name__ == "__main__":
    send_to_power_automate()