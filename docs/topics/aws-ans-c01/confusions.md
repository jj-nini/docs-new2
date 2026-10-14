# 헷갈리는 개념

ANS-C01 기출에서 정답과 오답 선택지로 자주 맞붙는 개념 묶음이다. 그룹마다 **판별 규칙**은 지문에 나오는 신호(키워드·요구사항)에서 정답 쪽으로 가는 길을 적었다.

!!! note "읽는 법"
    - 판별 규칙의 근거는 기출에서 반복되는 선택지 구성이다. 기출 원문은 옮기지 않았다.
    - 셀프 체크 문항은 직접 만든 짧은 문항이다. 클릭하면 정답이 열린다.
    - 덤프 정답은 해설이 없고, 일부는 서비스가 업데이트되기 전 기준이다. 그런 곳은 따로 표시했다.

## 그룹 목록

| 그룹 | 한 줄 요약 |
|------|-----------|
| [게이트웨이 vs 인터페이스 엔드포인트 vs PrivateLink](#vpc-endpoint-type) | 온프레미스나 피어 VPC에서 접근하면 인터페이스, 같은 VPC에서 S3·DynamoDB를 무료로 쓰면 게이트웨이 |
| [VPC 피어링 vs Transit Gateway vs PrivateLink](#vpc-interconnect) | CIDR 중복이나 단방향 서비스 노출은 PrivateLink, 소수·대용량·최저 비용은 피어링, 다수·전이 라우팅은 TGW |
| [프라이빗 VIF vs 퍼블릭 VIF vs 트랜짓 VIF](#dx-vif-type) | 도달 대상이 VPC(VGW/DXGW)인지, AWS 퍼블릭 엔드포인트인지, TGW인지로 고른다 |
| [DX 게이트웨이 vs Transit Gateway](#dx-gateway-transit) | DXGW는 전이 라우터가 아니다. 리전 간 VPC 통신은 TGW 피어링, 광고 범위는 허용 프리픽스 |
| [Resolver 인바운드 vs 아웃바운드](#resolver-direction) | 질의가 들어오는 방향이 기준이다. 온프레미스→AWS는 인바운드, AWS→온프레미스는 아웃바운드+규칙 |
| [프라이빗 호스팅 영역 vs 퍼블릭 호스팅 영역](#dns-zone-scope) | PHZ는 연결된 VPC 안에서만 보인다. 외부 위임·도메인 이전은 퍼블릭 영역 |
| [ALB vs NLB vs GWLB](#load-balancer-type) | 경로·쿠키·XFF는 ALB, 고정 IP·TCP/UDP·패스스루·PrivateLink는 NLB, 어플라이언스 삽입은 GWLB |
| [CloudFront vs Global Accelerator vs Route 53 라우팅 정책](#global-traffic) | 캐싱·HTTP는 CloudFront, 고정 IP·비HTTP·빠른 장애 조치는 GA, DNS 기반 분산은 Route 53 |
| [MACsec vs DX 위 IPsec VPN vs 인터넷 VPN](#dx-encryption) | 고속 전용 연결 + 최고 처리량 암호화는 MACsec, 호스티드·저속 회선은 VIF 위 IPsec |
| [BGP 경로 제어: Local Pref 커뮤니티 vs AS_PATH vs 구체적 프리픽스](#bgp-traffic-steering) | 어느 방향의 트래픽을, 어느 VIF 종류에서 조절하는지로 도구가 정해진다 |
| [Network Firewall vs GWLB vs 어플라이언스 모드](#inspection-insertion) | AZ를 넘는 트래픽만 끊기면 어플라이언스 모드, 서드파티는 GWLB, 관리형 IPS는 Network Firewall |
| [TGW Connect vs VPN 어태치먼트 vs Direct Connect](#sdwan-hybrid) | SD-WAN + 고대역폭 + IPsec 불필요는 Connect(GRE), 저예산 백업·동적 라우팅은 VPN |
| [Reachability Analyzer vs Route Analyzer vs Flow Logs vs Traffic Mirroring](#path-analysis-tools) | 구성 검증, TGW 경로, 흐름 메타데이터, 패킷 페이로드로 갈린다 |
| [보안 그룹·NACL vs Network Firewall vs WAF·Shield](#filtering-layer) | 상태 저장 여부, 거부 가능 여부, 계층(L3/L4 vs L7)으로 고른다 |
| [NAT 게이트웨이 vs IPAM·프라이빗 NAT vs PrivateLink](#nat-ip-exhaustion) | 포트 고갈과 IP 고갈을 구분하고, 중복 CIDR은 프라이빗 NAT나 PrivateLink |

---

## 게이트웨이 vs 인터페이스 엔드포인트 vs PrivateLink {#vpc-endpoint-type}

!!! warning "헷갈리는 이유"
    셋 다 "VPC 엔드포인트"라고 부르고, S3는 게이트웨이형과 인터페이스형을 모두 지원한다. 게이트웨이형은 라우팅 테이블 항목이라 VPC 밖(온프레미스, 피어 VPC, TGW 너머)에서는 쓸 수 없다는 점이 핵심 함정이다.

| 기준 | [게이트웨이 엔드포인트](concepts.md#gateway-endpoint) | [인터페이스 엔드포인트](concepts.md#interface-endpoint) | [PrivateLink 엔드포인트 서비스](concepts.md#privatelink) |
|------|------|------|------|
| 대상 | S3, DynamoDB만 | 대부분의 AWS 서비스(S3 포함) | 내가(또는 파트너가) 만든 서비스 |
| 동작 방식 | 라우팅 테이블에 프리픽스 리스트 경로 추가 | 서브넷에 ENI + 프라이빗 IP | 제공자 NLB(또는 GWLB) ↔ 소비자 인터페이스 엔드포인트 |
| 비용 | 무료 | 시간당 + 처리 GB당 요금 | 소비자 쪽 인터페이스 엔드포인트 요금 |
| VPC 밖에서 접근 | 불가 | 가능(DX/VPN/TGW/피어링 경유) | 가능 |
| DNS | 퍼블릭 서비스 이름 그대로 | 프라이빗 DNS 또는 엔드포인트 전용 DNS 이름 | 엔드포인트 DNS 이름(필요하면 PHZ) |
| 보안 수단 | 엔드포인트 정책 | 엔드포인트 정책 + 보안 그룹 | 허용 주체(allow principals) + 연결 수락 |

**판별 규칙**

- "온프레미스(또는 다른 VPC)에서 S3에 사설 접근" → **인터페이스 엔드포인트**. 게이트웨이형 선택지는 오답이다.
- 온프레미스 앱이 퍼블릭 S3 이름을 그대로 써야 함 → 인터페이스 엔드포인트 + **Resolver 인바운드 엔드포인트**로 온프레미스 DNS가 질의를 전달. 엔드포인트만 만들고 DNS를 안 건드리는 선택지는 불완전하다.
- "같은 VPC의 EC2 → S3", "NAT 게이트웨이 비용 절감", "데이터 전송 비용 최소화" → **게이트웨이 엔드포인트**.
- 수백 개 VPC가 인터페이스 엔드포인트를 공유(중앙 공유 서비스 VPC) → 엔드포인트의 **프라이빗 DNS를 끄고** 서비스 이름으로 PHZ를 만들어 각 VPC에 연결한다.
- "자사 서비스를 다른 계정·고객 VPC에 노출" → **PrivateLink 엔드포인트 서비스**(앞단은 NLB).

??? question "셀프 체크 (클릭해서 정답 보기)"
    Q1. 온프레미스 서버가 DX 프라이빗 VIF를 통해 S3에 접근해야 한다. 인터넷을 거치면 안 된다. 무엇을 만드는가?
    → **S3 인터페이스 엔드포인트**. 게이트웨이 엔드포인트는 VPC 라우팅 테이블에만 존재하므로 VPC 밖에서 온 트래픽은 쓸 수 없다.

    Q2. 프라이빗 서브넷 EC2가 같은 리전 S3로 대량 업로드를 하고, NAT 게이트웨이 처리 요금이 크다. 가장 저렴한 해결책은?
    → **S3 게이트웨이 엔드포인트**. 무료이고 라우팅 테이블에 경로만 추가하면 된다.

---

## VPC 피어링 vs Transit Gateway vs PrivateLink {#vpc-interconnect}

!!! warning "헷갈리는 이유"
    셋 다 VPC 사이를 연결한다. 기출은 같은 요구를 세 방식으로 써 놓고 **CIDR 중복, 규모, 비용, 방향성** 중 하나로 정답을 가른다.

| 기준 | [VPC 피어링](concepts.md#vpc-peering) | [Transit Gateway](concepts.md#transit-gateway) | [PrivateLink](concepts.md#privatelink) |
|------|------|------|------|
| 토폴로지 | 1:1, 비전이적 | 허브-스포크, 전이 라우팅 | 소비자 → 서비스 단방향 |
| CIDR 중복 | 불가 | 불가(라우팅이 필요하므로) | **가능** |
| 데이터 처리 요금 | 없음(전송 요금만) | 어태치먼트 시간당 + GB당 처리 요금 | 엔드포인트 시간당 + GB당 처리 요금 |
| 규모 | 소수 VPC에 적합, 메시가 커지면 관리 부담 | 수백~수천 VPC, VPN/DX 공유 | 서비스 단위로 무한히 늘릴 수 있음 |
| 계정·리전 간 | 가능 | RAM 공유, 리전 간 TGW 피어링 | 허용 주체로 계정 간 공유 |
| 노출 범위 | 양쪽 VPC 전체(라우팅 테이블 범위) | 라우팅 테이블로 세그먼트 분리 | 특정 서비스 포트만 |

**판별 규칙**

- "CIDR이 겹친다", "고객이 내부 IP를 공유하지 않는다", "SaaS 제공" → **PrivateLink**(NLB + 엔드포인트 서비스). 피어링·TGW 선택지는 라우팅 충돌로 오답이다.
- "가장 안전하게", "세분화된 접근 제어", "공유 서비스를 소비" → PrivateLink. TGW 풀 메시는 노출이 너무 넓다.
- "몇 개 VPC + 월 수십 TB 전송 + 최저 비용" → **VPC 피어링**. TGW는 GB당 처리 요금이 붙는다.
- "VPC가 계속 늘어난다", "온프레미스 연결을 여러 VPC가 공유", "전이 라우팅" → **Transit Gateway**.
- "다른 회사(계정)의 TGW와 연결, 최소 변경" → **TGW 피어링 어태치먼트**(계정 간 가능). TGW 사이에 VPN을 새로 거는 선택지는 과하다.

??? question "셀프 체크 (클릭해서 정답 보기)"
    Q1. 인수한 회사의 VPC가 우리 VPC와 같은 10.0.0.0/16을 쓴다. 우리 쪽 앱이 저쪽 API 하나만 호출하면 된다. 재배포 없이 가장 간단한 방법은?
    → **PrivateLink**. 저쪽 API를 NLB 뒤 엔드포인트 서비스로 노출하고 우리 VPC에 인터페이스 엔드포인트를 만든다. CIDR이 겹쳐도 된다.

    Q2. 피어링으로 A–B, B–C를 연결했다. A에서 C로 갈 수 있는가?
    → **불가**. 피어링은 비전이적이다. A–C 피어링을 추가하거나 TGW로 바꿔야 한다.

---

## 프라이빗 VIF vs 퍼블릭 VIF vs 트랜짓 VIF {#dx-vif-type}

!!! warning "헷갈리는 이유"
    같은 DX 회선 위의 논리 인터페이스라 이름만 다른 것처럼 보인다. 실제로는 **도달 대상**이 완전히 다르고, 기출 선택지는 "S3 접근"에 프라이빗 VIF를, "다수 VPC"에 프라이빗 VIF를 섞어 넣는다.

| 기준 | [프라이빗 VIF](concepts.md#private-vif) | [퍼블릭 VIF](concepts.md#public-vif) | [트랜짓 VIF](concepts.md#transit-vif) |
|------|------|------|------|
| 도달 대상 | VPC 사설 IP(VGW 또는 DXGW→VGW) | AWS 퍼블릭 엔드포인트(S3, DynamoDB, VPN 엔드포인트 등) | DXGW → TGW → 다수 VPC |
| 연결 대상 객체 | VGW 또는 DX 게이트웨이 | 없음(AWS 퍼블릭 네트워크) | DX 게이트웨이(TGW 연결) |
| 필요한 IP/ASN | 사설 IP, 사설 ASN 가능 | 퍼블릭 IP·광고할 퍼블릭 프리픽스 | 사설 IP |
| 확장성 | VPC마다 VIF 또는 DXGW에 VGW 여러 개 연결 | - | TGW 하나로 수백 VPC |
| 암호화를 얹는 방법 | VGW 대상 VPN은 불가 | 퍼블릭 VPN 엔드포인트로 IPsec | 프라이빗 IP VPN(TGW) |

**판별 규칙**

- "S3 같은 퍼블릭 서비스에 DX로" → **퍼블릭 VIF**. 프라이빗 VIF로 S3에 가려면 인터페이스 엔드포인트가 따로 있어야 한다.
- "DX 전용 회선 + 암호화 + 인터넷 금지"(호스티드·1Gbps 회선) → **퍼블릭 VIF + Site-to-Site VPN**. "퍼블릭 인터넷 사용 금지 + 사설 IP 강조" 문구가 있으면 **트랜짓 VIF 위 프라이빗 IP VPN**이 정답이 되는 문항도 있다.
- "VIF 개수 한도에 다다른다", "VPC가 계속 늘어난다", "가장 확장성 있게" → **TGW + DXGW + 트랜짓 VIF**.
- "VPC 몇 개만, 가장 저렴하게" → **VGW + DXGW + 프라이빗 VIF**. TGW를 추가하면 처리 요금이 붙는다.
- "SiteLink로 데이터센터끼리 연결, 운영 효율" → **기존 프라이빗(또는 트랜짓) VIF에서 SiteLink 활성화**. 퍼블릭 VIF와 VPN은 SiteLink 대상이 아니다.

??? question "셀프 체크 (클릭해서 정답 보기)"
    Q1. 1Gbps 호스티드 연결로 온프레미스 → S3 업로드를 하는데, 모든 패킷을 암호화해야 한다. 어떤 VIF 위에 무엇을 얹는가?
    → **퍼블릭 VIF + IPsec VPN**. 호스티드 연결은 MACsec 대상이 아니고, S3는 퍼블릭 엔드포인트이므로 퍼블릭 VIF가 맞다.

    Q2. 한 리전 VPC 40개를 같은 DX로 온프레미스와 연결하고, 앞으로 계속 늘어난다. 어떤 VIF인가?
    → **트랜짓 VIF**(DXGW에 TGW 연결). VPC마다 프라이빗 VIF를 만드는 방식은 VIF 한도에 걸린다.

---

## DX 게이트웨이 vs Transit Gateway {#dx-gateway-transit}

!!! warning "헷갈리는 이유"
    둘 다 "게이트웨이"이고 여러 리전을 묶을 수 있어서, DXGW도 TGW처럼 트래픽을 전달한다고 오해한다. DXGW는 **VIF ↔ VGW/TGW를 이어 주는 글로벌 연결 객체**일 뿐, VPC 간·VIF 간 전이 라우팅을 하지 않는다.

| 기준 | [DX 게이트웨이](concepts.md#dx-gateway) | [Transit Gateway](concepts.md#transit-gateway) | [트랜짓 VIF](concepts.md#transit-vif) |
|------|------|------|------|
| 범위 | 글로벌(리전 무관) | 리전 단위, 리전 간은 피어링 | DX 회선 위 VLAN |
| 전이 라우팅 | 없음(VPC↔VPC, VIF↔VIF 불가, SiteLink는 별도 기능) | 있음(라우팅 테이블 기반) | - |
| 광고 범위 제어 | **허용 프리픽스(allowed prefixes)** | 라우팅 테이블 연결·전파 | - |
| 계정 간 | 연결 제안(association proposal) | RAM 공유 | - |
| 역할 | 온프레미스 쪽 경로를 여러 리전으로 퍼뜨림 | VPC·VPN·DX 사이의 라우터 | 둘을 잇는 DX 쪽 인터페이스 |

**판별 규칙**

- "DXGW를 통해 리전 A VPC와 리전 B VPC가 서로 통신" → **오답 신호**. 리전 간 VPC 통신은 **TGW 리전 간 피어링**(정적 경로)이다.
- "다른 리전 TGW의 VPC도 온프레미스에서 접근" → 두 가지 정답 패턴: ① 그 TGW를 **기존 DXGW에 연결 + 허용 프리픽스에 CIDR 추가**, ② **TGW 피어링 + 기존 DXGW 허용 프리픽스에 양쪽 CIDR 추가**.
- "다른 계정(인수한 회사)의 TGW를 우리 DX로 연결" → 그 계정에서 **우리 DXGW에 연결 제안**을 보내고 우리가 수락. 새 DXGW를 만드는 선택지는 기존 VIF와 이어지지 않는다.
- "경로가 광고되지 않는다", "연결은 됐는데 온프레미스에 CIDR이 안 보인다" → **허용 프리픽스 누락**부터 의심한다.
- "새 리전 VPC를 기존 TGW 환경에 붙이고 DX 변경은 최소화" → 새 리전에 TGW를 만들고 **기존 TGW와 피어링**. VGW + 트랜짓 VIF 같은 짝이 안 맞는 조합은 오답이다(트랜짓 VIF는 VGW에 붙지 않는다).

??? question "셀프 체크 (클릭해서 정답 보기)"
    Q1. DXGW 하나에 us-east-1 VGW와 eu-west-1 VGW를 연결했다. 두 VPC 사이 트래픽이 DXGW를 통해 흐르는가?
    → **흐르지 않는다**. DXGW는 VPC 간 전이 라우팅을 하지 않는다. TGW 피어링이나 VPC 피어링이 필요하다.

    Q2. TGW를 DXGW에 연결했는데 온프레미스 라우터에 새 VPC CIDR이 광고되지 않는다. 먼저 확인할 것은?
    → **DXGW–TGW 연결의 허용 프리픽스 목록**. TGW 연결에서는 이 목록에 있는 프리픽스만 온프레미스로 광고된다.

---

## Resolver 인바운드 vs 아웃바운드 {#resolver-direction}

!!! warning "헷갈리는 이유"
    "온프레미스와 DNS 연동"이라는 같은 맥락에서 방향만 뒤집혀 나온다. 기준은 **질의가 어디서 시작해 어디로 들어가는가**다. 엔드포인트 이름은 VPC 입장에서 붙였다.

| 기준 | [인바운드 엔드포인트](concepts.md#route53-resolver-inbound) | [아웃바운드 엔드포인트·전달 규칙](concepts.md#route53-resolver-outbound) |
|------|------|------|
| 질의 방향 | 온프레미스 → VPC(PHZ, 엔드포인트 DNS) | VPC → 온프레미스 DNS |
| 온프레미스 쪽 설정 | 조건부 전달자 → 인바운드 엔드포인트 IP | 없음(온프레미스 DNS가 질의를 받기만 함) |
| AWS 쪽 설정 | 엔드포인트(ENI)만 | 엔드포인트 + **전달 규칙(도메인 → 대상 IP)** + VPC 연결 |
| 다계정 확장 | 중앙 VPC 하나 | 규칙을 **RAM으로 공유**, 각 VPC에 연결 |

**판별 규칙**

- "VPC 워크로드가 온프레미스 도메인 이름을 해석" → **아웃바운드 + 전달 규칙만**. 인바운드까지 함께 만드는 선택지는 "최소 관리" 조건에서 오답이다.
- "사무실(온프레미스)에서 PHZ 이름으로 접근" → **인바운드 엔드포인트 + 온프레미스 조건부 전달자**. VPC의 .2 리졸버 IP로 직접 전달하는 선택지는 오답이다(VPC 밖에서 닿지 않는다).
- "양방향", "AWS와 온프레미스가 서로의 이름을 해석" → **둘 다**.
- "여러 계정 VPC가 같은 규칙 사용" → 중앙 계정 아웃바운드 엔드포인트 + **규칙 RAM 공유** + 각 VPC DHCP 옵션을 AmazonProvidedDNS로.
- EC2 기반 BIND 포워더를 늘리는 선택지 → "최소 관리", "가장 확장성 있게" 조건에서 오답.
- "모든 질의를 온프레미스 보안 DNS로, 단 AWS 서비스 도메인은 제외" → 아웃바운드 + "." 전달 규칙 + amazonaws.com **시스템 규칙**.

??? question "셀프 체크 (클릭해서 정답 보기)"
    Q1. 온프레미스 DNS 서버가 corp.aws.internal(PHZ) 질의를 AWS로 보내야 한다. 무엇을 만드는가?
    → **Resolver 인바운드 엔드포인트**. 온프레미스 DNS에 그 IP로 가는 조건부 전달자를 설정한다.

    Q2. 30개 계정의 VPC가 모두 onprem.example.com을 해석해야 한다. 엔드포인트를 계정마다 만들어야 하는가?
    → **아니다**. 중앙 VPC에 아웃바운드 엔드포인트와 전달 규칙을 만들고, 규칙을 RAM으로 공유해 각 VPC에 연결한다.

---

## 프라이빗 호스팅 영역 vs 퍼블릭 호스팅 영역 {#dns-zone-scope}

!!! warning "헷갈리는 이유"
    같은 Route 53 호스팅 영역이고 같은 도메인 이름을 쓸 수 있다(split-horizon). 기출은 "인터넷에 노출하지 않는다"와 "하위 도메인을 위임한다"를 섞어, 어느 영역을 만들어야 하는지 헷갈리게 한다.

| 기준 | [퍼블릭 호스팅 영역](concepts.md#route53-public-zone) | [프라이빗 호스팅 영역](concepts.md#route53-private-hosted-zone) | [Resolver 인바운드](concepts.md#route53-resolver-inbound) |
|------|------|------|------|
| 누가 해석하나 | 인터넷 전체 | **연결된 VPC 안**에서만 | 온프레미스가 PHZ를 해석하는 통로 |
| 위임 | 부모 영역에 NS 레코드 | 해당 없음(NS 위임 불가) | - |
| 다른 계정 | 하위 도메인 영역을 그 계정에 만들고 NS 위임 | 다른 계정 VPC와 연결(승인 후 연결) | - |
| 전제 조건 | 등록 기관 NS 설정 | VPC의 enableDnsSupport, enableDnsHostnames | 온프레미스 조건부 전달자 |
| 지표 | DNSQueries(CloudWatch, 퍼블릭 영역) | 쿼리 로깅 | InboundQueryVolume 등 |

**판별 규칙**

- "인터넷에 노출하지 않는다", "VPC 안 서비스만 사용", "내부 도메인" → **PHZ**를 만들고 VPC와 연결. 퍼블릭 영역을 VPC와 "연결"하는 선택지는 성립하지 않는다.
- "하위 도메인(staging.example.com) 관리를 다른 계정 개발자에게" → 그 계정에 **퍼블릭 영역 생성 + 부모 영역에 NS 레코드**. 방향이 반대인 NS 레코드나 PHZ 선택지는 오답이다.
- "DNS 제공자를 Route 53으로 옮기되 다운타임 없이" → **퍼블릭 영역에 레코드 복사 → 기존 등록 기관에서 NS만 변경**. 도메인 이전(transfer)과 PHZ 선택지는 오답이다.
- "온프레미스에서 PHZ 이름 해석" → PHZ만으로는 불가. **인바운드 엔드포인트**가 필요하다.
- PHZ가 있는데 이름이 안 풀린다 → VPC 연결 누락, DNS 속성 비활성화, 커스텀 DHCP 옵션 순으로 의심한다.

??? question "셀프 체크 (클릭해서 정답 보기)"
    Q1. 부모 계정에 example.com 퍼블릭 영역이 있다. dev 계정이 dev.example.com 레코드를 직접 관리하게 하려면?
    → dev 계정에 **dev.example.com 퍼블릭 영역**을 만들고, 부모 영역에 dev.example.com **NS 레코드**(값은 dev 영역의 네임서버)를 추가한다.

    Q2. app.internal PHZ를 VPC에 연결했는데 EC2에서 이름이 안 풀린다. VPC 설정에서 확인할 두 속성은?
    → **enableDnsSupport**와 **enableDnsHostnames**.

---

## ALB vs NLB vs GWLB {#load-balancer-type}

!!! warning "헷갈리는 이유"
    "로드 밸런서를 고르라"는 문항에서 세 가지가 모두 선택지에 나온다. 특히 **클라이언트 IP 보존 방법**(XFF, NLB 기본 보존, Proxy Protocol v2)이 선택지마다 섞여 단골 오답이 된다.

| 기준 | [ALB](concepts.md#alb) | [NLB](concepts.md#nlb) | [GWLB](concepts.md#gwlb) |
|------|------|------|------|
| 계층 | L7(HTTP/HTTPS/gRPC) | L4(TCP/UDP/TLS) | L3(GENEVE) |
| 라우팅 | 경로·호스트·헤더 기반 | 포트 기반 | 어플라이언스 플릿으로 투명 전달 |
| 클라이언트 IP | **X-Forwarded-For** 헤더 | 인스턴스 타깃은 기본 보존, 그 밖(온프레미스 IP 타깃 등)은 **Proxy Protocol v2** | 원본 패킷 그대로 |
| 고정 IP | 없음(GA나 NLB 앞단 필요) | AZ별 고정 IP / EIP | - |
| TLS | HTTPS 종료(오프로드) | TLS 종료 또는 **TCP 패스스루** | 해당 없음 |
| 세션 고정 | 쿠키 기반 스티키 | 소스 IP 기반 스티키 | 흐름 고정 |
| PrivateLink 앞단 | 직접은 불가(NLB 뒤에 ALB 타깃) | **가능** | GWLB 엔드포인트 |

**판별 규칙**

- "URL 경로별로 다른 서비스", "쿠키 세션", "HTTPS 오프로드 + 클라이언트 IP" → **ALB + XFF**.
- "온프레미스 서버를 타깃으로 + 클라이언트 IP를 끝까지" → **NLB + Proxy Protocol v2**. NLB에 XFF를 켠다는 선택지는 존재하지 않는 기능이다.
- "중간 복호화 금지", "애플리케이션 인증서로 종단 간 암호화" → **NLB TCP 443 리스너(패스스루)**. ALB HTTPS나 CloudFront는 중간에서 복호화한다.
- "DNS를 못 쓰는 장치", "고정 IP 허용 목록" → **NLB**(단일 리전) 또는 Global Accelerator(멀티 리전·지연 최소). 가장 저렴하면 NLB 단독.
- "다른 계정에서 사설로 접근", "PrivateLink" → **NLB**.
- "서드파티 방화벽 플릿을 로드 밸런서 뒤에", "투명 삽입" → **GWLB**.
- "Traffic Mirroring 대상의 확장성" → **NLB**(UDP 4789 VXLAN). ALB는 미러 대상이 될 수 없다.
- "서브넷 IP가 부족" → NLB(/28 서브넷) 쪽이 ALB보다 IP를 덜 쓴다. 두 AZ 배치는 기본이다.

!!! note "덤프 정답과 최신 기능"
    mTLS(상호 TLS) 문항의 덤프 정답은 NLB TCP 패스스루다. ALB도 2023년 말부터 mTLS를 지원한다 (확인 필요: 기출이 어느 시점 기준인지). 시험에서는 "백엔드가 직접 인증" 문구가 있으면 NLB 패스스루를 고른다.

??? question "셀프 체크 (클릭해서 정답 보기)"
    Q1. 백엔드가 온프레미스 서버(IP 타깃)이고 TCP 서비스다. 백엔드가 클라이언트 IP를 알아야 한다. 무엇을 켜는가?
    → **NLB의 Proxy Protocol v2**. VPC 밖 IP 타깃은 클라이언트 IP가 기본 보존되지 않는다.

    Q2. 웹 앱의 /api는 서비스 A로, /img는 서비스 B로 보내야 한다. 어떤 로드 밸런서인가?
    → **ALB**의 경로 기반 라우팅. NLB에는 경로 라우팅이 없다.

---

## CloudFront vs Global Accelerator vs Route 53 라우팅 정책 {#global-traffic}

!!! warning "헷갈리는 이유"
    셋 다 "전 세계 사용자 지연 감소"로 소개된다. 기출은 **프로토콜(HTTP인지), 고정 IP, 캐싱, 장애 조치 속도, 비용**으로 정답을 가른다.

| 기준 | [CloudFront](concepts.md#cloudfront) | [Global Accelerator](concepts.md#global-accelerator) | [Route 53 라우팅 정책](concepts.md#route53-routing-policy) |
|------|------|------|------|
| 계층 | HTTP/HTTPS(웹소켓 포함) | TCP/UDP | DNS |
| 캐싱 | 있음 | **없음** | 없음 |
| 진입 IP | 바뀌는 엣지 IP(도메인 이름) | **고정 애니캐스트 IP 2개** | 엔드포인트 IP를 응답 |
| 장애 조치 | 오리진 그룹 장애 조치 | 헬스 체크로 즉시 전환(DNS 캐시 영향 없음) | TTL·클라이언트 캐시에 따라 지연 |
| 리전별 비율 조절 | - | **트래픽 다이얼**, 엔드포인트 가중치 | 가중치 정책 |
| 추가 기능 | Lambda@Edge, 필드 레벨 암호화, WAF | 지터·첫 바이트 지연 감소(AWS 백본) | 헬스 체크, 지리 위치 |

**판별 규칙**

- "IoT/게임/MQTT/UDP", "비HTTP" → **Global Accelerator**. CloudFront는 HTTP 전용이다.
- "고객 방화벽에 고정 IP 허용", "장치 재설정 없이" → **Global Accelerator**(BYOIP 가능). NLB를 추가하는 선택지는 멀티 리전이 안 된다.
- "가장 높은 가용성 + 멀티 리전 + 빠른 장애 조치" → **Global Accelerator**. Route 53 지연 시간 정책은 DNS 캐시 때문에 느리다.
- "롤아웃 중 리전별 트래픽 비율 조절 + 지터 최소화" → GA **트래픽 다이얼**.
- "HTTPS 웹 콘텐츠 + 지연 감소 + 최저 비용" → **CloudFront**(ALB를 HTTPS 오리진으로).
- "원거리 리전으로 패킷 손실" → GA로 백본 경유하거나, 가까운 리전에 배포 + **Route 53 지연 시간 정책**. 둘 다 정답인 복수 선택 문항이 있다.

??? question "셀프 체크 (클릭해서 정답 보기)"
    Q1. 전 세계 UDP 게임 서버(3개 리전)에 플레이어가 고정 IP로 접속해야 하고, 리전 장애 시 수 초 안에 전환해야 한다.
    → **Global Accelerator**. 애니캐스트 고정 IP, UDP 지원, 헬스 체크 기반 즉시 전환.

    Q2. 정적 이미지가 많은 HTTPS 사이트의 해외 사용자 지연을 가장 싸게 줄이려면?
    → **CloudFront**. 엣지 캐싱으로 오리진 왕복 자체를 줄인다.

---

## MACsec vs DX 위 IPsec VPN vs 인터넷 VPN {#dx-encryption}

!!! warning "헷갈리는 이유"
    "DX + 암호화"라는 같은 요구에 답이 세 가지다. MACsec은 L2라서 **회선 종류·속도 조건**이 있고, IPsec은 어디서나 되지만 **터널당 대역폭**이 낮다. 기출은 "최고 처리량", "기존 대역폭 유지", "호스티드 연결" 문구로 갈라 놓는다.

| 기준 | [MACsec](concepts.md#macsec) | [DX 위 IPsec VPN](concepts.md#vpn-over-dx) | [Site-to-Site VPN(인터넷)](concepts.md#site-to-site-vpn) |
|------|------|------|------|
| 계층 | L2(이더넷 프레임) | L3(IPsec) | L3(IPsec) |
| 적용 구간 | 고객 라우터 ↔ DX 장비(홉 단위) | 고객 장비 ↔ AWS VPN 종단(종단 간) | 고객 장비 ↔ AWS VPN 종단 |
| 회선 조건 | **전용 연결**, MACsec 지원 포트, 10Gbps·100Gbps 등 고속 (확인 필요: 최신 지원 속도) | DX 회선 종류 무관(호스티드 가능) | 인터넷 |
| 처리량 | 회선 속도 그대로 | 터널당 약 1.25Gbps, TGW ECMP로 확장 | 터널당 약 1.25Gbps |
| 필요한 것 | CKN/CAK(Secrets Manager), 연결/LAG에 키 연결, 암호화 모드 | 퍼블릭 VIF(퍼블릭 VPN 엔드포인트) 또는 트랜짓 VIF(프라이빗 IP VPN) | 인터넷 |

**판별 규칙**

- "10Gbps 이상 전용 연결 + 암호화 + 최고 처리량", "기존 대역폭 유지" → **MACsec**. VPN 선택지는 터널 대역폭 때문에 오답이다.
- 기존 회선이 MACsec 미지원이면 → **MACsec 지원 신규 전용 연결**을 추가하고 트래픽 이전.
- "호스티드 연결", "1Gbps", "APN 파트너 회선" + 암호화 → **퍼블릭 VIF + IPsec VPN**(또는 트랜짓 VIF + 프라이빗 IP VPN).
- "네트워크 계층 암호화 + 전용 회선" → **DX 위 IPsec**. KMS로 트래픽을 암호화한다는 선택지는 의미가 없다.
- MACsec 구현 단계 복수 선택 → **키(CKN/CAK) 생성·저장 → 연결에 키 연결 → 암호화 모드 설정 → 고객 라우터 설정**.

??? question "셀프 체크 (클릭해서 정답 보기)"
    Q1. 2Gbps 호스티드 DX로 VPC와 통신하며 암호화가 필요하다. MACsec을 쓸 수 있는가?
    → **쓸 수 없다**. MACsec은 지원 포트의 전용 연결에서만 된다. IPsec VPN을 VIF 위에 얹는다.

    Q2. 100Gbps 전용 DX 회선에서 처리량을 거의 잃지 않고 암호화하려면?
    → **MACsec**. IPsec 터널은 터널당 약 1.25Gbps라 수십 개의 ECMP 터널이 필요하다.

---

## BGP 경로 제어: Local Pref 커뮤니티 vs AS_PATH vs 구체적 프리픽스 {#bgp-traffic-steering}

!!! warning "헷갈리는 이유"
    도구는 셋인데 **방향**(AWS→온프레미스인지, 온프레미스→AWS인지)과 **우선순위**(더 구체적인 프리픽스 > Local Preference > AS_PATH 길이)를 동시에 따져야 한다. 게다가 7224 커뮤니티는 DX 프라이빗·트랜짓 VIF 전용이라 TGW Connect나 퍼블릭 VIF에는 통하지 않는다.

| 기준 | [Local Pref 커뮤니티](concepts.md#bgp-path-selection)(7224:7100/7200/7300) | AS_PATH 프리펜드 | 더 구체적인 프리픽스 |
|------|------|------|------|
| 조절하는 방향 | AWS → 온프레미스 | AWS → 온프레미스 | AWS → 온프레미스 |
| 어디에 설정 | 온프레미스가 AWS로 광고하는 경로에 태그 | 온프레미스가 광고할 때 백업 쪽 경로에 붙임 | 주 링크로 더 작은 프리픽스 광고 |
| 우선순위 | 프리픽스 길이 다음 | Local Pref 다음 | **가장 강함** |
| 적용 범위 | [DX](concepts.md#direct-connect) 프라이빗·트랜짓 VIF | DX, [VPN](concepts.md#site-to-site-vpn), TGW Connect | 모두 |
| 값의 뜻 | 7300 높음(주) > 7200 > 7100 낮음(백업) | 길수록 덜 선호 | 길수록(더 구체적) 선호 |

온프레미스 → AWS 방향은 온프레미스 라우터 자체의 Local Preference(AWS에서 받은 경로에 설정)로 조절한다.

**판별 규칙**

- "AWS에서 온프레미스로 가는 트래픽은 주 데이터센터 우선" (DX 프라이빗·트랜짓 VIF) → 주 쪽 경로에 **7224:7300**, 백업 쪽에 **7224:7100**. 숫자를 반대로 쓴 선택지가 단골 오답이다.
- 7224:9100/9200/9300 → 퍼블릭 VIF의 **광고 범위** 커뮤니티다. 우선순위 조절용 선택지로 나오면 오답.
- "퍼블릭 VIF + active/passive" → 온프레미스→AWS는 **온프레미스 Local Pref**, AWS→온프레미스는 **한쪽에 더 구체적인 프리픽스**(또는 AS_PATH 프리펜드).
- "TGW Connect의 두 SD-WAN 어플라이언스 중 하나만 사용" → 보조 어플라이언스에서 **AS_PATH 프리펜드**. 7224 커뮤니티는 DX 전용이라 오답.
- "같은 프리픽스를 DX와 VPN이 모두 광고" → **DX 우선**. VPN을 주 경로로 쓰려면 VPN 쪽에 더 구체적인 프리픽스를 광고해야 한다.
- "VPC 라우팅이 이상하다 + 온프레미스가 수백 개 프리픽스 광고" → 프라이빗 VIF **프리픽스 100개 제한** 초과. 요약(summarize)이 정답.
- "VPN 두 터널이 비대칭으로 동작해 응답이 버려진다 + 대역폭 유지" → 고객 장비에서 **비대칭 라우팅 허용**. AS_PATH로 한 터널만 쓰게 하면 대역폭이 줄어든다.

??? question "셀프 체크 (클릭해서 정답 보기)"
    Q1. DX 회선 2개(프라이빗 VIF)로 같은 프리픽스를 광고한다. AWS가 회선 A를 주로 쓰게 하려면 A 쪽 경로에 어떤 커뮤니티를 붙이는가?
    → **7224:7300**(높은 Local Preference). B 쪽에는 7224:7100.

    Q2. 회선 A에는 10.0.0.0/16, 회선 B에는 10.0.1.0/24를 광고했고, A에 7224:7300을 붙였다. 10.0.1.5로 가는 AWS 트래픽은 어느 회선을 타는가?
    → **회선 B**. 더 구체적인 프리픽스가 Local Preference보다 먼저 적용된다.

---

## Network Firewall vs GWLB vs 어플라이언스 모드 {#inspection-insertion}

!!! warning "헷갈리는 이유"
    중앙 검사 VPC 설계 문항에 셋이 함께 나온다. 어플라이언스 모드는 방화벽 제품이 아니라 **TGW 어태치먼트 옵션**이고, 비대칭 라우팅 증상을 고치는 데만 쓴다.

| 기준 | [Network Firewall](concepts.md#network-firewall) | [GWLB](concepts.md#gwlb) | [TGW 어플라이언스 모드](concepts.md#tgw-appliance-mode) |
|------|------|------|------|
| 정체 | AWS 관리형 상태 저장/비저장 방화벽·IPS | 서드파티 어플라이언스 앞의 L3 로드 밸런서 | TGW VPC 어태치먼트 설정 |
| 해결하는 문제 | 관리형 IPS, 도메인 필터, 로깅 | 서드파티 방화벽 플릿의 확장·HA·투명 삽입 | AZ를 넘는 흐름이 다른 AZ 어플라이언스로 가서 끊기는 문제 |
| 어디에 켜나 | 방화벽 서브넷 + 라우팅 | GWLB 엔드포인트 + 라우팅 | **검사(공유) VPC의 어태치먼트**에만 |
| 배포 모델 | 중앙(TGW 검사 VPC) / 분산(VPC마다) | 중앙 / 분산 | 중앙 모델에서 필요 |
| 핵심 설정 | HOME_NET 변수, 엄격한 규칙 순서, 알림·흐름 로그 | GENEVE, 어플라이언스 NIC 구성 | - |

**판별 규칙**

- "AZ를 넘는 트래픽만 간헐적으로 끊긴다", "같은 AZ끼리는 정상" → **검사 VPC 어태치먼트에 어플라이언스 모드**. 애플리케이션 VPC 어태치먼트에 켜는 선택지는 오답이다.
- "서드파티(Marketplace) 방화벽", "기존 벤더 어플라이언스를 확장" → **GWLB**.
- "AWS 관리형 IPS", "최소 운영" → **Network Firewall**.
- "VPC 피어링 구조 + 재설계 없이 IPS" → **분산 모델 Network Firewall**. 중앙 모델은 TGW가 필요하다.
- "TGW로 중앙 검사" 복수 선택 → **라우팅 테이블 2개**(앱 VPC용: 기본 경로 → 검사 VPC / 검사 VPC용: 앱 VPC 경로 전파) + 검사 VPC에 방화벽 + **HOME_NET에 모든 VPC·온프레미스 CIDR**. 라우팅 테이블 1개 선택지는 오답.
- "검사 트래픽 전부와 조치를 로깅" → Network Firewall 자체 로깅(**알림 + 흐름 로그**). VPC Flow Logs로 대신하는 선택지는 오답.

??? question "셀프 체크 (클릭해서 정답 보기)"
    Q1. TGW 중앙 검사 VPC를 거치게 했더니 VPC A(AZ-a) ↔ VPC B(AZ-b) 트래픽만 끊긴다. 어디에 무엇을 켜는가?
    → **검사 VPC의 TGW 어태치먼트에 어플라이언스 모드**. 흐름의 양방향이 같은 AZ 어플라이언스를 거치게 된다.

    Q2. 이미 쓰는 서드파티 차세대 방화벽 이미지를 Auto Scaling 플릿으로 VPC 경로에 끼워 넣으려면?
    → **GWLB**(+ GWLB 엔드포인트를 경로 대상으로).

---

## TGW Connect vs VPN 어태치먼트 vs Direct Connect {#sdwan-hybrid}

!!! warning "헷갈리는 이유"
    SD-WAN 어플라이언스를 TGW에 붙이는 방법으로 Connect와 VPN이 모두 가능해 보인다. Connect는 **IPsec 없이 GRE**를 쓰고 기존 VPC나 DX 어태치먼트를 전송로로 삼는다. VPN은 터널당 대역폭이 낮다.

| 기준 | [TGW Connect](concepts.md#tgw-connect) | [VPN 어태치먼트](concepts.md#site-to-site-vpn) | [Direct Connect](concepts.md#direct-connect) |
|------|------|------|------|
| 터널 | GRE + BGP | IPsec + BGP(또는 정적) | 물리 회선 + VLAN + BGP |
| 암호화 | 없음(전송로에 의존) | 있음 | 없음(MACsec/IPsec 별도) |
| 대역폭 | Connect 피어당 최대 약 5Gbps (확인 필요) | 터널당 약 1.25Gbps, ECMP로 확장 | 회선 속도 |
| 전제 | 전송용 VPC 어태치먼트 또는 DX 어태치먼트, **TGW CIDR 블록**(GRE 주소용) | 인터넷 또는 DX 위 | 회선 프로비저닝(수주) |
| 비용·속도 | 중간 | 가장 저렴·즉시 | 비싸고 느림 |

**판별 규칙**

- "SD-WAN 어플라이언스가 VPC에 있고 TGW와 고대역폭(수 Gbps)" → **TGW Connect**. VPN 어태치먼트 2개 선택지는 대역폭이 모자란다.
- Connect 구성 단계 → **TGW에 CIDR 블록 할당 → VPC 어태치먼트(전송로) → Connect 어태치먼트 → Connect 피어(GRE + BGP)**. VXLAN을 쓰는 선택지는 오답.
- "기존 트랜짓 VPC(어플라이언스)의 확장성·라우팅 테이블 한계 해결, 최소 운영" → **TGW + Connect 어태치먼트**. 피어링으로 묶는 선택지는 오답.
- "지점 서브넷이 바뀔 때마다 정적 경로 수정이 귀찮다" → **동적(BGP) VPN 어태치먼트 + 전파**.
- "DX에 복원력을 더하되 예산이 제한적" → **Site-to-Site VPN을 백업**으로. 회선 추가는 비싸다.

??? question "셀프 체크 (클릭해서 정답 보기)"
    Q1. TGW Connect 어태치먼트를 만들려면 무엇이 먼저 있어야 하는가?
    → **전송로가 될 VPC 어태치먼트(또는 DX 어태치먼트)**. Connect는 그 위에 GRE 터널을 올린다.

    Q2. SD-WAN 허브를 TGW에 붙이는데 암호화가 필수다. Connect가 답인가?
    → **아니다**. Connect의 GRE 자체는 암호화하지 않는다. 암호화가 필수면 VPN 어태치먼트(또는 전송로 쪽 암호화)를 검토한다.

---

## Reachability Analyzer vs Route Analyzer vs Flow Logs vs Traffic Mirroring {#path-analysis-tools}

!!! warning "헷갈리는 이유"
    모두 "연결 문제를 조사한다"로 묶인다. 기출은 **구성을 보는가, 실제 트래픽을 보는가**, 그리고 **TGW·리전 간인가, VPC 내부인가**, **페이로드까지 필요한가**로 정답을 가른다.

| 기준 | [Reachability Analyzer](concepts.md#reachability-analyzer) | [Route Analyzer](concepts.md#tgw-network-manager) | [VPC Flow Logs](concepts.md#vpc-flow-logs) | [Traffic Mirroring](concepts.md#traffic-mirroring) |
|------|------|------|------|------|
| 보는 것 | 구성(SG, NACL, 라우팅)으로 계산한 경로 | TGW 라우팅 테이블 경로 | 실제 흐름 메타데이터 | 실제 패킷(페이로드 포함) |
| 패킷 전송 | 없음 | 없음 | 관찰만 | 복제 |
| 범위 | VPC 리소스 간(소스·목적지 지정) | TGW, **리전 간 피어링 포함** | ENI·서브넷·VPC | ENI |
| 자동화 | 경로 저장 → 변경 이벤트 시 재분석 | Network Manager 이벤트 → EventBridge | CloudWatch Logs Insights / S3 + Athena | NLB·GWLB 엔드포인트 대상 |
| 대표 질문 | "SG 변경 후에도 연결되나" | "TGW 경로가 빠졌나" | "누가 트래픽을 만드나" | "UDP 내용이 무엇인가" |

**판별 규칙**

- "보안 그룹·NACL·라우팅 변경 때마다 연결을 자동 검증" → **Reachability Analyzer 경로 + EventBridge로 재분석**. 소스는 실제 진입점(예: 인터넷 게이트웨이)으로 지정한다. 보안 그룹을 소스로 쓰는 선택지는 오답.
- "리전 간 TGW 경로 누락", "TGW 라우팅 테이블 오류를 최소 운영으로" → **Route Analyzer**. Reachability Analyzer로 TGW 테이블을 분석한다는 선택지는 오답.
- "DX로 새 경로가 광고될 때마다 알림" → **Network Manager → CloudWatch Logs(Insights) / EventBridge**.
- "어떤 리소스가 트래픽을 만드나", "NAT 게이트웨이 사용량 급증 원인" → **Flow Logs**(CloudWatch Logs Insights 또는 S3 + Athena). NAT 게이트웨이 "액세스 로그"는 존재하지 않는다.
- "vpc-id, tcp-flags 같은 추가 필드 + 1년 보관 + 최저 비용" → **사용자 지정 필드 Flow Logs → S3**.
- "패킷 내용", "UDP 페이로드", "IDS/딥 패킷 분석" → **Traffic Mirroring**(필터로 범위 축소).

??? question "셀프 체크 (클릭해서 정답 보기)"
    Q1. 두 리전의 EC2가 TGW 피어링을 통해 통신하지 못한다. TGW 라우팅 테이블부터 보려면 어떤 도구인가?
    → **Network Manager Route Analyzer**. 리전 간 TGW 경로를 분석한다. VPC 라우팅 테이블은 따로 확인한다.

    Q2. 앱이 보내는 데이터의 실제 내용을 별도 계정의 분석 도구로 보내야 한다. Flow Logs로 되는가?
    → **안 된다**. Flow Logs에는 페이로드가 없다. **Traffic Mirroring**을 쓴다.

---

## 보안 그룹·NACL vs Network Firewall vs WAF·Shield {#filtering-layer}

!!! warning "헷갈리는 이유"
    모두 "트래픽을 막는다". **상태 저장 여부**(응답 트래픽 자동 허용인지), **거부 규칙 유무**, **계층**(L3/L4인지 L7인지)이 다르고, 원인 진단형 문항에서 어느 쪽 규칙을 고쳐야 하는지가 헷갈린다.

| 기준 | [보안 그룹](concepts.md#security-group-nacl) | [NACL](concepts.md#security-group-nacl) | [Network Firewall](concepts.md#network-firewall) | [WAF·Shield·Firewall Manager](concepts.md#perimeter-protection) |
|------|------|------|------|------|
| 상태 | 상태 저장 | **상태 비저장** | 상태 저장/비저장 둘 다 | L7(WAF) / DDoS(Shield) |
| 적용 단위 | ENI | 서브넷 | VPC 경로상 방화벽 엔드포인트 | CloudFront, ALB, API Gateway 등 |
| 거부 규칙 | 없음(허용만) | 있음 | 있음 | 있음 |
| 참조 | SG, **프리픽스 리스트** | CIDR만 | 도메인, Suricata 규칙 | IP 집합, 헤더, 속도 제한 |
| 함정 | 응답은 자동 허용 | **임시 포트(1024-65535) 반환 규칙** 필요 | HOME_NET 범위 | Shield Advanced의 비용 보호 |

**판별 규칙**

- "NACL 인바운드 80은 허용, 아웃바운드는 없음, 응답이 안 온다" → **NACL 아웃바운드에 1024-65535**. 보안 그룹 아웃바운드를 고치는 선택지는 오답(SG는 상태 저장).
- Flow Logs에 인바운드 ACCEPT, 아웃바운드 REJECT → **NACL 아웃바운드**가 원인. 둘 다 ACCEPT인데 안 되면 다른 곳을 본다.
- "ALB는 CloudFront에서 온 트래픽만, 네트워크 계층에서, 가장 운영 효율적" → **ALB 보안 그룹에 CloudFront 관리형 프리픽스 리스트**. NACL은 프리픽스 리스트를 참조하지 못한다. 커스텀 헤더 + WAF는 애플리케이션 계층 방식이다.
- "IPS", "도메인 기반 아웃바운드 필터" → **Network Firewall**. SG/NACL로는 패킷 내용을 못 본다.
- "DDoS + 확장 비용 보호" → **Shield Advanced**. "웹 요청의 보안 위협" → **WAF**.
- "조직 전체 계정에 정책 강제" → **Firewall Manager**(AWS Config 필요).
- 특정 포트 연결 실패 진단에서 NACL, SG, 기업 방화벽이 함께 나오면 → 상태 저장(SG)은 인바운드만, 상태 비저장(NACL)은 양방향을 확인한다.

??? question "셀프 체크 (클릭해서 정답 보기)"
    Q1. 서브넷 NACL이 인바운드 TCP 443 허용, 아웃바운드 규칙 없음이다. 보안 그룹은 인바운드 443 허용이다. 무엇을 추가하는가?
    → **NACL 아웃바운드 TCP 1024-65535**. NACL은 상태 비저장이라 응답 트래픽도 규칙이 필요하다.

    Q2. 보안 그룹으로 특정 악성 IP 하나를 "거부"할 수 있는가?
    → **없다**. 보안 그룹은 허용 규칙만 있다. NACL 거부 규칙이나 WAF IP 집합을 쓴다.

---

## NAT 게이트웨이 vs IPAM·프라이빗 NAT vs PrivateLink {#nat-ip-exhaustion}

!!! warning "헷갈리는 이유"
    "고갈"이라는 말이 두 가지로 나온다. NAT 게이트웨이의 **포트 고갈**(같은 목적지로 동시 연결이 너무 많음)과 VPC의 **IP 주소 고갈·CIDR 중복**이다. 해법이 완전히 다르다.

| 기준 | [NAT 게이트웨이](concepts.md#nat-gateway) 문제 | [IP 주소 관리](concepts.md#ip-address-management)(보조 CIDR·프라이빗 NAT·IPAM) | [PrivateLink](concepts.md#privatelink) |
|------|------|------|------|
| 증상 | 연결 실패 + **ErrorPortAllocation** 증가 / 약 6분 유휴 후 끊김 + **IdleTimeoutCount** | 서브넷 IP 부족, 상대가 허용한 IP 대역이 좁음, CIDR 중복 | CIDR이 겹치는 상대 서비스에 접근 |
| 원인 | 목적지별 포트 한도 / 350초 유휴 시간 초과 | 주소 계획 | 라우팅으로는 중복 해결 불가 |
| 해법 | NAT 게이트웨이 추가 + 서브넷 분산 / **TCP keepalive** | 보조 CIDR + **프라이빗 NAT 게이트웨이**(AZ마다), IPAM 풀·알림 | 엔드포인트 서비스 + 인터페이스 엔드포인트 |

**판별 규칙**

- "연결이 약 6분 무활동 후 끊긴다" → **IdleTimeoutCount 확인 + TCP keepalive**. HTTP/HTTPS 타임아웃이나 UDP keepalive 선택지는 오답.
- "ErrorPortAllocation 증가" → **NAT 게이트웨이를 늘리고 인스턴스를 여러 서브넷으로 분산** + TCP keepalive로 연결 재사용. "EIP 추가" 선택지는 덤프 정답에서 오답으로 처리되어 있다(현재는 NAT 게이트웨이에 보조 IP를 붙일 수 있다 (확인 필요)).
- "상대가 허용한 좁은 IP 대역으로만 접근, 고가용성" → 그 대역을 **보조 CIDR**로 추가하고 **AZ마다 프라이빗 NAT 게이트웨이**. 한 서브넷·한 NAT 선택지는 HA 조건 위반이고, 퍼블릭 NAT는 사설 경로에 맞지 않는다.
- "앱이 스케일 아웃해도 상대 허용 목록을 바꾸지 않게" → **프라이빗 NAT 게이트웨이**로 소스 IP 고정.
- "IP 사용률을 미리 알림받고 싶다, 최소 운영" → **VPC IPAM 풀 + 알림**. Lambda로 직접 세는 선택지는 운영 부담이 크다.
- "고객과 CIDR 중복 + 서비스 하나만 노출" → **PrivateLink**. 피어링 + NAT 조합은 오답.

??? question "셀프 체크 (클릭해서 정답 보기)"
    Q1. 프라이빗 서브넷 EC2 수백 대가 같은 외부 API로 연결하다가 실패하고, NAT 게이트웨이 ErrorPortAllocation이 오른다. IP 고갈인가?
    → **아니다. 포트 고갈이다.** NAT 게이트웨이를 늘려 서브넷별로 나누고, 연결을 재사용하도록 keepalive를 쓴다.

    Q2. 파트너 데이터센터가 10.1.0.0/24에서 오는 트래픽만 허용한다. 우리 VPC는 10.0.0.0/16이다. 무엇을 하는가?
    → VPC에 **10.1.0.0/24 보조 CIDR**을 붙이고 AZ마다 그 대역의 서브넷에 **프라이빗 NAT 게이트웨이**를 둔 뒤, 파트너행 트래픽을 그쪽으로 보낸다.
