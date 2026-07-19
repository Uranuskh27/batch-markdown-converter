# Batch Markdown Converter macOS 설계

## 목표

Finder에서 여러 파일과 폴더를 추가하고 목록을 확인한 후 Markdown으로 일괄 변환한다.
GUI는 스캔이나 변환 중에도 응답해야 하며, 한 파일의 실패가 다른 작업을 중단하면 안 된다.

## 아키텍처

```text
DropZone → Scanner(QThread) → JobManager → QProcess Worker × N
                                      └→ FileTable/Progress

QProcess Worker → MarkItDown → 임시 파일 → 최종 .md
```

MarkItDown을 GUI 프로세스의 스레드에서 직접 호출하지 않는다. 각 작업을 QProcess로
격리하여 충돌, 취소, 120초 기본 타임아웃을 처리한다. PyInstaller 빌드에서는 같은 앱
실행 파일을 `--worker SOURCE DESTINATION` 모드로 다시 실행한다.

## 상태 머신

```text
QUEUED → RUNNING → DONE
                 ├→ FAILED
                 ├→ CANCELLED
                 └→ SKIPPED
```

- 개별 실패는 큐를 중단하지 않는다.
- 처리 중 파일을 추가하면 기존 큐 뒤에 들어간다.
- 대기 작업 취소는 즉시 처리한다.
- 실행 작업 취소 및 타임아웃은 Worker 프로세스를 종료한다.
- 실패 및 취소 항목은 재시도할 수 있다.

## Scanner

- QThread에서 폴더를 재귀 탐색한다.
- 200개씩 결과를 GUI에 전달한다.
- 숨김파일, AppleDouble, 심볼릭 링크 디렉터리와 macOS 패키지를 제외한다.
- 파일 수 기본 상한은 10,000개, 파일 크기 기본 상한은 200MB다.
- 0바이트, Markdown 원본, 미지원 형식은 사유와 함께 SKIPPED로 표시한다.
- 한글 이름은 표시와 중복 키만 NFC로 정규화하며 실제 접근에는 원본 경로를 사용한다.

## 출력 정책

- 기본 위치는 원본 옆이다.
- 지정 폴더 모드에서는 드롭한 폴더의 상대 구조를 유지한다.
- 기본 충돌 정책은 `a (1).md` 형태의 자동 이름 변경이다.
- 동일 배치의 출력 경로를 메모리에서 예약하여 레이스를 막는다.
- Worker는 같은 폴더의 임시 파일에 UTF-8/LF로 기록한 뒤 `os.replace()`한다.
- 지정 출력 폴더는 배치 시작 전에 쓰기 가능 여부를 검사한다.
- PDF, Office, EPUB, ZIP, MSG는 변환 전에 파일 시그니처를 확인해 확장자만 위장한
  파일이나 명백히 손상된 파일을 실패 처리한다.

## 초기 지원 범위

PDF, DOCX, PPTX, XLSX, XLS, HTML, CSV, JSON, XML, EPUB, TXT, RTF, MSG, ZIP.
이미지 OCR, 오디오, URL 및 클라우드 변환은 후속 버전으로 미룬다.

## 패키징

개발 중에는 Python 3.12 가상환경을 사용한다. 개인용 `.app`은 PyInstaller로 arm64
빌드하며 MarkItDown의 동적 import를 명시적으로 수집한다. 배포 단계에서 Developer ID
서명, Apple 공증, DMG 생성을 추가한다.

한국어판과 영문판은 공용 변환·GUI 로직을 사용하고 표시 문구만 언어 계층에서 선택한다.
각 버전은 별도의 실행 진입점, 번들 식별자, QSettings 저장소를 사용하므로 동시에 설치하고
실행할 수 있다.

## 검증

자동화된 전체 테스트 범위와 최신 실행 결과는 [TESTING.md](TESTING.md)에 기록한다.
