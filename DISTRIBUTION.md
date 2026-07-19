# macOS 배포 가이드

## 현재 배포 수준

앱 기능, arm64 번들, 언어별 설정 분리와 DMG 패키징은 완료되어 있습니다. Apple
Developer ID 없이 만든 DMG도 직접 전달하거나 GitHub Release에 올릴 수 있지만,
다른 사용자의 Mac에서는 Gatekeeper 경고가 나타납니다.

경고 없는 공개 배포에는 다음이 필요합니다.

1. Apple Developer Program 가입
2. `Developer ID Application` 인증서 설치
3. Hardened Runtime과 타임스탬프를 사용한 앱 서명
4. Apple notary service 제출 및 DMG 티켓 스테이플

## 언어별 패키지 생성

다음 명령은 한글판과 영문판을 다시 빌드하고 각각의 DMG와 SHA-256 체크섬을 만듭니다.

```sh
./scripts/package_releases.command
```

산출물:

```text
release/
├── Korean/
│   ├── Batch-Markdown-Converter-Korean-0.1.0-arm64.dmg
│   ├── README.txt
│   └── SHA256SUMS.txt
└── English/
    ├── Batch-Markdown-Converter-English-0.1.0-arm64.dmg
    ├── README.txt
    └── SHA256SUMS.txt
```

이미 앱 번들을 빌드했다면 다음처럼 재빌드를 생략할 수 있습니다.

```sh
SKIP_BUILD=1 ./scripts/package_releases.command
```

## Developer ID 서명과 공증

먼저 공증 자격 증명을 Keychain에 한 번 저장합니다.

```sh
xcrun notarytool store-credentials batch-markdown-converter-notary
```

그다음 인증서 이름과 Keychain profile을 지정해 같은 패키징 명령을 실행합니다.

```sh
SIGNING_IDENTITY="Developer ID Application: YOUR NAME (TEAMID)" \
NOTARY_PROFILE="batch-markdown-converter-notary" \
./scripts/package_releases.command
```

`NOTARY_PROFILE`이 있으면 스크립트가 두 DMG를 각각 제출하고 완료를 기다린 뒤 티켓을
스테이플하고 검증합니다. 인증서나 profile이 없으면 로컬 임시 서명 DMG만 생성합니다.

## GitHub Release

각 언어 폴더의 DMG와 `SHA256SUMS.txt`를 같은 GitHub Release에 업로드합니다. 또한
`release/Source-Code/`의 PySide6, Qt Base, Qt SVG 소스 아카이브와 체크섬을 모두 같은
Release에 첨부합니다. 이 파일들은 LGPL 대응 소스이므로 DMG만 단독으로 공개하지 않습니다.

한글판과 영문판은 아래 명령으로 각각 독립된 업로드 폴더를 만들 수 있습니다. 두 명령
모두 공용 소스에서 두 앱이 정상 동작하는지 함께 검증하지만, 각 업로드 폴더에는 해당
언어의 DMG만 넣습니다.

```sh
./scripts/prepare_korean_github_release.command
./scripts/prepare_english_github_release.command
```

성공하면 `release/GitHub-Upload-Korean/`과 `release/GitHub-Upload-English/`에 각각 다음
6개 파일이 생성됩니다.

- 해당 언어의 DMG
- DMG 전용 SHA-256 체크섬
- PySide6, Qt Base, Qt SVG 대응 소스 아카이브 3개
- LGPL 소스 전용 SHA-256 체크섬

같은 이름의 `SHA256SUMS.txt`가 충돌하지 않도록 공개용 체크섬은 각각
`*.dmg.sha256.txt`와 `LGPL-Sources-SHA256SUMS.txt`로 구분됩니다. 이 폴더의 모든 파일을
동일한 GitHub Release에 업로드합니다.

GitHub CLI를 설치하고 로그인했으며 소스가 커밋·푸시된 상태라면 다음 명령으로 각 언어의
태그와 Release 생성, 6개 파일 업로드까지 한 번에 실행할 수 있습니다.

```sh
./scripts/publish_korean_github_release.command
./scripts/publish_english_github_release.command
```

서로 다른 저장소에 게시할 때는 저장소를 명시합니다.

```sh
GITHUB_REPOSITORY=owner/korean-repository ./scripts/publish_korean_github_release.command
GITHUB_REPOSITORY=owner/english-repository ./scripts/publish_english_github_release.command
```

이 게시 명령은 작업 트리에 커밋하지 않은 변경이 있거나 같은 버전의 Release가 이미
존재하면 중단합니다. 릴리스 본문은 `RELEASE_NOTES.ko.md`와 `RELEASE_NOTES.md`에서 각각
가져옵니다.

배포 전 [COMPLIANCE.md](COMPLIANCE.md)의 체크리스트를 확인합니다. 소스는 공용으로
유지해야 한글판과 영문판의 기능이 항상 동일하게 적용됩니다.
