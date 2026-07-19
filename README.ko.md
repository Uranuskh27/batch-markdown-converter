# Batch Markdown Converter for macOS

여러 문서나 폴더를 드래그 앤 드롭하여 Markdown으로 일괄 변환하는 개인용 macOS 앱입니다.

## 주요 기능

- 파일과 폴더 재귀 스캔
- 파일별 대기, 변환, 완료, 실패, 건너뜀, 취소 상태
- 최대 2개 기본 동시 변환과 파일별 타임아웃
- 변환 Worker 프로세스 격리
- 드롭다운 없이 바로 선택하는 세그먼트 컨트롤로 원본 옆 또는 지정 폴더 저장
- 자동 이름 변경, 건너뛰기, 덮어쓰기 충돌 정책
- 임시 파일을 이용한 원자적 저장
- 실패한 파일만 재시도
- 스위치 안의 해·달 아이콘과 움직이는 손잡이로 일반/다크 모드 전환 및 선택 저장
- 선택 시 변환 완료 후 Finder에서 출력 폴더 자동 열기(기본값 꺼짐)
- 창 너비를 쓰는 독립 행에서 통통한 시바·코기풍 강아지가 네 다리를 움직이며 달리는 진행 바

지원 형식은 PDF, DOCX, PPTX, XLSX, XLS, HTML, CSV, JSON, XML, EPUB, TXT,
RTF, MSG, ZIP입니다. OCR, 이미지, 오디오, URL 변환은 초기 버전에서 제외합니다.

## 처음 실행

Finder에서 다음 파일을 차례로 실행합니다.

1. `scripts/setup.command`
2. `scripts/run.command`

터미널에서는 다음처럼 실행할 수 있습니다.

```sh
./scripts/setup.command
./scripts/run.command
```

## 테스트

```sh
.venv/bin/pytest
```

자동화 테스트 코드는 GitHub에 포함합니다. 테스트가 만드는 문서와 변환 결과는 시스템
임시 폴더에서 처리되어 저장소에 남지 않습니다. 개인 문서나 외부 대용량 fixture로
추가 시험할 때는 Git에서 제외된 `local-test-data/`에 보관합니다. 테스트 보고서를
파일로 저장할 때는 `test-results/`를 사용합니다.

## 개인용 앱 빌드

```sh
./scripts/build_app.command
```

결과 앱은 `build/dist/Batch Markdown Converter Korean.app`에 생성됩니다. 현재 빌드는 로컬 임시 서명만
사용하므로 다른 Mac에 배포하려면 Developer ID 서명과 Apple 공증이 필요합니다.

## 별도 영문판

한국어판과 동일한 기능을 갖춘 영문판은 별도의 설정 저장소와 앱 번들을 사용합니다.

```sh
./scripts/run_english.command
./scripts/build_english_app.command
```

영문 앱은 `build/dist/Batch Markdown Converter English.app`에 생성되며 한국어판과 동시에 사용할 수
있습니다.

## 언어별 DMG 배포

한글판과 영문판 DMG, 설치 안내 및 SHA-256 체크섬을 별도 폴더로 한 번에 생성합니다.

```sh
./scripts/package_releases.command
```

산출물은 `release/Korean/`과 `release/English/`에 각각 저장됩니다. 공개 배포용
Developer ID 서명과 Apple 공증 방법은 [DISTRIBUTION.md](DISTRIBUTION.md)를 참고하세요.

패키징 과정은 Qt/PySide의 LGPL 대응 소스도 `release/Source-Code/`에 준비합니다. GitHub
Release에는 언어별 DMG와 체크섬뿐 아니라 이 폴더의 소스 아카이브와 체크섬도 함께
첨부해야 합니다. 전체 오픈소스 배포 정책은 [COMPLIANCE.md](COMPLIANCE.md), Qt 라이브러리
교체 방법은 [BUILD_AND_RELINK.md](BUILD_AND_RELINK.md)를 참고하세요.

각 언어의 GitHub 업로드 파일은 완전히 분리해서 생성할 수 있습니다.

```sh
./scripts/prepare_korean_github_release.command
./scripts/prepare_english_github_release.command
```

결과는 각각 `release/GitHub-Upload-Korean/`과 `release/GitHub-Upload-English/`에 생성됩니다.
각 폴더의 6개 파일을 해당 언어의 GitHub Release에 모두 업로드하세요.

자세한 구조와 정책은 [DESIGN.md](DESIGN.md)를 참고하세요.
전체 테스트 범위와 검증 결과는 [TESTING.md](TESTING.md)에 정리되어 있습니다.
