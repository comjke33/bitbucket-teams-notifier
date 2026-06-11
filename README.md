### Overview 
* Automatically open Microsoft Teams chat with PR links upon Bitbucket push using Git Hooks.
* GIT hook을 사용해서 Bitbucket에 푸시가 들어갔을 경우 Microsoft Teams 채팅으로 자동 알림 가는 서비스

### Motivation
* When working in a team environment, manually notifying reviewers after every git push can be repetitive and easy to forget. To streamline this workflow, I developed this automation tool using Git Hooks and Microsoft Teams. It eliminates manual copy-pasting, ensures immediate communication with reviewers, and helps the team maintain a continuous and seamless code review loop.
* 프로젝트 협업 중 팀원에게 Pull 해달라는 메시지를 자꾸 까먹어서 만들게 됨

### Result 
<img width="632" height="227" alt="image" src="https://github.com/user-attachments/assets/ac171c71-c85e-4109-b19b-961df4318ecb" />


### How It Works
* BitBucket은 자체 WebHook 기능이 있다.
* 하지만 이 방식을 사용하지 않고, Microsoft Power Automate를 이용하였다.
* Power Automate는 Microsoft Application 기반으로 n8n처럼 자동 파이프라인을 구축할 때 효과적이다.

#### 1. Architecture Overview (구축 아키텍처)
* This automation is built entirely using lightweight, local tools combined with cloud-based workflow automation to achieve zero-click notification delivery. 
* 이 자동화 서비스는 개발자의 별도 추가 행동 없이(Zero-click) 알림을 전송하기 위해, 로컬 스크립트와 클라우드 기반 워크플로우 자동화를 결합하여 구축되었습니다.



#### 2. Core Components & Implementation (핵심 컴포넌트 구현)

* **Git Hook (`pre-push`)**
  * When a developer runs `git push`, the local `pre-push` hook triggers natively right before data transfer. 
  * 개발자가 `git push`를 수행하는 순간 데이터가 원격으로 넘어가기 직전 로컬 깃 훅이 실행됩니다.
  * It dynamically captures metadata: the committer's name (`git config user.name`), the current branch name, and the latest commit message, then passes them as arguments to the Python script.
  * 깃 설정을 통해 커밋한 유저의 이름, 현재 브랜치명, 최신 커밋 메시지를 동적으로 추출하여 파이썬 스크립트의 인자로 넘겨줍니다.

* **Asynchronous Backend Script (`send_pr.py`)**
  * To prevent blocking or slowing down the core Git workflow, the hook asynchronously spawns `send_pr.py` using Windows background process handlers (`cmd.exe /c start /b`).
  * 깃 푸시 프로세스가 지연되거나 멈추는 것을 방지하기 위해 윈도우 백그라운드 프로세스 실행기(`cmd.exe /c start /b`)를 통해 파이썬 스크립트를 비동기적으로 실행합니다.
  * The script packages the arguments into a JSON payload and transmits it via a secure HTTP POST request using Python's native `urllib` library, avoiding external dependency overhead.
  * 전달받은 메타데이터를 JSON 페이로드로 패키징한 후, 외부 라이브러리 의존성 없이 파이썬 내장 `urllib` 모듈만을 활용해 안전하게 Power Automate의 Webhook URL로 전송합니다.
  * 근데 그 뒤로, cmd 방식이 좀 귀찮아져서 Python Script 실행으로 다시 돌아왔습니다. (송신이 안되는 이유가 백그라운드 프로세스 문제가 아님을 알게 되었기 때문에 원상복구함)

* **Cloud Pipeline & Routing (Power Automate)**
  * An automated cloud flow is configured with an **"When an HTTP request is received"** green trigger node that exposes a unique Webhook URL.
  * 고유한 Webhook URL 주소를 제공하는 **"HTTP 요청이 수신된 경우"** 트리거를 통해 파이썬이 보낸 데이터를 수신합니다.
  * It parses the incoming JSON payload (`user_name`, `branch_name`, `commit_msg`) using a pre-defined JSON schema.
  * 미리 정의된 JSON 스키마를 바탕으로 들어온 푸시 메타데이터를 파싱합니다.

* **Direct Messaging Integration (Microsoft Teams)**
  * Finally, the flow executes the **"Post message in a chat or channel"** action.
  * 최종적으로 **"채팅 또는 채널에 메시지 게시"** 액션을 수행합니다.
  * By configuring the execution context as **`Post as: User`**, the automation acts under the developer's credentials. It automatically routes a structured, Markdown-formatted direct message (DM) straight into the reviewer's 1:1 chat window on Microsoft Teams, preserving development focus.
  * 게시자를 흐름 봇이 아닌 `User`로 설정하여 파워 오토메이트가 개발자의 권한을 위임받아 동작하게 했습니다. 리뷰어 사내 이메일 계정을 기반으로, 상대방과의 실제 1:1 대화방에 깔끔하게 포맷팅된 Markdown 문자 메시지를 꽂아 넣어 줍니다.

#### 3. To replicate this workflow in your environment:
1. 먼저 Pre-Push Hook을 설정하십시오. (파일도 함께 push하였음)
   * 해당 파일은 프로젝트 .git/hooks/ 에 sample 확장자로 제공되고 있습니다. (숨긴 파일 보기 필수!)
3. Power Automate에서 디자인하십시오. 
   * HTML으로 Trigger 설정 -> JSON 스키마 설정
   * 채팅 또는 채널에서 메시지 게시 -> 사용자/그룹채팅/그룹ID/메시지 설정
   * 다만 그룹 ID는 그대로 복사하면 오류 뜨기 때문에 conversation key값부터 날리고 넣으심 됩니당.
   * 메시지 설정은 @{triggerOutputs()?['body/user_name']} 이렇게 넣으시면 인자를 넣을 수 있습니다. 전 아래와 같이 설정했습니다.
        
🔔 @{triggerOutputs()?['body/user_name']} 님의 새로운 Push가 완료되었습니다!
- Branch: @{triggerOutputs()?['body/branch_name']}
- Commit Msg: @{triggerOutputs()?['body/commit_msg']}

Pull 부탁드립니다!

3. 저장 -> 테스트 (필수) 
   * 바로 push 테스트하지마세요. 원치 않는 동작이 발생할 수 있습니다.

