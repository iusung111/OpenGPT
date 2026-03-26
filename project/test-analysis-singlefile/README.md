# Test Analysis Single File

단일 HTML 기반 시험 분석 앱입니다.

## 파일 구성
- `index.html` : 메인 앱
- `sample_experiment_data.csv` : 바로 import 가능한 샘플 데이터

## 사용 방법
1. 브라우저에서 `index.html`을 엽니다.
2. `샘플 데이터 로드`를 누르거나 `sample_experiment_data.csv`를 업로드합니다.
3. 컬럼 바인딩을 확인합니다.
4. `분석 실행`을 눌러 PASS/FAIL 판정을 수행합니다.
5. Plot, KPI, 상세 결과, Report Preview를 확인합니다.
6. `PDF / 인쇄`로 보고서를 저장합니다.

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
- CSV, XLSX, XLS 형식을 지원합니다.
- 매핑 템플릿은 브라우저 Local Storage에 저장됩니다.
- 단일 파일 프로토타입이므로 별도 서버 없이 열람 가능합니다.
