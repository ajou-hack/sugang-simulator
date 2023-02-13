# 수강신청 시뮬레이터

아주대학교 수강신청 연습을 위한 시뮬레이터입니다. (forked from [software-wanderer/potential-disco](https://github.com/software-wanderer/potential-disco)) 수강신청 외에 공지사항, 개인시간표, 여석조회 등 다른 기능은 구현되어있지 않습니다.

![](https://user-images.githubusercontent.com/6410412/218300888-2907ce24-6427-40eb-9063-97883080e9ce.png)

* 2022년 1학기에 개설된 실제 과목들이 연동되어 있습니다. 과목을 추가 또는 수정하려면 `static/db/db.xlsx` 파일을 변경해주세요.
* `main.py` 파일에서 수강신청 시작 시각을 지정해줄 수 있습니다. 부가적으로 이름, 학번, 학년, 최대신청학점 등을 지정할 수도 있습니다.
* **입력된 정보는 절대로 다른 서버로 전송되지 않습니다.** 따로 설정하지 않아도 기본값(홍길동)으로 사용할 수 있습니다.

## Getting Started

1. 프로젝트를 내려받고 필요한 패키지를 설치합니다.
   ```sh
   $ git clone https://github.com/ajou-hack/sugang-simulator
   $ cd sugang-simulator
   $ pip install -r requirements.txt
   ```
2. 서버를 실행합니다.
   ```sh
   $ make
   ```
3. 브라우저에서 '127.0.0.1:8000'에 접속합니다. 서버 실행 시각으로부터 1분 뒤 정각에 수강신청이 시작됩니다. 예를 들어, 13시 10분 37초에 서버를 실행했다면 13시 11분 0초에 수강신청이 시작됩니다.

## Screenshots

![](https://user-images.githubusercontent.com/6410412/218300879-9567bf3e-4895-456d-8629-ed6dd89336d6.png)

![](https://user-images.githubusercontent.com/6410412/218300921-e1b6b251-c676-4661-a3c0-10150693412d.png)
