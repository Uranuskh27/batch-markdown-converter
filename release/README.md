# Release artifacts

한글판과 영문판 배포 파일은 별도 디렉터리에 생성됩니다.

- `Korean/`: 한국어 UI용 DMG, 설치 안내, SHA-256 체크섬
- `English/`: 영어 UI용 DMG, installation guide, SHA-256 checksum
- `Source-Code/`: DMG와 같은 GitHub Release에 첨부할 Qt/PySide LGPL 대응 소스
- `GitHub-Upload-Korean/`: 한국어판 GitHub Release에 올릴 6개 파일
- `GitHub-Upload-English/`: 영문판 GitHub Release에 올릴 6개 파일

두 언어는 공용 소스 코드를 사용하며 `scripts/package_releases.command`가 각 배포
디렉터리를 자동으로 갱신합니다. DMG와 체크섬은 생성 산출물이므로 Git에서 제외됩니다.
`Source-Code`의 아카이브도 생성 산출물이며 공개 Release에는 반드시 함께 첨부합니다.
업로드 폴더 두 개는 각각 독립적으로 생성되며 선택한 언어 폴더의 파일을 모두 같은
GitHub Release에 올려야 합니다.
