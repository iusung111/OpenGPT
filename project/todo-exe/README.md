# Todo EXE

`project/todo-exe`는 Windows용 단일 실행 Todo 프로그램 예제입니다.

## 포함 파일
- `main.go`: 소스 코드
- `build.bat`: Windows에서 exe 빌드
- `.github/workflows/build-todo-exe.yml`: GitHub Actions 빌드 워크플로우

## 로컬 빌드
Windows에 Go가 설치되어 있다면 아래처럼 빌드할 수 있습니다.

```bat
build.bat
```

빌드 결과:
- `todo.exe`

## 기능
- 할 일 추가
- 완료 전환
- 삭제
- 완료 항목 일괄 삭제
- JSON 파일 저장
