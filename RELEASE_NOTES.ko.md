# Batch Markdown Converter 0.1.0

한국어 macOS 앱의 첫 공개 버전입니다.

## 주요 기능

- 파일과 폴더를 드래그 앤 드롭하여 Markdown으로 일괄 변환
- 문제가 있는 파일 하나가 전체 작업을 멈추지 않도록 변환 프로세스 격리
- 원본 파일 옆 또는 선택한 폴더에 결과 저장
- 같은 파일명이 있을 때 자동 이름 변경, 건너뛰기 또는 덮어쓰기
- 일반 모드와 다크 모드 전환
- 변환 완료 후 Finder에서 결과 폴더 열기 옵션
- 달리는 강아지 진행률 표시

## 지원 환경

- macOS 13 Ventura 이상
- Apple Silicon(arm64)

## 설치

한국어판 DMG와 SHA-256 체크섬을 다운로드하고 체크섬을 확인한 다음, DMG를 열어
`Batch Markdown Converter Korean.app`을 Applications 폴더로 드래그합니다.

현재 빌드는 임시 서명되었으며 Apple 공증을 받지 않았습니다. 처음 실행할 때 macOS가
차단하면 공식 Release의 체크섬과 일치하는지 확인한 뒤 Finder에서 앱을 Control-클릭하고
**열기**를 선택하세요.

## 오픈소스 안내

이 프로젝트는 Microsoft의 공식 제품이 아닌 독립 프로젝트입니다. 같은 Release에는 앱과
함께 LGPL 적용을 받는 PySide6/Qt의 정확한 대응 소스 및 체크섬이 포함됩니다.
