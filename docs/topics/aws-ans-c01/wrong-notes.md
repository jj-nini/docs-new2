# 오답노트

> 마지막 분석: 2026-10-14 · 누적 2회차(14응답) · 오답 2문항 중 정리 2 · 불안정 6문항

현재 오답은 2문항뿐이다. 그래서 이 노트는 **애매하게 맞힌 문항**과 **한 번 틀렸다가 맞힌 문항**도 함께 다룬다.

## 요약

| 심각도 | 패턴 | 관련 개념 | 문항 수 | 처방 |
|--------|------|----------|--------|------|
| 🔴 핵심 결손 | Resolver 엔드포인트 방향 혼동 (확신 오답 + 반복 오답) | [인바운드](concepts.md#route53-resolver-inbound) · [아웃바운드](concepts.md#route53-resolver-outbound) | 1 | [인바운드 vs 아웃바운드](confusions.md#resolver-direction) 표를 보고 "질의 출발지 → 도착지" 화살표를 직접 그린다 → 같은 개념 신규 문항 3개 |
| 🔴 핵심 결손 | 인라인 검사 도구와 보안 그룹 능력 오인 (확신 오답 + 같은 오답 2회) | [GWLB](concepts.md#gwlb) · [보안 그룹·NACL](concepts.md#security-group-nacl) | 1 | [보안 그룹·NACL](concepts.md#security-group-nacl) 규칙 표 다시 읽기 → [Network Firewall vs GWLB](confusions.md#inspection-insertion) 셀프 체크 → gwlb 문항 3개 |
| 🟡 부분 약점 | DX 양방향 경로 제어에서 커뮤니티와 Local Pref 방향 뒤집힘 | [BGP 경로 제어](concepts.md#bgp-path-selection) · [Direct Connect](concepts.md#direct-connect) | 1 | [BGP 경로 제어 비교](confusions.md#bgp-traffic-steering)에서 방향별로 "누가 누구에게 설정하나"를 표로 정리 → 문항 2개 |
| 🟡 부분 약점 | L7 요구에 L4 로드 밸런서 선택 | [ALB](concepts.md#alb) · [NLB](concepts.md#nlb) | 1 | [ALB vs NLB vs GWLB](confusions.md#load-balancer-type)에서 "클라이언트 IP 확보 방식" 행만 소리 내어 설명 |
| 🟡 불안정 | 맞혔지만 확신 없음 (VGW/TGW, NAT, 라우팅 정책, MTU) | 아래 [불안정한 문항](#unstable) 참고 | 4 | 내일 복습 때 확신도를 "확실"로 올릴 수 있는지 근거를 말로 먼저 적고 답한다 |

!!! note "채점 방식 주의"
    복수 선택 문항은 전부 맞혀야 정답이다. 그래서 MACsec과 경계 보호(Shield) 개념은 정답률 0%로 집계되지만, 두 번 모두 **해당 선택지는 맞게 골랐다**. 실제 구멍은 같은 문항의 GWLB 쪽이다.

## 개념 결손 체인

- [Route 53 Resolver 엔드포인트 방향](confusions.md#resolver-direction) → q003
    - 뿌리: "규칙(rule)은 아웃바운드 엔드포인트로 **나가는** 질의에만 쓴다"는 점을 모른다. 들어오는 질의도 규칙으로 처리하려 한다.
- [보안 그룹은 허용만 가능](concepts.md#security-group-nacl) → q009
    - 뿌리: 차단 수단을 보안 그룹으로 착각해 인라인 검사([GWLB](concepts.md#gwlb)) 자리를 밀어냈다.
- [BGP 경로 제어 방향](confusions.md#bgp-traffic-steering) → q010, (q005는 맞힘)
    - 뿌리: "커뮤니티는 AWS→온프레미스, Local Pref는 온프레미스→AWS"라는 방향 구분이 아직 자동으로 나오지 않는다.

## 문항별 노트

### q003 · 하이브리드 DNS를 Resolver 엔드포인트로 교체 {#q003}

- **상황 요지**: 온프레미스와 VPC가 서로의 도메인을 조회하는 양방향 DNS 전달을 자체 DNS 서버 대신 Resolver 엔드포인트로 바꾼다.
- **내 답 → 정답**: 1회차 C·D·E, 2회차 B·C·D → **B·C·E** · 확신도: 확실 → 애매 · 오답 유형: 🔴 개념 결손
- **왜 틀렸나**: 두 번 모두 D(인바운드 엔드포인트를 대상으로 하는 Resolver 규칙)를 골랐다. 1회차는 B(온프레미스 전달기를 인바운드로) 대신, 2회차는 E(온프레미스 도메인 전달 규칙) 대신 골랐다. 정답 하나를 고치면 다른 하나가 빠지는 것은 방향 개념 자체가 서 있지 않다는 신호다.
- **올바른 판단 근거**:
    - 온프레미스 → AWS: 설정은 **온프레미스 DNS 쪽**에서 한다. 조건부 전달기를 인바운드 엔드포인트 IP로 향하게 한다.
    - AWS → 온프레미스: 아웃바운드 엔드포인트 + **전달 규칙**(온프레미스 도메인 → 온프레미스 DNS IP).
    - VPC의 프라이빗 호스팅 영역 도메인은 Resolver가 직접 답하므로 규칙이 필요 없다.
- **기억할 한 줄**: Resolver 규칙은 언제나 아웃바운드용이다. 인바운드 엔드포인트를 가리키는 규칙은 없다.
- **관련**: [인바운드](concepts.md#route53-resolver-inbound) · [아웃바운드·전달 규칙](concepts.md#route53-resolver-outbound) · [헷갈리는 개념](confusions.md#resolver-direction)
- **기록**: ✗ 10-14 · ✗ 10-14 · 다음 복습 10-15

### q009 · 의료 워크로드의 암호화·검사·DDoS 비용 보호 {#q009}

- **상황 요지**: 온프레미스 구간 전송 암호화, 클라우드를 떠나기 전 모든 트래픽 검사, 공개 구성 요소의 DDoS 방어와 확장 비용 보호를 함께 만족해야 한다.
- **내 답 → 정답**: 두 회차 모두 C·D·F → **D·E·F** · 확신도: 확실 → 애매 · 오답 유형: 🔴 개념 결손 (같은 오답 반복 → 함정 신호 겹침)
- **왜 틀렸나**: E(GWLB로 서드파티 방화벽 인라인 삽입) 대신 C(Lambda로 보안 그룹에 거부 규칙 생성)를 두 번 골랐다. 보안 그룹은 **거부 규칙이 없다**. 또 "허용 전에 검사"라는 요구는 차단 목록이 아니라 인라인 검사 장비를 요구한다.
- **올바른 판단 근거**:
    - 요구사항 3개를 선택지 3개에 하나씩 짝짓는다: 암호화 → MACsec DX, 검사 → GWLB, DDoS 비용 → Shield Advanced.
    - "검사(inspect)" + "떠나기 전" → 트래픽 경로 안에 끼는 장비(GWLB, Network Firewall). 미러링이나 보안 그룹은 아니다.
- **기억할 한 줄**: 보안 그룹은 허용만, IP 차단은 NACL, 인라인 검사는 GWLB다.
- **관련**: [GWLB](concepts.md#gwlb) · [보안 그룹·NACL](concepts.md#security-group-nacl) · [MACsec](concepts.md#macsec) · [WAF·Shield](concepts.md#perimeter-protection) · [헷갈리는 개념: 검사 삽입](confusions.md#inspection-insertion) · [필터링 계층](confusions.md#filtering-layer)
- **기록**: ✗ 10-14 · ✗ 10-14 · 다음 복습 10-15

## 불안정한 문항 {#unstable}

맞혔지만 오답처럼 다룬다. 한 번 틀렸다가 바로 다시 맞힌 문항은 해설을 본 직후라 실력으로 치지 않는다.

| 문항 | 요지 | 기록 | 불안 원인 | 확인할 곳 |
|------|------|------|----------|----------|
| q001 | 경로 기반 라우팅 + HTTPS + 클라이언트 IP | ✗ 10-14 (확실) · ✓ 10-14 · 다음 복습 10-15 | 1회차에 B(XFF 헤더) 대신 A(NLB)를 확신하고 골랐다. "원본 IP 필요 → NLB"라는 연상이 경로 라우팅 조건을 덮었다. | [ALB](concepts.md#alb) · [ALB vs NLB vs GWLB](confusions.md#load-balancer-type) |
| q010 | DX 두 회선 중 하나를 보조로 만드는 BGP 설정 | ✗ 10-14 (찍음) · ✓ 10-14 (애매) · 다음 복습 10-15 | 1회차에 커뮤니티와 Local Pref를 모두 반대로 골랐다. 7300이 높음, Local Pref는 높을수록 선호. | [BGP 경로 제어](concepts.md#bgp-path-selection) · [BGP 비교](confusions.md#bgp-traffic-steering) |
| q002 | NAT 게이트웨이 경유 시 특정 공급자만 연결이 멈춤 | ✓ 10-14 (애매) · 다음 복습 10-15 | 정답 A(NAT GW의 단편화 미지원)를 골랐지만 MTU 오답들과 확실히 구분하지 못했다. "퍼블릭 서브넷에서는 정상"이 결정적 단서다. | [NAT 게이트웨이](concepts.md#nat-gateway) · [MTU](concepts.md#enhanced-networking) |
| q004 | 두 리전 VPC 연결 + 온프레미스 IPv6 VPN | ✓ 10-14 (애매) · 다음 복습 10-15 | VGW VPN은 IPv4 전용, TGW는 리전 리소스라는 두 근거가 확실하지 않았다. | [Transit Gateway](concepts.md#transit-gateway) · [Site-to-Site VPN](concepts.md#site-to-site-vpn) · [연결 방식 비교](confusions.md#vpc-interconnect) |
| q006 | 승인된 IP 대역으로만 온프레미스 접근, IGW 없음, 고가용성 | ✓ 10-14 (애매, 오래 고민) · 다음 복습 10-15 | 프라이빗 NAT와 AZ별 배치를 맞혔지만 판단에 시간이 오래 걸렸다. | [NAT 게이트웨이](concepts.md#nat-gateway) · [프라이빗 NAT 비교](confusions.md#nat-ip-exhaustion) |
| q007 | 가장 빠른 리전으로 보내고 장애 시 다음 리전으로 | ✓ 10-14 (애매) · 다음 복습 10-15 | 지연 시간 정책과 지리 위치 정책, alias + Evaluate Target Health의 역할이 흔들렸다. | [라우팅 정책](concepts.md#route53-routing-policy) · [글로벌 트래픽 비교](confusions.md#global-traffic) |

## 졸업한 문항

아직 없다. 연속 3회 맞히고 마지막이 "확실"이면 이곳으로 옮긴다.
