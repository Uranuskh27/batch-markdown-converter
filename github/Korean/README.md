# Batch Markdown Converter for macOS

여러 문서와 폴더를 드래그 앤 드롭하여 Markdown으로 한꺼번에 변환하는 한국어 macOS
데스크톱 앱입니다. 변환 엔진으로 Microsoft의 오픈소스 프로젝트
[MarkItDown](https://github.com/microsoft/markitdown)을 사용합니다.

> 이 프로젝트는 Microsoft의 공식 제품이 아닌 독립적인 오픈소스 GUI 프로젝트입니다.

## 주요 기능

- 여러 파일과 폴더를 한 번에 추가하고 하위 폴더까지 재귀적으로 검색
- 앱이 멈추지 않도록 파일별 변환 프로세스를 분리하여 실행
- 개별 파일의 대기, 변환, 완료, 실패, 건너뜀, 취소 상태 표시
- 실패한 파일만 다시 시도하고 실행 중인 작업 취소
- 원본 파일 옆 또는 사용자가 지정한 폴더에 Markdown 저장
- 동일한 파일명이 있을 때 자동 이름 변경, 건너뛰기 또는 덮어쓰기
- 일반 모드와 다크 모드를 전환하는 해·달 슬라이드 스위치
- 변환 진행률에 맞춰 달리는 강아지 진행 표시
- 선택한 경우 변환 완료 후 Finder에서 출력 폴더 자동 열기
- 모든 문서를 사용자의 Mac에서 로컬로 처리

## 지원 형식

PDF, DOCX, PPTX, XLSX, XLS, HTML, CSV, JSON, XML, EPUB, TXT, RTF, MSG, ZIP

현재 버전은 이미지 OCR, 이미지 파일, 오디오, URL 및 클라우드 문서 변환을 지원하지
않습니다.

## 시스템 요구사항

- macOS 13 Ventura 이상
- Apple Silicon Mac
- 현재 제공되는 DMG는 arm64 전용

## 설치

1. GitHub 저장소의 **Releases**에서 최신 `Batch-Markdown-Converter-Korean-*-arm64.dmg`를 받습니다.
2. DMG를 열고 `Batch Markdown Converter Korean.app`을 `Applications` 폴더로 드래그합니다.
3. 응용 프로그램 폴더에서 **Batch Markdown Converter Korean**을 실행합니다.

현재 테스트 빌드는 Apple 공증을 받지 않은 ad-hoc 서명 빌드입니다. 반드시 공식 Release에서
받은 파일인지 확인하고 함께 제공되는 `SHA256SUMS.txt`로 무결성을 검증하세요. macOS가
첫 실행을 차단하면 Finder에서 앱을 Control-클릭한 다음 **열기**를 선택할 수 있습니다.

## 사용 방법

1. 파일은 **파일 추가**로 선택하고, 파일이나 폴더는 창의 드롭 영역으로 끌어놓습니다.
2. 결과를 원본 옆에 저장할지 지정 폴더에 저장할지 선택합니다.
3. 필요한 경우 설정에서 동시 변환 수, 파일당 시간제한, 파일명 충돌 정책과 완료 후 폴더
   열기를 변경합니다.
4. **모두 변환**을 누릅니다.

파일 하나의 변환이 실패해도 나머지 작업은 계속됩니다. 원본 파일은 수정하지 않습니다.

## 소스에서 실행

Python 3.12 사용을 권장합니다.

```sh
git clone <이 저장소의 URL>
cd <저장소 디렉터리>
./scripts/setup.command
./scripts/run.command
```

## 테스트와 빌드

```sh
.venv/bin/pytest
./scripts/build_app.command
./scripts/package_releases.command
./scripts/verify_releases.command
```

`package_releases.command`는 한국어판과 영문판 DMG를 함께 만들며, 이 저장소에서 배포할
때는 `release/Korean/`의 DMG와 체크섬을 GitHub Release에 첨부하면 됩니다. 공개 배포용
Developer ID 서명과 Apple 공증 절차는 `DISTRIBUTION.md`를 참고하세요.

## 개인정보 보호

추가한 문서는 앱 내부의 로컬 변환 프로세스에서 처리됩니다. 이 GUI는 변환할 문서를
외부 서버로 업로드하지 않습니다. 민감한 문서도 사용자가 선택한 출력 위치에만 결과가
저장됩니다.

## 기여하기

버그 제보와 개선 제안을 환영합니다. 문제를 등록할 때 macOS 버전, Mac 종류, 입력 형식,
재현 방법과 표시된 오류를 함께 적어주세요. 개인정보나 원본 문서는 공개 Issue에 첨부하지
마세요.

코드를 수정했다면 다음 명령으로 전체 테스트를 먼저 실행해주세요.

```sh
.venv/bin/pytest
```

## 라이선스

이 GUI 프로젝트는 [MIT License](LICENSE)로 배포됩니다. 변환 엔진인 Microsoft
MarkItDown 역시 MIT License로 제공됩니다. 포함된 라이브러리의 고지 사항은
`THIRD_PARTY_NOTICES.md`에서 확인할 수 있습니다. Qt/PySide는 LGPLv3 조건으로 사용하며,
대응 소스와 라이브러리 교체 방법은 `COMPLIANCE.md`와 `BUILD_AND_RELINK.md`에 정리되어
있습니다. 이 프로젝트는 Microsoft의 공식 제품이 아닙니다.
