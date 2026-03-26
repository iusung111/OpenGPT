# Test Analysis Single File

단일 HTML 기반 시험 분석 앱입니다.

## 권장 실행 파일
- `index-v2.html` : 권장 메인 앱
- `index.html` : 초기 버전
- `sample_experiment_data.csv` : 바로 import 가능한 샘플 데이터

## v2 주요 기능
- CSV / XLSX / XLS import
- 열 인덱스 또는 컬럼명 바인딩
- PASS / FAIL 판정
- line / scatter / histogram / box / control chart
- KPI / 결과 테이블 / 상세 판정 패널
- report preview / PDF 인쇄
- 컬럼 타입 추론 표시
- 결과 CSV 저장
- 보고서 HTML 저장
- 요약 텍스트 복사

## 사용 방법
1. 브라우저에서 `index-v2.html`을 엽니다.
2. `샘플 데이터`를 누르거나 `sample_experiment_data.csv`를 업로드합니다.
3. 컬럼 바인딩을 확인합니다.
4. `분석 실행`을 눌러 PASS/FAIL 판정을 수행합니다.
5. Plot, KPI, 상세 결과, Report Preview를 확인합니다.
6. 필요 시 결과 CSV 또는 보고서 HTML을 저장합니다.
7. `PDF / 인쇄`로 보고서를 출력합니다.

## 기본 판정 규칙
- `Lower Spec <= Test Value <= Upper Spec` 이면 `PASS`
- 그 외는 `FAIL`

## 기본 바인딩 필드
- Sample ID
- Lot No
- Timestamp
- Measurement X
- Measurement Y
- Lower Spec
- Upper Spec
- Test Value
- Operator
- Remark

## 참고
- 매핑 템플릿은 브라우저 Local Storage에 저장됩니다.
- 단일 파일 프로토타입이므로 별도 서버 없이 열람 가능합니다.
- `index-v2.html`은 기존 `index.html` 대비 export 및 타입 프로파일 기능이 추가된 버전입니다.
