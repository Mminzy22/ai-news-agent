# ai-news-agent

Hacker News, GeekNews, AI Times RSS/Atom feeds에서 AI/개발 뉴스를 수집해 한국어로 요약하고 Slack으로 보내는 자동화입니다.

## 설정

프로젝트 루트에 `.env` 파일을 만들고 아래 값을 넣습니다.

```env
OPENAI_API_KEY=sk-...
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

선택 설정:

```env
OPENAI_MODEL=gpt-5
MAX_ARTICLES=8
LOOKBACK_HOURS=24
```

## 로컬 실행

### 1. 뉴스 결과만 바로 확인하기

RSS에서 최신 뉴스를 가져오고 OpenAI로 요약한 뒤, Slack으로 보내지 않고 터미널에만 출력합니다.

```bash
python -m src.scheduler --dry-run --include-seen
```

처음 테스트할 때는 `--include-seen`을 붙이는 것을 추천합니다. 이미 발송한 기사 기록을 무시하고 현재 수집 결과를 바로 볼 수 있습니다.

### 2. 실제 발송 전 최종 확인하기

이미 보낸 기사는 제외하고, 실제 발송될 메시지만 터미널에서 확인합니다.

```bash
python -m src.scheduler --dry-run
```

출력에 `최근 기준에 맞는 새 기사가 없습니다.`가 나오면 새로 보낼 기사가 없다는 뜻입니다.

### 3. Slack으로 발송 테스트하기

아래 명령은 실제 Slack 채널로 메시지를 보냅니다.

```bash
python -m src.scheduler
```

성공하면 `data/seen.json`에 발송한 기사 ID가 저장되고, 다음 실행부터 같은 기사는 다시 보내지 않습니다.

발송된 Slack 메시지는 `뉴스 요약/YYYY-MM-DD.md`에도 저장됩니다.

### 4. 같은 기사로 Slack 발송을 다시 테스트하고 싶을 때

이미 보낸 기사도 다시 포함해서 Slack 발송을 테스트하려면 아래 명령을 사용합니다.

```bash
python -m src.scheduler --include-seen
```

주의: 이 명령은 같은 뉴스를 Slack에 중복 발송할 수 있습니다.

## 동작 방식

1. `config/sources.yml`에 있는 RSS/Atom 피드를 읽습니다.
2. 최근 `LOOKBACK_HOURS` 시간 안의 기사만 남깁니다.
3. AI/개발 관련 키워드로 점수를 매깁니다.
4. 비슷한 제목의 중복 기사를 제거합니다.
5. 상위 `MAX_ARTICLES`개를 OpenAI로 한국어 요약합니다.
6. Slack Incoming Webhook으로 메시지를 보냅니다.
7. 발송한 메시지를 `뉴스 요약/YYYY-MM-DD.md`에 저장합니다.

## 발송 기록 확인

로컬에서 Slack 발송을 실행하면 발송 내용이 날짜별 Markdown 파일로 저장됩니다.

```bash
ls "뉴스 요약"
cat "뉴스 요약/2026-06-13.md"
```

GitHub Actions에서 실행된 경우에는 `뉴스 요약/YYYY-MM-DD.md` 파일을 자동으로 커밋하고 push합니다.

## 뉴스 소스 수정

뉴스 소스는 `config/sources.yml`에서 관리합니다.

```yaml
sources:
  - name: GeekNews
    url: https://news.hada.io/rss/news
    type: atom
    language: ko
    weight: 1.3
```

`weight`가 높을수록 같은 조건에서 더 우선적으로 선택됩니다.

## 자주 쓰는 명령

```bash
# 요약 결과만 확인
python -m src.scheduler --dry-run --include-seen

# 실제 발송될 새 기사만 확인
python -m src.scheduler --dry-run

# Slack 발송
python -m src.scheduler

# 테스트 실행
python -m unittest discover
```

## GitHub Actions

`.github/workflows/daily-news.yml`는 매일 오전 9시 KST에 실행됩니다.

GitHub 저장소 Settings → Secrets and variables → Actions에 아래 secrets를 추가해야 합니다.

- `OPENAI_API_KEY`
- `SLACK_WEBHOOK_URL`

Actions 실행 후에는 Slack에 보낸 메시지가 `뉴스 요약/YYYY-MM-DD.md`로 커밋됩니다. 이 동작을 위해 workflow에 `contents: write` 권한이 설정되어 있습니다.
